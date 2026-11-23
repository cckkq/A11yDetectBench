from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SKIP_DIRS = {'_logs', 'launcher_logs', '__pycache__'}
REQUIRED_RUN_ARTIFACTS = ('task.snapshot.yaml', 'evaluate-rule.snapshot.yaml', 'final-response.json')


@dataclass
class EvaluationFinding:
    file: str
    task_id: str
    instance_id: str
    task_level: str
    expected_verdict: str
    observed_verdict: str
    overall_pass: bool | None
    hard_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    page: dict[str, Any] = field(default_factory=dict)
    gold_resolution_errors: list[dict[str, Any]] = field(default_factory=list)
    gold_selector_errors: list[dict[str, Any]] = field(default_factory=list)
    agent_selector_errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DomainAudit:
    domain: str
    roots: list[str]
    evals: int = 0
    missing_roots: list[dict[str, str]] = field(default_factory=list)
    parse_errors: list[dict[str, str]] = field(default_factory=list)
    hard_failures: list[EvaluationFinding] = field(default_factory=list)
    warnings: list[EvaluationFinding] = field(default_factory=list)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_string(value: Any) -> str:
    return '' if value is None else str(value)


def is_login_like_url(url: Any) -> bool:
    return bool(re.search(r'/auth/login/?|/customer/account/login/?|/login(\?|/|$)|/signin(\?|/|$)', as_string(url), re.I))


def looks_like_auth_failure(page: dict[str, Any]) -> bool:
    start_url = page.get('start_url')
    final_url = page.get('final_url')
    try:
        status = int(page.get('http_status'))
    except Exception:
        status = 0
    return (is_login_like_url(final_url) and not is_login_like_url(start_url)) or status >= 400


def has_run_artifacts(path: Path) -> bool:
    return all((path / name).exists() for name in REQUIRED_RUN_ARTIFACTS)


def iter_evaluation_files(root: Path):
    if not root.exists():
        yield {'missing_root': str(root), 'error': 'path does not exist'}
        return
    for path in root.rglob('evaluation.json'):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        if any(part.startswith('tmp_') for part in path.parts):
            continue
        yield {'file': path}


def iter_run_dirs_missing_evaluation(root: Path):
    if not root.exists():
        return
    seen: set[Path] = set()
    for task_snapshot in root.rglob('task.snapshot.yaml'):
        run_dir = task_snapshot.parent
        if run_dir in seen:
            continue
        seen.add(run_dir)
        parts = set(run_dir.parts)
        if parts & SKIP_DIRS:
            continue
        if any(part.startswith('tmp_') for part in run_dir.parts):
            continue
        if has_run_artifacts(run_dir) and not (run_dir / 'evaluation.json').exists():
            yield run_dir


def missing_evaluation_finding(run_dir: Path) -> EvaluationFinding:
    return EvaluationFinding(
        file=str(run_dir / 'evaluation.json'),
        task_id=run_dir.parent.name,
        instance_id='',
        task_level='',
        expected_verdict='',
        observed_verdict='',
        overall_pass=None,
        hard_failures=['missing_evaluation_json'],
    )


def classify_evaluation(file: Path, parsed: dict[str, Any]) -> EvaluationFinding:
    page = parsed.get('page') if isinstance(parsed.get('page'), dict) else {}
    gold_resolution_errors = as_list(parsed.get('gold_resolution_errors'))
    selector_errors = as_list(parsed.get('selector_errors'))
    gold_selector_errors = [err for err in selector_errors if isinstance(err, dict) and as_string(err.get('side')) == 'gold']
    agent_selector_errors = [err for err in selector_errors if isinstance(err, dict) and as_string(err.get('side')) == 'agent']
    expected_verdict = as_string(parsed.get('expected_verdict'))

    hard_failures: list[str] = []
    missing_artifacts = [name for name in REQUIRED_RUN_ARTIFACTS if not (file.parent / name).exists()]
    if missing_artifacts:
        hard_failures.append('missing_run_artifacts:' + ','.join(missing_artifacts))
    missing_core = [key for key in ('task_id', 'instance_id', 'expected_verdict') if not parsed.get(key)]
    if missing_core:
        hard_failures.append('missing_core:' + ','.join(missing_core))
    if parsed.get('evaluator_error'):
        hard_failures.append('evaluator_error')
    if gold_resolution_errors:
        hard_failures.append('gold_resolution')
    if gold_selector_errors:
        hard_failures.append('gold_selector_error')
    if expected_verdict == 'issue_found' and isinstance(parsed.get('gold_selectors'), list) and not parsed.get('gold_selectors'):
        hard_failures.append('expected_issue_without_gold_selectors')
    auth_suspect = looks_like_auth_failure(page)
    if auth_suspect and expected_verdict == 'issue_found':
        hard_failures.append('auth_or_http_for_issue_task')

    warnings: list[str] = []
    if agent_selector_errors:
        warnings.append('agent_selector_error')
    if auth_suspect and expected_verdict != 'issue_found':
        warnings.append('auth_or_http_on_non_issue_task')

    return EvaluationFinding(
        file=str(file),
        task_id=as_string(parsed.get('task_id') or file.parent.name),
        instance_id=as_string(parsed.get('instance_id')),
        task_level=as_string(parsed.get('task_level')),
        expected_verdict=expected_verdict,
        observed_verdict=as_string(parsed.get('observed_verdict')),
        overall_pass=parsed.get('overall_pass') if isinstance(parsed.get('overall_pass'), bool) else None,
        hard_failures=hard_failures,
        warnings=warnings,
        page=page,
        gold_resolution_errors=[err for err in gold_resolution_errors if isinstance(err, dict)],
        gold_selector_errors=gold_selector_errors,
        agent_selector_errors=agent_selector_errors,
    )


def audit_roots(domain: str, roots: list[Path]) -> DomainAudit:
    result = DomainAudit(domain=domain, roots=[str(root) for root in roots])
    for root in roots:
        for entry in iter_evaluation_files(root):
            if 'missing_root' in entry:
                result.missing_roots.append({'root': entry['missing_root'], 'error': entry['error']})
                continue
            file = entry['file']
            result.evals += 1
            try:
                parsed = json.loads(file.read_text(encoding='utf-8'))
            except Exception as exc:
                result.parse_errors.append({'file': str(file), 'error': str(exc)})
                continue
            if not isinstance(parsed, dict):
                result.parse_errors.append({'file': str(file), 'error': 'evaluation JSON root is not an object'})
                continue
            finding = classify_evaluation(file, parsed)
            if finding.hard_failures:
                result.hard_failures.append(finding)
            if finding.warnings:
                result.warnings.append(finding)
        for run_dir in iter_run_dirs_missing_evaluation(root):
            result.hard_failures.append(missing_evaluation_finding(run_dir))
    return result


def parse_domain_specs(values: list[str]) -> list[tuple[str, list[Path]]]:
    specs: list[tuple[str, list[Path]]] = []
    for value in values:
        name, sep, raw_roots = value.partition('=')
        if not sep or not name.strip() or not raw_roots.strip():
            raise ValueError(f'Invalid --domain spec: {value}')
        specs.append((name.strip(), [Path(chunk) for chunk in raw_roots.split(';') if chunk]))
    return specs


def print_text(results: list[DomainAudit]) -> None:
    for result in results:
        print(f'\n## {result.domain}')
        print(
            f'evals={result.evals} hard_failures={len(result.hard_failures)} '
            f'warnings={len(result.warnings)} parse_errors={len(result.parse_errors)} missing_roots={len(result.missing_roots)}'
        )
        for row in result.hard_failures:
            print(f'FAIL {row.task_id} [{",".join(row.hard_failures)}]')
            if row.gold_resolution_errors:
                print('  gold: ' + ' || '.join(as_string(err.get('reason')) for err in row.gold_resolution_errors))
            print(f'  file: {row.file}')
        for row in result.warnings:
            print(f'WARN {row.task_id} [{",".join(row.warnings)}]')
            print(f'  file: {row.file}')


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Audit official GT evaluation.json artifacts only.')
    parser.add_argument('--domain', action='append', required=True, help='Domain root spec, e.g. ERROR=C:\\runs\\error or LINKS=C:\\a;C:\\b')
    parser.add_argument('--json', action='store_true', help='Print machine-readable JSON.')
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results = [audit_roots(domain, roots) for domain, roots in parse_domain_specs(args.domain)]
    if args.json:
        print(json.dumps([asdict(result) for result in results], ensure_ascii=True, indent=2))
    else:
        print_text(results)
    failed = any(result.missing_roots or result.parse_errors or result.hard_failures for result in results)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
