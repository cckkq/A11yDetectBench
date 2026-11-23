from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from agent.gt_focus.generate_clean_assets import (
    DEFAULT_TEMPLATE_ROOT,
    GT_FOCUS_DIR,
    clean_output_dirs,
    criterion_for,
    dump_yaml,
    optional,
    output_dirs,
    require,
    source_instances,
    source_templates,
    write_task_rule_prompt,
)
from agent.gt_focus.generate_clean_assets import build_l1_task as build_base_l1_task


DEFAULT_SOURCE_ROOT = GT_FOCUS_DIR / 'source_md_clean' / 'pass-instances'
DEFAULT_OUTPUT_ROOT = GT_FOCUS_DIR / 'generated_clean_pilot' / 'generated_pass'
SUPPORTED_FAMILIES = {'visible_focus', 'revealing_content'}


def validate_pass(instance: dict[str, Any]) -> None:
    iid = str(require(instance, 'instance_id'))
    if require(instance, 'issue_present') is not False:
        raise ValueError('PASS requires issue_present false: ' + iid)
    if require(instance, 'gold.expected_verdict') != 'no_issue_found':
        raise ValueError('PASS requires expected_verdict no_issue_found: ' + iid)
    if require(instance, 'source.matched_positive') != iid:
        raise ValueError('PASS source.matched_positive must equal instance_id: ' + iid)
    family = str(require(instance, 'criterion.issue_family'))
    if family not in SUPPORTED_FAMILIES:
        raise ValueError('Unsupported Focus PASS issue_family: ' + family)


def build_l1_task(
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    output_root: Path,
) -> dict[str, Any]:
    validate_pass(instance)
    return build_base_l1_task(instance, templates, output_root)


def build_l1_rule(
    task: dict[str, Any],
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    validate_pass(instance)
    criterion = criterion_for(instance, templates)
    return {
        'task_id': task['task_id'],
        'instance_id': str(require(instance, 'instance_id')),
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
            'issue_type': [require(criterion, 'wcag_target'), require(instance, 'template_id')],
            'target': require(instance, 'target'),
            'criterion': criterion,
            'evidence_rule': require(instance, 'gold.evidence_rule'),
        },
        'evaluation_logic': [
            'Verdict must be exactly no_issue_found for the matched PASS target.',
            'Target may use a different locator, but it must resolve to the same DOM or accessibility target as the gold selector.',
            'A reported focus issue on this clean target is a false alarm for this task.',
            'Reporting unrelated focus issues does not count for this task.',
        ],
    }


def write_assets(
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    output_root: Path,
) -> list[Path]:
    task = build_l1_task(instance, templates, output_root)
    rule = build_l1_rule(task, instance, templates)
    return write_task_rule_prompt(task, rule, output_root)


def generate_all_pass_assets(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    template_root: Path = DEFAULT_TEMPLATE_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> list[Path]:
    templates = source_templates(template_root)
    clean_output_dirs(output_root)
    written: list[Path] = []
    for instance in source_instances(source_root):
        written.extend(write_assets(instance, templates, output_root))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate FOCUS PASS-L1 clean-pilot assets.')
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument('--template-root', type=Path, default=DEFAULT_TEMPLATE_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    written = generate_all_pass_assets(
        source_root=args.source_root,
        template_root=args.template_root,
        output_root=args.output_root,
    )
    print('Wrote ' + str(len(written)) + ' files under ' + str(args.output_root))


if __name__ == '__main__':
    main()
