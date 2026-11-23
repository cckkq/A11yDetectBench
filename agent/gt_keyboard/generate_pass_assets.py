from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from typing import Any

from agent.gt_keyboard.generate_clean_assets import (
    DEFAULT_TEMPLATE_ROOT,
    GT_KEYBOARD_DIR,
    clean_output_dirs,
    criterion_for,
    dump_yaml,
    optional,
    output_dirs,
    parse_source_md,
    require,
    source_instances,
    source_templates,
    write_task_rule_prompt,
)
from agent.gt_keyboard.generate_clean_assets import build_l1_task as build_base_l1_task
from agent.gt_keyboard.run_task import PASS_L1_PATCH_MANIFEST, load_yaml


DEFAULT_BASE_SOURCE_ROOT = GT_KEYBOARD_DIR / 'source_md_clean' / 'issue-instances'
DEFAULT_SOURCE_ROOT = GT_KEYBOARD_DIR / 'source_md_clean' / 'pass-instances'
DEFAULT_OUTPUT_ROOT = GT_KEYBOARD_DIR / 'generated_clean_pilot' / 'generated_pass'
SUPPORTED_FAMILIES = {'keyboard_nonreachable', 'on_input', 'character_key_shortcuts'}


def runtime_patch_ids() -> set[str]:
    if not PASS_L1_PATCH_MANIFEST.exists():
        raise FileNotFoundError('Keyboard PASS L1 runtime patch manifest not found: ' + str(PASS_L1_PATCH_MANIFEST))
    manifest = load_yaml(PASS_L1_PATCH_MANIFEST)
    patches = manifest.get('patches')
    if not isinstance(patches, dict):
        raise ValueError('patches must be a mapping: ' + str(PASS_L1_PATCH_MANIFEST))
    return {str(key) for key in patches}


def pass_instance_from_base(base: dict[str, Any]) -> dict[str, Any]:
    iid = str(require(base, 'instance_id'))
    instance = deepcopy(base)
    instance['issue_present'] = False
    source = dict(require(instance, 'source'))
    source['matched_positive'] = iid
    instance['source'] = source
    gold = dict(require(instance, 'gold'))
    gold['expected_verdict'] = 'no_issue_found'
    gold['evidence_rule'] = (
        'Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected '
        'to remove the reviewed keyboard failure while keeping the same page, setup, target '
        'selector, and criterion. A reported keyboard issue on this matched clean target is '
        'a false alarm for this task.'
    )
    instance['gold'] = gold
    return instance


def write_pass_source_md(instance: dict[str, Any], path: Path) -> None:
    iid = str(require(instance, 'instance_id'))
    text = (
        '# PASS Instance\n\n'
        '```yaml\n'
        + dump_yaml(instance)
        + '```\n\n'
        '## Selector Check\n\n'
        '- This PASS L1 instance is counterfactually derived from BASE L1 `' + iid + '`.\n'
        '- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.\n'
        '- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def generate_pass_source_instances(
    base_source_root: Path = DEFAULT_BASE_SOURCE_ROOT,
    output_source_root: Path = DEFAULT_SOURCE_ROOT,
) -> list[Path]:
    patch_ids = runtime_patch_ids()
    base_instances = source_instances(base_source_root)
    base_ids = {str(require(instance, 'instance_id')) for instance in base_instances}
    missing_patches = sorted(base_ids - patch_ids)
    extra_patches = sorted(patch_ids - base_ids)
    if missing_patches:
        raise ValueError('Missing Keyboard PASS L1 runtime patches: ' + str(missing_patches))
    if extra_patches:
        raise ValueError('Runtime patch manifest contains ids outside BASE L1 source set: ' + str(extra_patches))

    output_source_root.mkdir(parents=True, exist_ok=True)
    for old in output_source_root.glob('*.md'):
        old.unlink()

    written: list[Path] = []
    for base in base_instances:
        instance = pass_instance_from_base(base)
        path = output_source_root / (str(require(instance, 'instance_id')) + '.md')
        write_pass_source_md(instance, path)
        written.append(path)
    return written


def pass_source_instances(source_root: Path) -> list[dict[str, Any]]:
    paths = sorted(source_root.glob('*.md'))
    if not paths:
        raise ValueError('No Keyboard PASS source markdown files found: ' + str(source_root))
    items = [parse_source_md(path) for path in paths]
    ids = [require(item, 'instance_id') for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate instance_id in keyboard pass source md')
    return items


def validate_pass(instance: dict[str, Any], templates: dict[str, dict[str, Any]], patch_ids: set[str]) -> None:
    iid = str(require(instance, 'instance_id'))
    if iid not in patch_ids:
        raise ValueError('Missing Keyboard PASS L1 runtime patch for ' + iid)
    if require(instance, 'issue_present') is not False:
        raise ValueError('PASS requires issue_present false: ' + iid)
    if require(instance, 'gold.expected_verdict') != 'no_issue_found':
        raise ValueError('PASS requires expected_verdict no_issue_found: ' + iid)
    if require(instance, 'source.matched_positive') != iid:
        raise ValueError('PASS source.matched_positive must equal instance_id: ' + iid)
    family = str(require(criterion_for(instance, templates), 'issue_family'))
    if family not in SUPPORTED_FAMILIES:
        raise ValueError('Unsupported Keyboard PASS issue_family: ' + family)
    require(instance, 'target.selector')


def build_l1_task(
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    output_root: Path,
    patch_ids: set[str],
) -> dict[str, Any]:
    validate_pass(instance, templates, patch_ids)
    return build_base_l1_task(instance, templates, output_root)


def build_l1_rule(
    task: dict[str, Any],
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    patch_ids: set[str],
) -> dict[str, Any]:
    validate_pass(instance, templates, patch_ids)
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
            'A reported keyboard issue on this clean target is a false alarm for this task.',
            'Reporting unrelated keyboard issues does not count for this task.',
        ],
    }


def write_assets(
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    output_root: Path,
    patch_ids: set[str],
) -> list[Path]:
    task = build_l1_task(instance, templates, output_root, patch_ids)
    rule = build_l1_rule(task, instance, templates, patch_ids)
    return write_task_rule_prompt(task, rule, output_root)


def generate_all_pass_assets(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    template_root: Path = DEFAULT_TEMPLATE_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    regenerate_source: bool = True,
    base_source_root: Path = DEFAULT_BASE_SOURCE_ROOT,
) -> list[Path]:
    if regenerate_source:
        generate_pass_source_instances(base_source_root=base_source_root, output_source_root=source_root)
    templates = source_templates(template_root)
    patch_ids = runtime_patch_ids()
    clean_output_dirs(output_root)
    written: list[Path] = []
    for instance in pass_source_instances(source_root):
        written.extend(write_assets(instance, templates, output_root, patch_ids))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate Keyboard PASS-L1 clean-pilot assets.')
    parser.add_argument('--base-source-root', type=Path, default=DEFAULT_BASE_SOURCE_ROOT)
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument('--template-root', type=Path, default=DEFAULT_TEMPLATE_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--no-regenerate-source', action='store_true')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    written = generate_all_pass_assets(
        source_root=args.source_root,
        template_root=args.template_root,
        output_root=args.output_root,
        regenerate_source=not args.no_regenerate_source,
        base_source_root=args.base_source_root,
    )
    print('Wrote ' + str(len(written)) + ' files under ' + str(args.output_root))


if __name__ == '__main__':
    main()
