#!/usr/bin/env python3
"""Generate ERROR merge L2/L3 assets from cleaned merge source markdown."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from agent.gt_errors.generate_clean_assets import WCAG_META
from agent.gt_errors.run_task import (
    SELECTOR_FIELD_DESCRIPTION,
    TARGET_FIELD_DESCRIPTION,
    build_task_prompt,
    load_task,
)


GT_ERRORS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_ERRORS_DIR.parent.parent
SOURCE_ROOT = GT_ERRORS_DIR / 'source_md_clean' / 'merge-instances'
DEFAULT_OUTPUT_ROOT = GT_ERRORS_DIR / 'generated_clean_pilot' / 'generated_merge'

SUPPORTED_FAMILIES = {'error_identification', 'error_suggestion', 'error_prevention', 'status_messages'}
SUPPORTED_LEVELS = {'level2', 'level3'}


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


def optional(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def output_dirs(output_root: Path) -> dict[str, Path]:
    return {
        'tasks': output_root / 'tasks',
        'rules': output_root / 'evaluate-rules',
        'prompts': output_root / 'prompts',
    }


def clean_output_dirs(output_root: Path) -> None:
    resolved_output = output_root.resolve()
    project_root = PROJECT_ROOT.resolve()
    if resolved_output == Path(resolved_output.anchor) or resolved_output == project_root:
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
    return display_path(output_root / 'evaluate-rules' / f'{task_id}.yaml')


def wcag_meta_for_target(wcag_target: str) -> dict[str, str]:
    meta = WCAG_META.get(wcag_target)
    if meta is None:
        raise ValueError(f'Unsupported wcag_target: {wcag_target}')
    return meta


def wcag_meta_for_family(family: str) -> tuple[str, dict[str, str]]:
    for wcag_target, meta in WCAG_META.items():
        if family == 'error_identification' and meta['assessment_requirement'] == 'E.1 Error Identification':
            return wcag_target, meta
        if family == 'error_suggestion' and meta['assessment_requirement'] == 'E.2 Error Suggestion':
            return wcag_target, meta
        if family == 'error_prevention' and meta['assessment_requirement'] == 'E.3 Error Prevention':
            return wcag_target, meta
        if family == 'status_messages' and meta['assessment_requirement'] == 'E.4 Status Messages':
            return wcag_target, meta
    raise ValueError(f'Unsupported issue_family: {family}')


def family_from_issue(issue: dict[str, Any]) -> str:
    family = str(require(issue, 'criterion.issue_family'))
    if family not in SUPPORTED_FAMILIES:
        issue_id = require(issue, 'issue_id')
        raise ValueError(f'Unsupported issue_family {family}: {issue_id}')
    return family


def enriched_criterion(issue: dict[str, Any]) -> dict[str, Any]:
    family = family_from_issue(issue)
    wcag_target = str(require(issue, 'criterion.wcag_target'))
    meta = wcag_meta_for_target(wcag_target)
    return {
        'issue_family': family,
        'wcag_target': wcag_target,
        'assessment_requirement': meta['assessment_requirement'],
        'wcag': {
            'number': meta['number'],
            'name': meta['name'],
            'link_name': meta['link_name'],
            'url': meta['url'],
            'criterion_text': meta['criterion_text'],
        },
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


def multi_output_format(family: str | None = None) -> dict[str, Any]:
    return {
        'verdict': 'issue_found | no_issue_found',
        'issues': [
            {
                'selector': SELECTOR_FIELD_DESCRIPTION,
                'target': TARGET_FIELD_DESCRIPTION,
                'issue_type': family if family else 'error_identification | error_suggestion | error_prevention | status_messages',
                'observed_behavior': 'concise description of the observed error behavior',
                'evidence': 'concrete DOM, interaction, text, or accessibility facts supporting the issue',
            }
        ],
    }


def l3_wcag_criteria() -> dict[str, dict[str, str]]:
    order = [
        'WCAG 3.3.1 Error Identification',
        'WCAG 3.3.3 Error Suggestion',
        'WCAG 3.3.4 Error Prevention (Legal, Financial, Data)',
        'WCAG 4.1.3 Status Messages',
    ]
    result: dict[str, dict[str, str]] = {}
    for target in order:
        meta = WCAG_META[target]
        result[meta['assessment_requirement']] = {
            'target': target,
            'text': meta['criterion_text'],
            'url': meta['url'],
        }
    return result


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
        'source.review_status',
        'page.site',
        'page.page_name',
        'page.start_url',
        'gold.expected_verdict',
    ]:
        require(instance, field)
    optional(instance, 'page.auth_state_file')
    if expected_level == 'level2':
        family = require(instance, 'scope.issue_family')
        wcag_target, meta = wcag_meta_for_family(str(family))
        if require(instance, 'scope.wcag_target') != wcag_target:
            raise ValueError(f'L2 wcag_target mismatch for {iid}')
        if require(instance, 'scope.assessment_requirement') != meta['assessment_requirement']:
            raise ValueError(f'L2 assessment_requirement mismatch for {iid}')
        for issue in issues:
            if family_from_issue(issue) != family:
                issue_id = require(issue, 'issue_id')
                raise ValueError(f'L2 issue family mismatch for {iid}: {issue_id}')
    else:
        if require(instance, 'scope.assessment_scope') != 'ERROR E.1-E.4':
            raise ValueError(f'L3 assessment_scope mismatch for {iid}')


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
    iid = str(require(instance, 'instance_id'))
    family = str(require(instance, 'scope.issue_family'))
    wcag_target, meta = wcag_meta_for_family(family)
    page_name = str(require(instance, 'page.page_name'))
    task_id = f'{iid}.verify.level2.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_2_clause_given_location_hidden',
        'issue_domain': 'error',
        'issue_family': family,
        'wcag_target': wcag_target,
        'wcag_source_url': meta['url'],
        'wcag_clause_text': meta['criterion_text'],
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': f'{level2_target_description(family)} on the {page_name} page',
        'setup': None,
        'output_format': multi_output_format(family),
    }


def level2_target_description(family: str) -> str:
    if family == 'error_identification':
        return 'input-error identification paths'
    if family == 'error_suggestion':
        return 'input-error suggestion paths'
    if family == 'error_prevention':
        return 'legal, financial, data-modifying, or test-response submission paths'
    if family == 'status_messages':
        return 'interactions that trigger same-page error or status messages'
    raise ValueError(f'Unsupported issue_family {family}')


def build_l3_task(instance: dict[str, Any], output_root: Path) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    page_name = str(require(instance, 'page.page_name'))
    task_id = f'{iid}.verify.level3.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_3_error_assessment_scope',
        'issue_domain': 'error',
        'issue_family': 'error_assessment_e1_to_e4',
        'wcag_target': 'ERROR assessment E.1-E.4',
        'wcag_clause_text': 'ERROR assessment scope covers E.1 Error Identification, E.2 Error Suggestion, E.3 Error Prevention, and E.4 Status Messages.',
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': f'error handling and status-message behavior within ERROR assessment scope E.1-E.4 on the {page_name} page',
        'setup': None,
        'wcag_criteria': l3_wcag_criteria(),
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
        'task_level': level,
        'source': source_record(instance),
        'page': page_record(instance),
        'scope': scope_record(instance, level),
        'gold': {
            'issue_present': require(instance, 'issue_present'),
            'expected_verdict': require(instance, 'gold.expected_verdict'),
            'issues': [inventory_issue(issue) for issue in require(instance, 'gold.issues')],
        },
    }


def write_task_rule_prompt(task: dict[str, Any], rule: dict[str, Any], output_root: Path) -> list[Path]:
    dirs = output_dirs(output_root)
    task_id = task['task_id']
    task_path = dirs['tasks'] / f'{task_id}.yaml'
    rule_path = dirs['rules'] / f'{task_id}.yaml'
    prompt_path = dirs['prompts'] / f'{task_id}.task.prompt.txt'
    task_path.write_text(dump_yaml(task), encoding='utf-8')
    rule_path.write_text(dump_yaml(rule), encoding='utf-8')
    prompt_path.write_text(build_task_prompt(load_task(task_path)) + '\n', encoding='utf-8')
    return [task_path, rule_path, prompt_path]


def task_for_level(instance: dict[str, Any], output_root: Path, level: str) -> dict[str, Any]:
    if level == 'level2':
        return build_l2_task(instance, output_root)
    if level == 'level3':
        return build_l3_task(instance, output_root)
    raise ValueError(f'Unsupported merge level: {level}')


def generate_all_merge_assets(
    *,
    source_root: Path = SOURCE_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    levels: tuple[str, ...] | list[str] | None = None,
) -> list[Path]:
    selected_levels = tuple(levels) if levels is not None else ('level2', 'level3')
    if not selected_levels:
        raise ValueError('levels must not be empty')
    unsupported = sorted(set(selected_levels) - SUPPORTED_LEVELS)
    if unsupported:
        raise ValueError(f'Unsupported levels: {unsupported}')
    clean_output_dirs(output_root)
    written: list[Path] = []
    for level in selected_levels:
        for instance in load_merge_instances(level, source_root):
            task = task_for_level(instance, output_root, level)
            rule = build_rule(task, instance, level)
            written.extend(write_task_rule_prompt(task, rule, output_root))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate ERROR merge L2/L3 assets.')
    parser.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--levels', nargs='+', choices=sorted(SUPPORTED_LEVELS), default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    written = generate_all_merge_assets(
        source_root=args.source_root,
        output_root=args.output_root,
        levels=args.levels,
    )
    print(f'Wrote {len(written)} files under {args.output_root}')


if __name__ == '__main__':
    main()
