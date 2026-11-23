from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from agent.gt_keyboard.run_task import build_task_prompt, load_task


GT_KEYBOARD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_KEYBOARD_DIR.parent.parent
DEFAULT_SOURCE_ROOT = GT_KEYBOARD_DIR / 'source_md_clean' / 'issue-instances'
DEFAULT_TEMPLATE_ROOT = GT_KEYBOARD_DIR / 'source_md_clean' / 'issue-templates'
DEFAULT_OUTPUT_ROOT = GT_KEYBOARD_DIR / 'generated_clean_pilot' / 'generated'

SUPPORTED_FAMILIES = {'keyboard_nonreachable', 'on_input', 'character_key_shortcuts'}
SUPPORTED_LEVELS = {'level1', 'level2', 'level3'}
KEYBOARD_L3_ISSUE_FAMILY = 'keyboard_assessment_1_1_1_2_1_3_1_4_1_6'
KEYBOARD_L3_WCAG_TARGET = 'Keyboard assessment 1.1, 1.2, 1.3, 1.4, and 1.6'
KEYBOARD_L3_SCOPE = 'Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6'
KEYBOARD_L3_CLAUSE_TEXT = (
    'Keyboard assessment scope covers 1.1 Keyboard navigation, 1.2 No keyboard traps, '
    '1.3 On focus, 1.4 On input, and 1.6 Character key shortcuts.'
)
KEYBOARD_L3_ISSUE_TYPES = [
    'keyboard_nonreachable',
    'keyboard_trap',
    'on_focus',
    'on_input',
    'character_key_shortcuts',
]
KEYBOARD_L3_LABEL_ORDER = [
    '1.1 Keyboard navigation',
    '1.2 No keyboard traps',
    '1.3 On focus',
    '1.4 On input',
    '1.6 Character key shortcuts',
]
KEYBOARD_L3_EXTRA_CRITERIA = {
    '1.2 No keyboard traps': {
        'target': 'WCAG 2.1.2 No Keyboard Trap',
        'text': (
            'If keyboard focus can be moved to a component of the page using a keyboard interface, then focus can be moved away from that '
            'component using only a keyboard interface, and, if it requires more than unmodified arrow or tab keys or other standard exit methods, '
            'the user is advised of the method for moving focus away.'
        ),
        'url': 'https://www.w3.org/WAI/WCAG21/Understanding/no-keyboard-trap.html',
    },
    '1.3 On focus': {
        'target': 'WCAG 3.2.1 On Focus',
        'text': 'When any user interface component receives focus, it does not initiate a change of context.',
        'url': 'https://www.w3.org/WAI/WCAG21/Understanding/on-focus.html',
    },
}


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
    return yaml.dump(
        data,
        Dumper=CleanDumper,
        allow_unicode=False,
        default_flow_style=False,
        sort_keys=False,
        width=88,
    )


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
        raise ValueError('Duplicate instance_id in keyboard source md')
    return items


def source_templates(template_root: Path) -> dict[str, dict[str, Any]]:
    templates = [parse_source_md(path) for path in sorted(template_root.glob('*.md'))]
    result = {str(require(template, 'template_id')): template for template in templates}
    if len(result) != len(templates):
        raise ValueError('Duplicate template_id in keyboard source md')
    return result


def template_for_instance(instance: dict[str, Any], templates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    template_id = str(require(instance, 'template_id'))
    template = templates.get(template_id)
    if template is None:
        raise ValueError('Missing template for ' + str(require(instance, 'instance_id')))
    return template


def criterion_for(instance: dict[str, Any], templates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    criterion = require(template_for_instance(instance, templates), 'criterion')
    if require(instance, 'criterion.issue_family') != require(criterion, 'issue_family'):
        raise ValueError('issue_family mismatch for ' + str(require(instance, 'instance_id')))
    if require(instance, 'criterion.wcag_target') != require(criterion, 'wcag_target'):
        raise ValueError('wcag_target mismatch for ' + str(require(instance, 'instance_id')))
    return criterion


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


def issue_family(instance: dict[str, Any], templates: dict[str, dict[str, Any]] | None = None) -> str:
    if templates is None:
        family = str(require(instance, 'criterion.issue_family'))
    else:
        family = str(require(criterion_for(instance, templates), 'issue_family'))
    if family not in SUPPORTED_FAMILIES:
        raise ValueError('Unsupported issue_family ' + family + ': ' + str(require(instance, 'instance_id')))
    return family


def task_criterion_fields(instance: dict[str, Any], templates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    criterion = criterion_for(instance, templates)
    return {
        'wcag_target': require(criterion, 'wcag_target'),
        'wcag_source_url': require(criterion, 'wcag.url'),
        'wcag_clause_text': require(criterion, 'wcag.criterion_text'),
        'ai_web': require(criterion, 'ai_web'),
    }


def rule_file_for_task(task_id: str, output_root: Path, *, level1: bool = False) -> str:
    name = f'{task_id}.yaml'.replace('.verify.v1.yaml', '.verify.shared.v1.yaml')
    if not level1:
        name = f'{task_id}.yaml'
    return display_path(output_root / 'evaluate-rules' / name)


def modality_policy(instance: dict[str, Any]) -> str:
    explicit = optional(instance, 'modality_policy')
    if explicit:
        return str(explicit)
    if issue_family(instance) == 'on_input':
        return 'unrestricted_detection'
    return 'keyboard_primary_pointer_confirmation'


def single_output_format(family: str) -> dict[str, str]:
    return {
        'verdict': 'issue_found | no_issue_found',
        'selector': 'verified CSS selector for the reported keyboard target, or empty string',
        'target': 'natural-language target description',
        'issue_type': family,
        'observed_behavior': 'concise description of the observed keyboard behavior',
        'evidence': 'concrete keyboard path, rendered behavior, DOM, or accessibility facts supporting the verdict',
    }


def multi_output_format(family: str | None = None) -> dict[str, Any]:
    return {
        'verdict': 'issue_found | no_issue_found',
        'issues': [
            {
                'selector': 'verified CSS selector for the reported keyboard target, or empty string',
                'target': 'natural-language description of the reported keyboard target',
                'issue_type': family if family else ' | '.join(KEYBOARD_L3_ISSUE_TYPES),
                'observed_behavior': 'concise description of the observed keyboard behavior',
                'evidence': 'concrete keyboard path, rendered behavior, DOM, or accessibility facts supporting the issue',
            }
        ],
    }


def level2_target_description(family: str) -> str:
    if family == 'keyboard_nonreachable':
        return 'interactive interface components on this page'
    if family == 'on_input':
        return 'controls that change value or selection on this page'
    if family == 'character_key_shortcuts':
        return 'single printable-character shortcuts on this page'
    raise ValueError('Unsupported issue_family ' + family)


def _add_l3_criterion(by_label: dict[str, dict[str, str]], label: str, fields: dict[str, str]) -> None:
    existing = by_label.get(label)
    if existing is not None and existing != fields:
        raise ValueError('Conflicting Keyboard L3 criterion fields for ' + label)
    by_label[label] = fields


def l3_wcag_criteria(templates: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, str]]:
    by_label: dict[str, dict[str, str]] = {}
    for label, fields in KEYBOARD_L3_EXTRA_CRITERIA.items():
        _add_l3_criterion(by_label, label, dict(fields))
    if templates:
        for template in templates.values():
            criterion = require(template, 'criterion')
            label = str(require(criterion, 'assessment_requirement'))
            if label not in KEYBOARD_L3_LABEL_ORDER:
                continue
            _add_l3_criterion(
                by_label,
                label,
                {
                    'target': require(criterion, 'wcag_target'),
                    'text': require(criterion, 'wcag.criterion_text'),
                    'url': require(criterion, 'wcag.url'),
                },
            )
    missing = [label for label in KEYBOARD_L3_LABEL_ORDER if label not in by_label]
    if missing:
        raise ValueError('Missing Keyboard L3 criteria: ' + str(missing))
    return {label: by_label[label] for label in KEYBOARD_L3_LABEL_ORDER}


def build_l1_task(instance: dict[str, Any], templates: dict[str, dict[str, Any]], output_root: Path) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    family = issue_family(instance, templates)
    task_id = f'{iid}.verify.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root, level1=True),
        'difficulty': 'level_1_direct_verification',
        'issue_domain': 'keyboard',
        'issue_family': family,
        **task_criterion_fields(instance, templates),
        'modality_policy': modality_policy(instance),
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': require(instance, 'target.description'),
        'setup': optional(instance, 'setup'),
        'output_format': single_output_format(family),
        'target_selector': require(instance, 'target.selector'),
    }


def build_l2_task(instance: dict[str, Any], templates: dict[str, dict[str, Any]], output_root: Path) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
    family = issue_family(instance, templates)
    task_id = f'{iid}.verify.level2.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_2_clause_given_location_hidden',
        'issue_domain': 'keyboard',
        'issue_family': family,
        **task_criterion_fields(instance, templates),
        'modality_policy': modality_policy(instance),
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': optional(instance, 'page.auth_state_file'),
        'target_description': level2_target_description(family),
        'setup': optional(instance, 'setup'),
        'output_format': multi_output_format(family),
    }


def build_l3_task(instance: dict[str, Any], templates: dict[str, dict[str, Any]], output_root: Path) -> dict[str, Any]:
    iid = str(require(instance, 'instance_id'))
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
        'target_description': 'keyboard behavior within ' + KEYBOARD_L3_SCOPE + ' on this page',
        'setup': optional(instance, 'setup'),
        'wcag_criteria': l3_wcag_criteria(templates),
        'output_format': multi_output_format(),
    }


def build_rule_for_task(task: dict[str, Any], instance: dict[str, Any], level: str, templates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    criterion = criterion_for(instance, templates)
    return {
        'task_id': task['task_id'],
        'instance_id': str(require(instance, 'instance_id')),
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
            'issue_type': [require(criterion, 'wcag_target'), require(instance, 'template_id')],
            'target': require(instance, 'target'),
            'criterion': criterion,
            'evidence_rule': require(instance, 'gold.evidence_rule'),
        },
        'evaluation_logic': evaluation_logic_for_level(level),
    }


def evaluation_logic_for_level(level: str) -> list[str]:
    if level == 'level3':
        return [
            'Verdict must be exactly correct.',
            'Agent may report one or more findings under Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6.',
            'Pass if at least one reported finding correctly matches the reviewed gold issue for this task.',
            'Target may use a different locator, but it must resolve to the same DOM or accessibility target as the gold selector.',
            'Behavior may use different wording, but it must satisfy the gold evidence rule.',
            'Reporting other true keyboard issues does not by itself count unless one reported finding matches the reviewed gold issue.',
        ]
    return [
        'Verdict must be exactly correct.',
        'Target may use a different locator, but it must resolve to the same DOM or accessibility target as the gold selector.',
        'Behavior may use different wording, but it must satisfy the gold evidence rule.',
        'Reporting unrelated keyboard issues does not count for this task.',
    ]


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(data), encoding='utf-8')


def write_task_rule_prompt(task: dict[str, Any], rule: dict[str, Any], output_root: Path) -> list[Path]:
    dirs = output_dirs(output_root)
    task_id = str(task['task_id'])
    task_path = dirs['tasks'] / (task_id + '.yaml')
    rule_path = dirs['rules'] / Path(str(task['evaluate_rule_file'])).name
    prompt_path = dirs['prompts'] / (task_id + '.task.prompt.txt')
    write_yaml(task_path, task)
    write_yaml(rule_path, rule)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(build_task_prompt(load_task(task_path)) + '\n', encoding='utf-8')
    return [task_path, rule_path, prompt_path]


def task_for_level(instance: dict[str, Any], templates: dict[str, dict[str, Any]], output_root: Path, level: str) -> dict[str, Any]:
    if level == 'level1':
        return build_l1_task(instance, templates, output_root)
    if level == 'level2':
        return build_l2_task(instance, templates, output_root)
    if level == 'level3':
        return build_l3_task(instance, templates, output_root)
    raise ValueError('Unsupported level: ' + level)


def normalize_levels(levels: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if levels is None:
        return ('level1',)
    result = tuple(levels)
    if not result:
        raise ValueError('levels must not be empty')
    unsupported = sorted(set(result) - SUPPORTED_LEVELS)
    if unsupported:
        raise ValueError('Unsupported levels: ' + str(unsupported))
    return result


def select_instances(instances: list[dict[str, Any]], instance_ids: list[str] | tuple[str, ...] | None) -> list[dict[str, Any]]:
    if instance_ids is None:
        return instances
    wanted = list(instance_ids)
    by_id = {str(require(instance, 'instance_id')): instance for instance in instances}
    missing = [iid for iid in wanted if iid not in by_id]
    if missing:
        raise ValueError('Missing source instance ids: ' + str(missing))
    return [by_id[iid] for iid in wanted]


def write_assets(instance: dict[str, Any], templates: dict[str, dict[str, Any]], output_root: Path, levels: tuple[str, ...]) -> list[Path]:
    written: list[Path] = []
    for level in levels:
        task = task_for_level(instance, templates, output_root, level)
        rule = build_rule_for_task(task, instance, level, templates)
        written.extend(write_task_rule_prompt(task, rule, output_root))
    return written


def generate_all_clean_assets(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    template_root: Path = DEFAULT_TEMPLATE_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    levels: tuple[str, ...] | list[str] | None = None,
    instance_ids: list[str] | tuple[str, ...] | None = None,
) -> list[Path]:
    selected_levels = normalize_levels(levels)
    templates = source_templates(template_root)
    clean_output_dirs(output_root)
    written: list[Path] = []
    for instance in select_instances(source_instances(source_root), instance_ids):
        written.extend(write_assets(instance, templates, output_root, selected_levels))
    return written


def generate_all_l1_assets(source_root: Path = DEFAULT_SOURCE_ROOT, output_root: Path = DEFAULT_OUTPUT_ROOT) -> list[Path]:
    return generate_all_clean_assets(source_root=source_root, output_root=output_root, levels=('level1',))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate Keyboard clean-pilot BASE assets.')
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument('--template-root', type=Path, default=DEFAULT_TEMPLATE_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--levels', nargs='+', choices=sorted(SUPPORTED_LEVELS), default=None)
    parser.add_argument('--instance-id', dest='instance_ids', action='append', default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    written = generate_all_clean_assets(
        source_root=args.source_root,
        template_root=args.template_root,
        output_root=args.output_root,
        levels=args.levels,
        instance_ids=args.instance_ids,
    )
    print('Wrote ' + str(len(written)) + ' files under ' + str(args.output_root))


if __name__ == '__main__':
    main()
