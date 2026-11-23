#!/usr/bin/env python3
"""Generate Keyboard MERGE L2/L3 assets from cleaned merge source markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from agent.gt_keyboard.generate_clean_assets import (
    DEFAULT_TEMPLATE_ROOT,
    KEYBOARD_L3_CLAUSE_TEXT,
    KEYBOARD_L3_ISSUE_FAMILY,
    KEYBOARD_L3_SCOPE,
    KEYBOARD_L3_WCAG_TARGET,
    SUPPORTED_FAMILIES,
    clean_output_dirs,
    dump_yaml,
    l3_wcag_criteria,
    multi_output_format,
    optional,
    output_dirs,
    require,
    rule_file_for_task,
    source_templates,
)
from agent.gt_keyboard.run_task import build_task_prompt, load_task


GT_KEYBOARD_DIR = Path(__file__).resolve().parent
SOURCE_ROOT = GT_KEYBOARD_DIR / 'source_md_clean' / 'merge-instances'
DEFAULT_OUTPUT_ROOT = GT_KEYBOARD_DIR / 'generated_clean_pilot' / 'generated_merge'

SUPPORTED_LEVELS = {'level2', 'level3'}


def extract_first_yaml_block(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    match = re.search(r'```yaml\s*\n(.*?)\n```', text, flags=re.S)
    if not match:
        raise ValueError(f'No fenced yaml block found: {path}')
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f'YAML block must be a mapping: {path}')
    return data


def criterion_by_family(templates: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    criteria: dict[str, dict[str, Any]] = {}
    for template in templates.values():
        criterion = require(template, 'criterion')
        family = str(require(criterion, 'issue_family'))
        if family not in SUPPORTED_FAMILIES:
            continue
        existing = criteria.get(family)
        if existing is not None and require(existing, 'wcag_target') != require(criterion, 'wcag_target'):
            raise ValueError('Conflicting Keyboard criterion metadata for family: ' + family)
        criteria[family] = criterion
    missing = sorted(SUPPORTED_FAMILIES - set(criteria))
    if missing:
        raise ValueError('Missing Keyboard template criterion metadata for families: ' + ', '.join(missing))
    return criteria


def family_from_issue(issue: dict[str, Any]) -> str:
    family = str(require(issue, 'criterion.issue_family'))
    if family not in SUPPORTED_FAMILIES:
        issue_id = require(issue, 'issue_id')
        raise ValueError(f'Unsupported Keyboard issue_family {family}: {issue_id}')
    return family


def enriched_criterion(issue: dict[str, Any], criteria: dict[str, dict[str, Any]]) -> dict[str, Any]:
    family = family_from_issue(issue)
    wcag_target = str(require(issue, 'criterion.wcag_target'))
    criterion = criteria[family]
    if wcag_target != require(criterion, 'wcag_target'):
        issue_id = require(issue, 'issue_id')
        raise ValueError(f'wcag_target mismatch for {issue_id}: {wcag_target}')
    return criterion


def inventory_issue(issue: dict[str, Any], criteria: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        'issue_id': require(issue, 'issue_id'),
        'target': {
            'selector': require(issue, 'target.selector'),
            'description': require(issue, 'target.description'),
            'coverage_policy': require(issue, 'target.coverage_policy'),
        },
        'criterion': enriched_criterion(issue, criteria),
        'evidence_rule': require(issue, 'evidence_rule'),
    }


def modality_policy_for_family(family: str) -> str:
    if family == 'on_input':
        return 'unrestricted_detection'
    return 'keyboard_primary_pointer_confirmation'


def level2_target_description(family: str, page_name: str) -> str:
    if family == 'keyboard_nonreachable':
        return f'interactive interface components on the {page_name} page'
    if family == 'on_input':
        return f'controls that change value or selection on the {page_name} page'
    if family == 'character_key_shortcuts':
        return f'single printable-character shortcuts on the {page_name} page'
    raise ValueError('Unsupported issue_family ' + family)


def validate_issue(issue: dict[str, Any]) -> None:
    for field in [
        'issue_id',
        'target.selector',
        'target.description',
        'target.coverage_policy',
        'criterion.issue_family',
        'criterion.wcag_target',
        'evidence_rule',
    ]:
        require(issue, field)
    if require(issue, 'target.coverage_policy') not in {'single', 'representative_group'}:
        issue_id = require(issue, 'issue_id')
        raise ValueError(f'Unsupported coverage_policy for {issue_id}')
    family_from_issue(issue)


def validate_merge_instance(
    instance: dict[str, Any],
    expected_level: str,
    criteria: dict[str, dict[str, Any]],
) -> None:
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
    for issue in issues:
        validate_issue(issue)
        enriched_criterion(issue, criteria)
    if expected_level == 'level2':
        family = str(require(instance, 'scope.issue_family'))
        if family not in SUPPORTED_FAMILIES:
            raise ValueError(f'Unsupported L2 issue_family for {iid}: {family}')
        criterion = criteria[family]
        if require(instance, 'scope.wcag_target') != require(criterion, 'wcag_target'):
            raise ValueError(f'L2 wcag_target mismatch for {iid}')
        if require(instance, 'scope.assessment_requirement') != require(criterion, 'assessment_requirement'):
            raise ValueError(f'L2 assessment_requirement mismatch for {iid}')
        for issue in issues:
            if family_from_issue(issue) != family:
                issue_id = require(issue, 'issue_id')
                raise ValueError(f'L2 issue family mismatch for {iid}: {issue_id}')
    elif require(instance, 'scope.assessment_scope') != KEYBOARD_L3_SCOPE:
        raise ValueError(f'L3 assessment_scope mismatch for {iid}')


def load_merge_instances(
    level: str,
    source_root: Path = SOURCE_ROOT,
    criteria: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if level not in SUPPORTED_LEVELS:
        raise ValueError('Unsupported merge level: ' + level)
    if criteria is None:
        criteria = criterion_by_family(source_templates(DEFAULT_TEMPLATE_ROOT))
    source_dir = source_root / level
    paths = sorted(source_dir.glob('*.md'))
    if not paths:
        raise ValueError(f'No merge source markdown files found: {source_dir}')
    instances = [extract_first_yaml_block(path) for path in paths]
    ids = [require(instance, 'instance_id') for instance in instances]
    if len(ids) != len(set(ids)):
        raise ValueError(f'Duplicate merge instance_id under {source_dir}')
    for instance in instances:
        validate_merge_instance(instance, level, criteria)
    return instances


def task_criterion_fields(criterion: dict[str, Any]) -> dict[str, Any]:
    return {
        'wcag_target': require(criterion, 'wcag_target'),
        'wcag_source_url': require(criterion, 'wcag.url'),
        'wcag_clause_text': require(criterion, 'wcag.criterion_text'),
        'ai_web': require(criterion, 'ai_web'),
    }


def build_l2_task(
    instance: dict[str, Any],
    output_root: Path,
    criteria: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    family = str(require(instance, 'scope.issue_family'))
    criterion = criteria[family]
    page_name = str(require(instance, 'page.page_name'))
    task_id = f'{iid}.verify.level2.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_2_clause_given_location_hidden',
        'issue_domain': 'keyboard',
        'issue_family': family,
        **task_criterion_fields(criterion),
        'modality_policy': modality_policy_for_family(family),
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': level2_target_description(family, page_name),
        'setup': None,
        'output_format': multi_output_format(family),
    }


def build_l3_task(
    instance: dict[str, Any],
    output_root: Path,
    templates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    page_name = str(require(instance, 'page.page_name'))
    task_id = f'{iid}.verify.level3.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_3_keyboard_assessment_scope',
        'issue_domain': 'keyboard',
        'issue_family': KEYBOARD_L3_ISSUE_FAMILY,
        'wcag_target': KEYBOARD_L3_WCAG_TARGET,
        'wcag_clause_text': KEYBOARD_L3_CLAUSE_TEXT,
        'modality_policy': 'keyboard_primary_pointer_confirmation',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': f'keyboard behavior within {KEYBOARD_L3_SCOPE} on the {page_name} page',
        'setup': None,
        'wcag_criteria': l3_wcag_criteria(templates),
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


def build_rule(
    task: dict[str, Any],
    instance: dict[str, Any],
    level: str,
    criteria: dict[str, dict[str, Any]],
) -> dict[str, Any]:
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
            'issues': [inventory_issue(issue, criteria) for issue in require(instance, 'gold.issues')],
        },
    }


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(data), encoding='utf-8')


def write_task_rule_prompt(task: dict[str, Any], rule: dict[str, Any], output_root: Path) -> list[Path]:
    dirs = output_dirs(output_root)
    task_id = str(task['task_id'])
    task_path = dirs['tasks'] / f'{task_id}.yaml'
    rule_path = dirs['rules'] / f'{task_id}.yaml'
    prompt_path = dirs['prompts'] / f'{task_id}.task.prompt.txt'
    write_yaml(task_path, task)
    write_yaml(rule_path, rule)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(build_task_prompt(load_task(task_path)) + '\n', encoding='utf-8')
    return [task_path, rule_path, prompt_path]


def normalize_levels(levels: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    selected = tuple(levels) if levels is not None else ('level2', 'level3')
    if not selected:
        raise ValueError('levels must not be empty')
    unsupported = sorted(set(selected) - SUPPORTED_LEVELS)
    if unsupported:
        raise ValueError('Unsupported levels: ' + str(unsupported))
    return selected


def generate_all_merge_assets(
    *,
    source_root: Path = SOURCE_ROOT,
    template_root: Path = DEFAULT_TEMPLATE_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    levels: tuple[str, ...] | list[str] | None = None,
) -> list[Path]:
    selected_levels = normalize_levels(levels)
    templates = source_templates(template_root)
    criteria = criterion_by_family(templates)
    clean_output_dirs(output_root)
    written: list[Path] = []
    for level in selected_levels:
        for instance in load_merge_instances(level, source_root, criteria):
            if level == 'level2':
                task = build_l2_task(instance, output_root, criteria)
            else:
                task = build_l3_task(instance, output_root, templates)
            rule = build_rule(task, instance, level, criteria)
            written.extend(write_task_rule_prompt(task, rule, output_root))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate Keyboard MERGE L2/L3 assets.')
    parser.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    parser.add_argument('--template-root', type=Path, default=DEFAULT_TEMPLATE_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--levels', nargs='+', choices=sorted(SUPPORTED_LEVELS), default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    written = generate_all_merge_assets(
        source_root=args.source_root,
        template_root=args.template_root,
        output_root=args.output_root,
        levels=args.levels,
    )
    print('Wrote ' + str(len(written)) + ' files under ' + str(args.output_root))


if __name__ == '__main__':
    main()
