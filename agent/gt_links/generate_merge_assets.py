#!/usr/bin/env python3
'''Generate Links merge L2/L3 assets from cleaned merge source markdown.'''

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from agent.gt_links.links_gt_manifest import WCAG_244, WCAG_412
from agent.gt_links.run_task import build_task_prompt, load_task


GT_LINKS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_LINKS_DIR.parent.parent
SOURCE_ROOT = GT_LINKS_DIR / 'source_md_clean' / 'merge-instances'
DEFAULT_OUTPUT_ROOT = GT_LINKS_DIR / 'generated_clean_pilot' / 'generated_merge'


class MergeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def _str_presenter(dumper: yaml.Dumper, data: str) -> yaml.nodes.ScalarNode:
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    if len(data) > 88:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


MergeDumper.add_representer(str, _str_presenter)


WCAG_METADATA = {
    'link_function': {
        'assessment_requirement': 'L.1 Link Function',
        'wcag_target': 'WCAG 4.1.2 Name, Role, Value',
        'wcag_source_url': 'https://www.w3.org/TR/WCAG21/#name-role-value',
        'wcag_clause_text': WCAG_412,
        'wcag': {
            'number': '4.1.2',
            'name': 'Name, Role, Value',
            'link_name': 'Name, Role, Value',
            'url': 'https://www.w3.org/TR/WCAG21/#name-role-value',
            'criterion_text': WCAG_412,
        },
    },
    'link_purpose': {
        'assessment_requirement': 'L.2 Link Purpose',
        'wcag_target': 'WCAG 2.4.4 Link Purpose (In Context)',
        'wcag_source_url': 'https://www.w3.org/TR/WCAG21/#link-purpose-in-context',
        'wcag_clause_text': WCAG_244,
        'wcag': {
            'number': '2.4.4',
            'name': 'Link Purpose (In Context)',
            'link_name': 'Link Purpose (In Context)',
            'url': 'https://www.w3.org/TR/WCAG21/#link-purpose-in-context',
            'criterion_text': WCAG_244,
        },
    },
}


L2_EVIDENCE_RULE = {
    'link_function': (
        'that anchor performs an in-place control or command instead of taking '
        'the user to link content, a page location, or a resource.'
    ),
    'link_purpose': (
        'that anchor purpose cannot be determined from its accessible name alone '
        'or from its accessible name together with programmatically determined link context.'
    ),
}


def multi_output_format(family: str | None = None) -> dict[str, Any]:
    issue_type = family if family else 'link_function | link_purpose'
    return {
        'verdict': 'issue_found | no_issue_found',
        'issues': [
            {
                'selector': 'verified CSS selector for the reported anchor, or empty string',
                'target': 'natural-language target description',
                'issue_type': issue_type,
                'observed_behavior': 'concise description of the observed link behavior or accessible-name/context problem',
                'evidence': 'concrete DOM, AX, or interaction facts supporting the issue',
            }
        ],
    }


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.dump(
        data,
        Dumper=MergeDumper,
        allow_unicode=False,
        default_flow_style=False,
        sort_keys=False,
        width=88,
    )


def extract_first_yaml_block(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    match = re.search(r'```yaml\s*\n(.*?)\n```', text, flags=re.S)
    if not match:
        raise ValueError(f'No fenced yaml block found: {path}')
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f'YAML block must be a mapping: {path}')
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


def output_dirs(output_root: Path) -> dict[str, Path]:
    return {
        'tasks': output_root / 'tasks',
        'rules': output_root / 'evaluate-rules',
        'prompts': output_root / 'prompts',
    }


def clean_output_dirs(output_root: Path) -> None:
    resolved_output = output_root.resolve()
    if resolved_output == resolved_output.anchor or resolved_output == PROJECT_ROOT.resolve():
        raise RuntimeError(f'Refusing to clean unsafe output root: {output_root}')
    for directory in output_dirs(output_root).values():
        directory.mkdir(parents=True, exist_ok=True)
        resolved_dir = directory.resolve()
        if resolved_output not in resolved_dir.parents:
            raise RuntimeError(f'Refusing to clean directory outside output root: {directory}')
        for path in directory.glob('*'):
            resolved_path = path.resolve()
            if resolved_dir not in resolved_path.parents:
                raise RuntimeError(f'Refusing to remove outside output directory: {path}')
            if path.is_file():
                path.unlink()


def rule_file_for_task(task_id: str, output_root: Path) -> str:
    path = output_root / 'evaluate-rules' / f'{task_id}.yaml'
    try:
        display_path = path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        display_path = path.resolve()
    return str(display_path).replace('\\', '/')


def family_from_issue(issue: dict[str, Any]) -> str:
    family = require(issue, 'criterion.issue_family')
    if family not in WCAG_METADATA:
        issue_id = require(issue, 'issue_id')
        raise ValueError(f'Unsupported issue_family {family}: {issue_id}')
    return str(family)


def enriched_criterion(issue: dict[str, Any]) -> dict[str, Any]:
    family = family_from_issue(issue)
    meta = WCAG_METADATA[family]
    wcag_target = require(issue, 'criterion.wcag_target')
    if wcag_target != meta['wcag_target']:
        issue_id = require(issue, 'issue_id')
        raise ValueError(f'wcag_target mismatch for {issue_id}: {wcag_target}')
    return {
        'issue_family': family,
        'wcag_target': wcag_target,
        'assessment_requirement': meta['assessment_requirement'],
        'wcag': meta['wcag'],
    }


def inventory_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        'issue_id': require(issue, 'issue_id'),
        'target': {
            'selector': require(issue, 'target.selector'),
            'description': require(issue, 'target.description'),
            'coverage_policy': require(issue, 'target.coverage_policy'),
        },
        'criterion': enriched_criterion(issue),
        'evidence_rule': require(issue, 'evidence_rule'),
    }


def validate_merge_instance(instance: dict[str, Any], expected_level: str) -> None:
    iid = require(instance, 'instance_id')
    if require(instance, 'task_level') != expected_level:
        raise ValueError(f'task_level mismatch for {iid}')
    if require(instance, 'issue_present') is not True:
        raise ValueError(f'Merge instances currently require issue_present: true: {iid}')
    issues = require(instance, 'gold.issues')
    if not isinstance(issues, list) or not issues:
        raise ValueError(f'gold.issues must be a non-empty list: {iid}')
    ids = [require(issue, 'issue_id') for issue in issues]
    if len(ids) != len(set(ids)):
        raise ValueError(f'Duplicate issue_id in merge instance: {iid}')
    for field in [
        'source.record_file',
        'source.page_id',
        'page.site',
        'page.page_name',
        'page.start_url',
        'page.auth_state_file',
        'gold.expected_verdict',
    ]:
        require(instance, field)
    if expected_level == 'level2':
        family = require(instance, 'scope.issue_family')
        if family not in WCAG_METADATA:
            raise ValueError(f'Unsupported L2 issue_family for {iid}: {family}')
        if require(instance, 'scope.wcag_target') != WCAG_METADATA[family]['wcag_target']:
            raise ValueError(f'L2 wcag_target mismatch for {iid}')
        for issue in issues:
            if family_from_issue(issue) != family:
                issue_id = require(issue, 'issue_id')
                raise ValueError(f'L2 issue family mismatch for {iid}: {issue_id}')
    else:
        require(instance, 'scope.assessment_scope')


def load_merge_instances(level: str, source_root: Path = SOURCE_ROOT) -> list[dict[str, Any]]:
    source_dir = source_root / level
    paths = sorted(source_dir.glob('*.md'))
    if not paths:
        raise ValueError(f'No merge source markdown files found: {source_dir}')
    instances = [extract_first_yaml_block(path) for path in paths]
    ids = [require(instance, 'instance_id') for instance in instances]
    if len(ids) != len(set(ids)):
        raise ValueError(f'Duplicate merge instance_id under {source_dir}')
    for instance in instances:
        validate_merge_instance(instance, level)
    return instances


def build_l2_task(instance: dict[str, Any], output_root: Path) -> dict[str, Any]:
    iid = require(instance, 'instance_id')
    family = require(instance, 'scope.issue_family')
    meta = WCAG_METADATA[family]
    page_name = require(instance, 'page.page_name')
    task_id = f'{iid}.verify.level2.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_2_clause_given_location_hidden',
        'issue_domain': 'links',
        'issue_family': family,
        'wcag_target': meta['wcag_target'],
        'wcag_source_url': meta['wcag_source_url'],
        'wcag_clause_text': meta['wcag_clause_text'],
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': require(instance, 'page.auth_state_file'),
        'target_description': f'any anchor on the {page_name} page',
        'setup': None,
        'output_format': multi_output_format(family),
    }


def wcag_criteria_for_issues(issues: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    criteria: dict[str, dict[str, str]] = {}
    for issue in issues:
        family = family_from_issue(issue)
        meta = WCAG_METADATA[family]
        label = meta['assessment_requirement']
        criteria[label] = {
            'target': meta['wcag_target'],
            'text': meta['wcag_clause_text'],
            'url': meta['wcag_source_url'],
        }
    return {key: criteria[key] for key in sorted(criteria)}


def build_l3_task(instance: dict[str, Any], output_root: Path) -> dict[str, Any]:
    iid = require(instance, 'instance_id')
    page_name = require(instance, 'page.page_name')
    task_id = f'{iid}.verify.level3.v1'
    issues = require(instance, 'gold.issues')
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_3_links_assessment_scope',
        'issue_domain': 'links',
        'issue_family': 'links_assessment_l1_to_l2',
        'wcag_target': 'Links assessment L.1-L.2',
        'wcag_clause_text': 'Links assessment scope covers L.1 Link Function and L.2 Link Purpose.',
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': require(instance, 'page.auth_state_file'),
        'target_description': f'link-role elements within Links assessment scope L.1-L.2 on the {page_name} page',
        'setup': None,
        'wcag_criteria': wcag_criteria_for_issues(issues),
        'output_format': multi_output_format(),
    }


def page_record(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        'site': require(instance, 'page.site'),
        'page_name': require(instance, 'page.page_name'),
        'start_url': require(instance, 'page.start_url'),
    }


def source_record(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        'record_file': require(instance, 'source.record_file'),
        'page_id': require(instance, 'source.page_id'),
        'review_status': require(instance, 'source.review_status'),
    }


def scope_record(instance: dict[str, Any], level: str) -> dict[str, Any]:
    if level == 'level2':
        return {
            'issue_family': require(instance, 'scope.issue_family'),
            'wcag_target': require(instance, 'scope.wcag_target'),
            'assessment_requirement': require(instance, 'scope.assessment_requirement'),
        }
    return {'assessment_scope': require(instance, 'scope.assessment_scope')}


def build_rule(task: dict[str, Any], instance: dict[str, Any], level: str) -> dict[str, Any]:
    return {
        'task_id': task['task_id'],
        'instance_id': require(instance, 'instance_id'),
        'task_level': 'level2' if level == 'level2' else 'level3',
        'source': source_record(instance),
        'page': page_record(instance),
        'scope': scope_record(instance, level),
        'gold': {
            'issue_present': require(instance, 'issue_present'),
            'expected_verdict': require(instance, 'gold.expected_verdict'),
            'issues': [inventory_issue(issue) for issue in require(instance, 'gold.issues')],
        },
    }


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(data), encoding='utf-8')


def write_task_rule_prompt(
    task: dict[str, Any],
    rule: dict[str, Any],
    output_root: Path,
) -> list[Path]:
    dirs = output_dirs(output_root)
    task_id = task['task_id']
    task_path = dirs['tasks'] / f'{task_id}.yaml'
    rule_path = dirs['rules'] / f'{task_id}.yaml'
    prompt_path = dirs['prompts'] / f'{task_id}.task.prompt.txt'
    write_yaml(task_path, task)
    write_yaml(rule_path, rule)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(build_task_prompt(load_task(task_path)) + '\n', encoding='utf-8')
    return [task_path, rule_path, prompt_path]


def generate_all_merge_assets(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    source_root: Path = SOURCE_ROOT,
) -> list[Path]:
    clean_output_dirs(output_root)
    written: list[Path] = []

    for instance in sorted(load_merge_instances('level2', source_root), key=lambda item: require(item, 'instance_id')):
        task = build_l2_task(instance, output_root)
        rule = build_rule(task, instance, 'level2')
        written.extend(write_task_rule_prompt(task, rule, output_root))

    for instance in sorted(load_merge_instances('level3', source_root), key=lambda item: require(item, 'instance_id')):
        task = build_l3_task(instance, output_root)
        rule = build_rule(task, instance, 'level3')
        written.extend(write_task_rule_prompt(task, rule, output_root))

    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate Links merge L2/L3 assets.')
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    written = generate_all_merge_assets(output_root=args.output_root, source_root=args.source_root)
    print(f'wrote {len(written)} files under {args.output_root}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
