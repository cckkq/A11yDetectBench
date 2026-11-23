#!/usr/bin/env python3
'''Generate runnable Links clean-pilot assets from the clean manifest.'''

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

import yaml

from agent.gt_links.run_task import build_task_prompt, load_task


GT_LINKS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_LINKS_DIR.parent.parent
DEFAULT_MANIFEST = GT_LINKS_DIR / 'generated_clean_pilot' / 'manifest' / 'links_manifest_v0_1_clean.yaml'
DEFAULT_OUTPUT_ROOT = GT_LINKS_DIR / 'generated_clean_pilot' / 'generated'

DESTRUCTIVE_SETUP = 'Do not complete confirmation dialogs or submit changes.'


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


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    data = yaml.safe_load(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'Manifest root must be a mapping: {manifest_path}')
    return data


def template_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    templates = manifest.get('templates')
    if not isinstance(templates, list) or not all(isinstance(item, dict) for item in templates):
        raise ValueError('manifest templates must be a list of mappings')
    result = {require(template, 'template_id'): template for template in templates}
    if len(result) != len(templates):
        raise ValueError('Duplicate template_id in clean manifest')
    return result


def manifest_instances(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    items = manifest.get('instances')
    if not isinstance(items, list) or not items:
        raise ValueError('manifest instances must be a non-empty list')
    if not all(isinstance(item, dict) for item in items):
        raise ValueError('manifest instances must be mappings')
    ids = [require(item, 'instance_id') for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate instance_id in clean manifest')
    return items


def template_for_instance(instance: dict[str, Any], templates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    template_id = require(instance, 'template_id')
    template = templates.get(template_id)
    if template is None:
        raise ValueError(f'Missing template for {require(instance, "instance_id")}')
    return template


def criterion_for(instance: dict[str, Any], templates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    template = template_for_instance(instance, templates)
    criterion = require(template, 'criterion')
    if require(instance, 'criterion.issue_family') != require(criterion, 'issue_family'):
        raise ValueError(f'issue_family mismatch for {require(instance, "instance_id")}')
    if require(instance, 'criterion.wcag_target') != require(criterion, 'wcag_target'):
        raise ValueError(f'wcag_target mismatch for {require(instance, "instance_id")}')
    return criterion


def family_for(instance: dict[str, Any], templates: dict[str, dict[str, Any]]) -> str:
    family = require(criterion_for(instance, templates), 'issue_family')
    if family not in {'link_function', 'link_purpose'}:
        raise ValueError(f'Unsupported issue_family {family}: {require(instance, "instance_id")}')
    return str(family)


def task_criterion_fields(instance: dict[str, Any], templates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    criterion = criterion_for(instance, templates)
    return {
        'wcag_target': require(criterion, 'wcag_target'),
        'wcag_source_url': require(criterion, 'wcag.url'),
        'wcag_clause_text': require(criterion, 'wcag.criterion_text'),
        'ai_web': require(criterion, 'ai_web'),
    }


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


def rule_file_for_task(task_id: str, output_root: Path, *, level1: bool = False) -> str:
    name = f'{task_id}.yaml'
    if level1:
        name = name.replace('.verify.v1.yaml', '.verify.shared.v1.yaml')
    return display_path(output_root / 'evaluate-rules' / name)


def single_output_format(family: str) -> dict[str, Any]:
    return {
        'verdict': 'issue_found | no_issue_found',
        'selector': 'verified CSS selector for the reported anchor, or empty string',
        'target': 'natural-language target description',
        'issue_type': family,
        'observed_behavior': 'concise description of the observed link behavior or accessible-name/context problem',
        'evidence': 'concrete DOM, AX, or interaction facts supporting the issue',
    }


def multi_output_format(family: str | None = None) -> dict[str, Any]:
    return {
        'verdict': 'issue_found | no_issue_found',
        'issues': [
            {
                'selector': 'verified CSS selector for the reported anchor, or empty string',
                'target': 'natural-language target description',
                'issue_type': family if family else 'link_function | link_purpose',
                'observed_behavior': 'concise description of the observed link behavior or accessible-name/context problem',
                'evidence': 'concrete DOM, AX, or interaction facts supporting the issue',
            }
        ],
    }


def safety_setup(instance: dict[str, Any]) -> str | None:
    explicit = optional(instance, 'setup')
    if explicit:
        return str(explicit)
    text = ' '.join(
        str(part)
        for part in [
            optional(instance, 'target.description'),
            optional(instance, 'target.selector'),
        ]
        if part
    ).lower()
    if any(token in text for token in ['confirmation', 'submit', 'remove', 'delete', 'unassign']):
        return DESTRUCTIVE_SETUP
    return None


def build_l1_task(
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    output_root: Path,
) -> dict[str, Any]:
    iid = require(instance, 'instance_id')
    family = family_for(instance, templates)
    task_id = f'{iid}.verify.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root, level1=True),
        'difficulty': 'level_1_direct_verification',
        'issue_domain': 'links',
        'issue_family': family,
        **task_criterion_fields(instance, templates),
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': require(instance, 'page.auth_state_file'),
        'target_description': require(instance, 'target.description'),
        'setup': safety_setup(instance),
        'output_format': single_output_format(family),
        'target_selector': require(instance, 'target.selector'),
    }


def build_l2_task(
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    output_root: Path,
) -> dict[str, Any]:
    iid = require(instance, 'instance_id')
    family = family_for(instance, templates)
    task_id = f'{iid}.verify.level2.v1'
    return {
        'task_id': task_id,
        'instance_id': iid,
        'task_type': 'verification',
        'evaluate_rule_file': rule_file_for_task(task_id, output_root),
        'difficulty': 'level_2_clause_given_location_hidden',
        'issue_domain': 'links',
        'issue_family': family,
        **task_criterion_fields(instance, templates),
        'modality_policy': 'unrestricted_detection',
        'start_url': require(instance, 'page.start_url'),
        'auth_state_file': require(instance, 'page.auth_state_file'),
        'target_description': 'any anchor on this page',
        'setup': safety_setup(instance),
        'output_format': multi_output_format(family),
    }


def l3_wcag_criteria(templates: dict[str, dict[str, Any]]) -> dict[str, dict[str, str]]:
    by_label: dict[str, dict[str, str]] = {}
    for template in templates.values():
        criterion = require(template, 'criterion')
        label = require(criterion, 'assessment_requirement')
        by_label[label] = {
            'target': require(criterion, 'wcag_target'),
            'text': require(criterion, 'wcag.criterion_text'),
            'url': require(criterion, 'wcag.url'),
        }
    return {key: by_label[key] for key in sorted(by_label)}


def build_l3_task(
    instance: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    output_root: Path,
) -> dict[str, Any]:
    iid = require(instance, 'instance_id')
    task_id = f'{iid}.verify.level3.v1'
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
        'target_description': 'link-role elements within Links assessment scope L.1-L.2 on this page',
        'setup': safety_setup(instance),
        'wcag_criteria': l3_wcag_criteria(templates),
        'output_format': multi_output_format(),
    }


def source_record(instance: dict[str, Any]) -> dict[str, Any]:
    source = {
        'record_file': require(instance, 'source.record_file'),
        'page_id': require(instance, 'source.page_id'),
    }
    legacy_id = optional(instance, 'source.legacy_instance_id')
    if legacy_id:
        source['legacy_instance_id'] = legacy_id
    split = optional(instance, 'source.split_from_legacy_group')
    if split is not None:
        source['split_from_legacy_group'] = split
    return source


def page_record(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        'site': require(instance, 'page.site'),
        'page_name': require(instance, 'page.page_name'),
        'start_url': require(instance, 'page.start_url'),
    }


def target_record(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        'selector': require(instance, 'target.selector'),
        'description': require(instance, 'target.description'),
        'coverage_policy': require(instance, 'target.coverage_policy'),
    }


def build_rule(
    task: dict[str, Any],
    instance: dict[str, Any],
    level: str,
    templates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    criterion = criterion_for(instance, templates)
    return {
        'task_id': task['task_id'],
        'instance_id': require(instance, 'instance_id'),
        'task_level': level,
        'source': source_record(instance),
        'page': page_record(instance),
        'gold': {
            'issue_present': require(instance, 'issue_present'),
            'expected_verdict': require(instance, 'gold.expected_verdict'),
            'issue_type': [require(criterion, 'wcag_target'), require(instance, 'template_id')],
            'target': target_record(instance),
            'criterion': criterion,
            'evidence_rule': require(instance, 'gold.evidence_rule'),
        },
        'evaluation_logic': [
            'Verdict must be exactly correct.',
            'Target may use a different locator, but it must resolve to the same DOM or accessibility target as the gold selector.',
            'Behavior may use different wording, but it must satisfy the gold evidence rule.',
            'Reporting unrelated issues does not count for this task.',
        ],
    }


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(data), encoding='utf-8')


def write_task_rule_prompt(task: dict[str, Any], rule: dict[str, Any], output_root: Path) -> list[Path]:
    dirs = output_dirs(output_root)
    task_id = task['task_id']
    task_path = dirs['tasks'] / f'{task_id}.yaml'
    rule_path = dirs['rules'] / Path(task['evaluate_rule_file']).name
    prompt_path = dirs['prompts'] / f'{task_id}.task.prompt.txt'
    write_yaml(task_path, task)
    write_yaml(rule_path, rule)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(build_task_prompt(load_task(task_path)) + '\n', encoding='utf-8')
    return [task_path, rule_path, prompt_path]


def generate_all_clean_assets(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> list[Path]:
    manifest = load_manifest(manifest_path)
    templates = template_map(manifest)
    rows = sorted(manifest_instances(manifest), key=lambda item: require(item, 'instance_id'))
    clean_output_dirs(output_root)
    written: list[Path] = []
    for instance in rows:
        tasks = {
            'level1': build_l1_task(instance, templates, output_root),
            'level2': build_l2_task(instance, templates, output_root),
            'level3': build_l3_task(instance, templates, output_root),
        }
        for level, task in tasks.items():
            rule = build_rule(task, instance, level, templates)
            written.extend(write_task_rule_prompt(task, rule, output_root))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate Links clean-pilot assets.')
    parser.add_argument('--manifest-path', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    written = generate_all_clean_assets(manifest_path=args.manifest_path, output_root=args.output_root)
    print(f'wrote {len(written)} files under {args.output_root}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
