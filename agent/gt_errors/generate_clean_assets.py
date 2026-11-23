from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from agent.gt_errors.run_task import (
    SELECTOR_FIELD_DESCRIPTION,
    TARGET_FIELD_DESCRIPTION,
    build_task_prompt,
    load_task,
)


GT_ERRORS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_ERRORS_DIR.parent.parent
DEFAULT_SOURCE_ROOT = GT_ERRORS_DIR / 'source_md_clean' / 'issue-instances'
DEFAULT_OUTPUT_ROOT = GT_ERRORS_DIR / 'generated_clean_pilot' / 'generated'

ERROR_PREVENTION_META = {
    'number': '3.3.4',
    'name': 'Error Prevention (Legal, Financial, Data)',
    'link_name': 'WCAG 3.3.4',
    'url': 'https://www.w3.org/WAI/WCAG21/Understanding/error-prevention-legal-financial-data.html',
    'criterion_text': (
        'If submitting data might have serious consequences, users must be able to correct the '
        'data input before finalizing a submission. If the page allows users to make legal '
        'commitments or financial transactions, modify or delete data in a data storage system, '
        'or submit test responses, at least one of the following must be true: submissions are '
        'reversible; data entered by the user is checked for input errors, and the user is given '
        'an opportunity to correct them; or the user can review, confirm, and correct information '
        'before finalizing the submission.'
    ),
    'assessment_requirement': 'E.3 Error Prevention',
}

WCAG_META: dict[str, dict[str, str]] = {
    'WCAG 3.3.1 Error Identification': {
        'number': '3.3.1',
        'name': 'Error Identification',
        'link_name': 'WCAG 3.3.1',
        'url': 'https://www.w3.org/WAI/WCAG21/Understanding/error-identification.html',
        'criterion_text': (
            'If an input error is automatically detected, the item that is in error is identified '
            'and the error is described to the user in text.'
        ),
        'assessment_requirement': 'E.1 Error Identification',
    },
    'WCAG 3.3.3 Error Suggestion': {
        'number': '3.3.3',
        'name': 'Error Suggestion',
        'link_name': 'WCAG 3.3.3',
        'url': 'https://www.w3.org/WAI/WCAG21/Understanding/error-suggestion.html',
        'criterion_text': (
            'If an input error is automatically detected and suggestions for correction are known, '
            'then the suggestions are provided to the user, unless it would jeopardize the security '
            'or purpose of the content.'
        ),
        'assessment_requirement': 'E.2 Error Suggestion',
    },
    'WCAG 3.3.4 Error Prevention (Legal, Financial, Data)': ERROR_PREVENTION_META,
    'WCAG 3.3.4 Error Prevention': ERROR_PREVENTION_META,
    'WCAG 4.1.3 Status Messages': {
        'number': '4.1.3',
        'name': 'Status Messages',
        'link_name': 'WCAG 4.1.3',
        'url': 'https://www.w3.org/WAI/WCAG21/Understanding/status-messages.html',
        'criterion_text': (
            'In content implemented using markup languages, status messages can be programmatically '
            'determined through role or properties such that they can be presented to the user by '
            'assistive technologies without receiving focus.'
        ),
        'assessment_requirement': 'E.4 Status Messages',
    },
}

SUPPORTED_FAMILIES = {'error_identification', 'error_suggestion', 'error_prevention', 'status_messages'}
SUPPORTED_LEVELS = {'level1', 'level2', 'level3'}



class CleanDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def _str_presenter(dumper: yaml.Dumper, data: str) -> yaml.nodes.ScalarNode:
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    if len(data) > 88:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


CleanDumper.add_representer(str, _str_presenter)


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.dump(data, Dumper=CleanDumper, allow_unicode=False, default_flow_style=False, sort_keys=False, width=88)


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


def parse_source_md(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    match = re.search(r'```yaml\n(.*?)\n```', text, re.S)
    if not match:
        raise ValueError(f'Missing YAML block: {path}')
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f'Source YAML root must be a mapping: {path}')
    return data


def source_instances(source_root: Path) -> list[dict[str, Any]]:
    items = [parse_source_md(path) for path in sorted(source_root.glob('*.md'))]
    ids = [require(item, 'instance_id') for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate instance_id in error source md')
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


def rule_file_for_task(task_id: str, output_root: Path) -> str:
    name = f'{task_id}.yaml'.replace('.verify.v1.yaml', '.verify.shared.v1.yaml')
    return display_path(output_root / 'evaluate-rules' / name)


def level1_rule_file_for_task(task_id: str, output_root: Path) -> str:
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


def level2_target_description(family: str) -> str:
    if family == 'error_identification':
        return 'input-error identification paths on this page'
    if family == 'error_suggestion':
        return 'input-error suggestion paths on this page'
    if family == 'error_prevention':
        return 'legal, financial, data-modifying, or test-response submission paths on this page'
    if family == 'status_messages':
        return 'interactions that trigger same-page error or status messages on this page'
    raise ValueError(f'Unsupported issue_family {family}')


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


def build_l1_task(instance: dict[str, Any], output_root: Path) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    family = issue_family(instance)
    meta = wcag_meta(instance)
    task_id = f'{iid}.verify.v1'
    task = {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': level1_rule_file_for_task(task_id, output_root),
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
    return task


def build_l2_task(instance: dict[str, Any], output_root: Path) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    family = issue_family(instance)
    meta = wcag_meta(instance)
    task_id = f'{iid}.verify.level2.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_2_clause_given_location_hidden',
        'issue_domain': 'error',
        'issue_family': family,
        'wcag_target': require(instance, 'criterion.wcag_target'),
        'wcag_source_url': meta['url'],
        'wcag_clause_text': meta['criterion_text'],
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': level2_target_description(family),
        'setup': None,
        'output_format': multi_output_format(family),
    }


def build_l3_task(instance: dict[str, Any], output_root: Path) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
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
        'target_description': 'error handling and status-message behavior within ERROR assessment scope E.1-E.4 on this page',
        'setup': None,
        'wcag_criteria': l3_wcag_criteria(),
        'output_format': multi_output_format(),
    }


def build_rule_for_task(task: dict[str, Any], instance: dict[str, Any], level: str) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    family = issue_family(instance)
    meta = wcag_meta(instance)
    return {
        'task_id': task['task_id'],
        'instance_id': iid,
        'task_level': level,
        'source': require(instance, 'source'),
        'page': {
            'site': require(instance, 'page.site'),
            'page_name': require(instance, 'page.page_name'),
            'start_url': require(instance, 'page.start_url'),
        },
        'gold': {
            'issue_present': require(instance, 'issue_present'),
            'expected_verdict': require(instance, 'gold.expected_verdict'),
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
            'Verdict must be exactly correct.',
            'Target may use a different locator, but it must resolve to the same DOM or accessibility target as the gold selector.',
            'Behavior may use different wording, but it must satisfy the gold evidence rule.',
            'Reporting unrelated issues does not count for this task.',
        ],
    }


def build_l1_rule(instance: dict[str, Any]) -> dict[str, Any]:
    task = {'task_id': f"{require(instance, 'instance_id')}.verify.v1"}
    return build_rule_for_task(task, instance, 'level1')


def task_for_level(instance: dict[str, Any], output_root: Path, level: str) -> dict[str, Any]:
    if level == 'level1':
        return build_l1_task(instance, output_root)
    if level == 'level2':
        return build_l2_task(instance, output_root)
    if level == 'level3':
        return build_l3_task(instance, output_root)
    raise ValueError(f'Unsupported level: {level}')


def write_task_rule_prompt(task: dict[str, Any], rule: dict[str, Any], output_root: Path) -> list[Path]:
    dirs = output_dirs(output_root)
    task_id = task['task_id']
    task_path = dirs['tasks'] / f'{task_id}.yaml'
    rule_path = dirs['rules'] / Path(task['evaluate_rule_file']).name
    prompt_path = dirs['prompts'] / f'{task_id}.task.prompt.txt'
    task_path.write_text(dump_yaml(task), encoding='utf-8')
    rule_path.write_text(dump_yaml(rule), encoding='utf-8')
    prompt_path.write_text(build_task_prompt(load_task(task_path)) + '\n', encoding='utf-8')
    return [task_path, rule_path, prompt_path]


def write_assets(instance: dict[str, Any], output_root: Path, levels: tuple[str, ...]) -> list[Path]:
    written: list[Path] = []
    for level in levels:
        task = task_for_level(instance, output_root, level)
        rule = build_rule_for_task(task, instance, level)
        written.extend(write_task_rule_prompt(task, rule, output_root))
    return written


def normalize_levels(levels: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if levels is None:
        return ('level1',)
    result = tuple(levels)
    if not result:
        raise ValueError('levels must not be empty')
    unsupported = sorted(set(result) - SUPPORTED_LEVELS)
    if unsupported:
        raise ValueError(f'Unsupported levels: {unsupported}')
    return result


def select_instances(instances: list[dict[str, Any]], instance_ids: list[str] | tuple[str, ...] | None) -> list[dict[str, Any]]:
    if instance_ids is None:
        return instances
    wanted = list(instance_ids)
    by_id = {str(require(instance, 'instance_id')): instance for instance in instances}
    missing = [iid for iid in wanted if iid not in by_id]
    if missing:
        raise ValueError(f'Missing source instance ids: {missing}')
    return [by_id[iid] for iid in wanted]


def generate_all_clean_assets(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    levels: tuple[str, ...] | list[str] | None = None,
    instance_ids: list[str] | tuple[str, ...] | None = None,
) -> list[Path]:
    selected_levels = normalize_levels(levels)
    clean_output_dirs(output_root)
    written: list[Path] = []
    for instance in select_instances(source_instances(source_root), instance_ids):
        written.extend(write_assets(instance, output_root, selected_levels))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate ERROR clean-pilot base L1 assets.')
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--levels', nargs='+', choices=sorted(SUPPORTED_LEVELS), default=None)
    parser.add_argument('--instance-id', dest='instance_ids', action='append', default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    written = generate_all_clean_assets(
        source_root=args.source_root,
        output_root=args.output_root,
        levels=args.levels,
        instance_ids=args.instance_ids,
    )
    print(f'Wrote {len(written)} files under {args.output_root}')


if __name__ == '__main__':
    main()
