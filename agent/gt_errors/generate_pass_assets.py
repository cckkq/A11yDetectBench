from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


GT_ERRORS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_ERRORS_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.gt_errors.generate_clean_assets import WCAG_META
from agent.gt_errors.run_task import (
    SELECTOR_FIELD_DESCRIPTION,
    TARGET_FIELD_DESCRIPTION,
    build_task_prompt,
    load_task,
)

DEFAULT_SOURCE_ROOT = GT_ERRORS_DIR / 'source_md_clean' / 'pass-instances'
DEFAULT_OUTPUT_ROOT = GT_ERRORS_DIR / 'generated_clean_pilot' / 'generated_pass'
SUPPORTED_FAMILIES = {'error_identification', 'error_suggestion', 'error_prevention', 'status_messages'}


class PassDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def _str_presenter(dumper: yaml.Dumper, data: str) -> yaml.nodes.ScalarNode:
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    if len(data) > 88:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


PassDumper.add_representer(str, _str_presenter)


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.dump(data, Dumper=PassDumper, allow_unicode=False, default_flow_style=False, sort_keys=False, width=88)


def parse_source_md(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    match = re.search(r'```yaml\n(.*?)\n```', text, re.S)
    if not match:
        raise ValueError(f'Missing YAML block: {path}')
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f'Source YAML root must be a mapping: {path}')
    return data


def require(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            ident = data.get('instance_id', '<unknown>')
            raise ValueError(f'Missing required field {dotted}: {ident}')
        cur = cur[part]
    if cur is None or cur == '':
        ident = data.get('instance_id', '<unknown>')
        raise ValueError(f'Empty required field {dotted}: {ident}')
    return cur


def optional(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def source_instances(source_root: Path) -> list[dict[str, Any]]:
    paths = sorted(source_root.glob('*.md'))
    if not paths:
        raise ValueError(f'No ERROR PASS source markdown files found: {source_root}')
    items = [parse_source_md(path) for path in paths]
    ids = [require(item, 'instance_id') for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate instance_id in error pass source md')
    return items


def wcag_meta(instance: dict[str, Any]) -> dict[str, str]:
    target = require(instance, 'criterion.wcag_target')
    meta = WCAG_META.get(str(target))
    if meta is None:
        raise ValueError(f'Unsupported wcag_target {target}: {require(instance, "instance_id")}')
    return meta


def issue_family(instance: dict[str, Any]) -> str:
    family = str(require(instance, 'criterion.issue_family'))
    if family not in SUPPORTED_FAMILIES:
        raise ValueError(f'Unsupported issue_family {family}: {require(instance, "instance_id")}')
    return family


def output_dirs(output_root: Path) -> dict[str, Path]:
    return {
        'tasks': output_root / 'tasks',
        'rules': output_root / 'evaluate-rules',
        'prompts': output_root / 'prompts',
    }


def clean_output_dirs(output_root: Path) -> None:
    resolved_output = output_root.resolve()
    if resolved_output == Path(resolved_output.anchor) or resolved_output == PROJECT_ROOT.resolve():
        raise RuntimeError(f'Refusing to clean unsafe output root: {output_root}')
    for directory in output_dirs(output_root).values():
        if directory.exists():
            resolved_dir = directory.resolve()
            if resolved_output not in resolved_dir.parents and resolved_dir != resolved_output:
                raise RuntimeError(f'Refusing to clean outside output root: {directory}')
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)


def display_path(path: Path) -> str:
    try:
        shown = path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        shown = path.resolve()
    return str(shown).replace('\\', '/')


def rule_file_for_task(task_id: str, output_root: Path) -> str:
    name = f'{task_id}.yaml'.replace('.verify.v1.yaml', '.verify.shared.v1.yaml')
    return display_path(output_root / 'evaluate-rules' / name)


def single_output_format(family: str) -> dict[str, str]:
    return {
        'verdict': 'issue_found | no_issue_found',
        'selector': SELECTOR_FIELD_DESCRIPTION,
        'target': TARGET_FIELD_DESCRIPTION,
        'issue_type': family,
        'observed_behavior': 'concise description of the observed error behavior',
        'evidence': 'concrete DOM, interaction, text, or accessibility facts supporting the verdict',
    }


def validate_pass(instance: dict[str, Any]) -> None:
    if require(instance, 'issue_present') is not False:
        raise ValueError(f'PASS requires issue_present false: {require(instance, "instance_id")}')
    if require(instance, 'gold.expected_verdict') != 'no_issue_found':
        raise ValueError(f'PASS requires no_issue_found: {require(instance, "instance_id")}')
    require(instance, 'source.matched_positive')
    require(instance, 'probe')


def build_l1_task(instance: dict[str, Any], output_root: Path) -> dict[str, Any]:
    validate_pass(instance)
    iid = str(require(instance, 'instance_id'))
    family = issue_family(instance)
    meta = wcag_meta(instance)
    task_id = f'{iid}.verify.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_1_direct_verification',
        'issue_domain': 'error',
        'issue_family': family,
        'wcag_target': require(instance, 'criterion.wcag_target'),
        'wcag_source_url': meta['url'],
        'wcag_clause_text': meta['criterion_text'],
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': require(instance, 'target.description'),
        'probe': require(instance, 'probe'),
        'setup': None,
        'output_format': single_output_format(family),
        'target_selector': require(instance, 'target.selector'),
    }


def build_l1_rule(task: dict[str, Any], instance: dict[str, Any]) -> dict[str, Any]:
    validate_pass(instance)
    family = issue_family(instance)
    meta = wcag_meta(instance)
    return {
        'task_id': task['task_id'],
        'instance_id': require(instance, 'instance_id'),
        'task_level': 'level1',
        'source': require(instance, 'source'),
        'page': {
            'site': require(instance, 'page.site'),
            'page_name': require(instance, 'page.page_name'),
            'start_url': require(instance, 'page.start_url'),
        },
        'gold': {
            'issue_present': False,
            'expected_verdict': 'no_issue_found',
            'issue_type': [require(instance, 'criterion.wcag_target'), require(instance, 'template_id')],
            'target': require(instance, 'target'),
            'criterion': {
                'issue_family': family,
                'wcag_target': require(instance, 'criterion.wcag_target'),
                'assessment_requirement': meta['assessment_requirement'],
                'wcag': {
                    'number': meta['number'],
                    'name': meta['name'],
                    'link_name': meta['link_name'],
                    'url': meta['url'],
                    'criterion_text': meta['criterion_text'],
                },
            },
            'evidence_rule': require(instance, 'gold.evidence_rule'),
        },
        'evaluation_logic': [
            'Verdict must be exactly no_issue_found for the matched PASS target.',
            'Target may use a different locator, but it must resolve to the same DOM or accessibility target as the gold selector.',
            'A reported issue on this clean target is a false alarm for this task.',
            'Reporting unrelated issues does not count for this task.',
        ],
    }


def write_assets(instance: dict[str, Any], output_root: Path) -> list[Path]:
    dirs = output_dirs(output_root)
    task = build_l1_task(instance, output_root)
    rule = build_l1_rule(task, instance)
    task_id = task['task_id']
    task_path = dirs['tasks'] / f'{task_id}.yaml'
    rule_path = dirs['rules'] / Path(task['evaluate_rule_file']).name
    prompt_path = dirs['prompts'] / f'{task_id}.task.prompt.txt'
    task_path.write_text(dump_yaml(task), encoding='utf-8')
    rule_path.write_text(dump_yaml(rule), encoding='utf-8')
    prompt_path.write_text(build_task_prompt(load_task(task_path)) + '\n', encoding='utf-8')
    return [task_path, rule_path, prompt_path]


def generate_all_pass_assets(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> list[Path]:
    clean_output_dirs(output_root)
    written: list[Path] = []
    for instance in source_instances(source_root):
        written.extend(write_assets(instance, output_root))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate ERROR PASS-L1 clean-pilot assets.')
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    written = generate_all_pass_assets(source_root=args.source_root, output_root=args.output_root)
    print(f'Wrote {len(written)} files under {args.output_root}')


if __name__ == '__main__':
    main()
