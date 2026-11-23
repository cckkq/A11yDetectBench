from __future__ import annotations

import base64
import inspect
import json
from pathlib import Path
from typing import Any


FOCUS_VLM_PROMPT = '''You are reviewing keyboard focus evidence for WCAG 2.4.7 Focus Visible.

For each item, compare the BEFORE crop and AFTER crop from the rendered page.
The AFTER crop was captured immediately after a real Tab key press. The target
region is the component that received keyboard focus or the keyboard-current
item associated with aria-activedescendant.

Decide whether a sighted keyboard user can perceive a focus indicator in the
AFTER crop. A valid indicator may be on the focused element itself, the
keyboard-current item, a visually tied parent/proxy, or nearby context that
clearly marks the current item. Examples include outline, border, glow, shadow,
underline, background change, or another clear visual change.

This is a candidate generator, not a final verdict. Set suspect=true when the
crop is clear and you cannot identify a user-perceivable focus indicator, or
when the only possible indicator is too unclear/subtle to be useful evidence.
Set suspect=false when a clear or reasonably perceivable indicator is visible.

Do not decide whether this is a confirmed accessibility violation. Return JSON
only in this shape:
{
  "result": [
    {
      "tab_index": 1,
      "visual_focus_indicator": "present|absent|uncertain",
      "indicator_location": "focused_element|keyboard_current_item|parent_or_proxy|nearby_context|none|unclear",
      "suspect": false,
      "confidence": "high|medium|low",
      "reason": "short visual evidence explanation"
    }
  ]
}

Use visual_focus_indicator="uncertain" only when the visual evidence is genuinely
ambiguous; it may still have suspect=true if no clear user-perceivable indicator
can be identified. Do not use the words violation, confirmed issue, should
report, or verdict.'''


def _image_url(path: str) -> dict[str, Any]:
    encoded = base64.b64encode(Path(path).read_bytes()).decode('ascii')
    return {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + encoded}}


def _responses_image(path: str) -> dict[str, Any]:
    encoded = base64.b64encode(Path(path).read_bytes()).decode('ascii')
    return {'type': 'input_image', 'image_url': 'data:image/png;base64,' + encoded}


def _observation_label(observation: dict[str, Any]) -> str:
    parts = [
        'tab_index=' + str(observation.get('tab_index')),
        'target_selector=' + str(observation.get('selector') or ''),
        'focus_owner_selector=' + str(observation.get('focus_owner_selector') or ''),
        'keyboard_current_source=' + str(observation.get('keyboard_current_source') or 'active_element'),
        'role=' + str(observation.get('role') or ''),
        'name=' + str(observation.get('ariaLabel') or observation.get('text') or observation.get('title') or ''),
    ]
    return ' | '.join(parts)


def build_focus_vlm_messages(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [{'type': 'text', 'text': FOCUS_VLM_PROMPT}]
    for observation in observations:
        tab_index = str(observation.get('tab_index'))
        content.append({'type': 'text', 'text': _observation_label(observation) + ' | BEFORE crop'})
        content.append(_image_url(str(observation['before_crop_path'])))
        content.append({'type': 'text', 'text': 'tab_index=' + tab_index + ' | AFTER crop'})
        content.append(_image_url(str(observation['after_crop_path'])))
    return [{'role': 'user', 'content': content}]


def build_focus_vlm_responses_input(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [{'type': 'input_text', 'text': FOCUS_VLM_PROMPT}]
    for observation in observations:
        tab_index = str(observation.get('tab_index'))
        content.append({'type': 'input_text', 'text': _observation_label(observation) + ' | BEFORE crop'})
        content.append(_responses_image(str(observation['before_crop_path'])))
        content.append({'type': 'input_text', 'text': 'tab_index=' + tab_index + ' | AFTER crop'})
        content.append(_responses_image(str(observation['after_crop_path'])))
    return [{'role': 'user', 'content': content}]


def _strip_json_fence(raw: str) -> str:
    text = (raw or '').strip()
    if text.startswith('```'):
        text = text.removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return text


def _bool_from_any(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    if text in {'true', 'yes', '1'}:
        return True
    if text in {'false', 'no', '0'}:
        return False
    return None


def parse_focus_vlm_response(raw: str) -> list[dict[str, Any]]:
    payload = json.loads(_strip_json_fence(raw))
    result = payload.get('result', [])
    parsed: list[dict[str, Any]] = []
    for item in result if isinstance(result, list) else []:
        indicator = str(item.get('visual_focus_indicator') or '').strip().lower()
        if indicator not in {'present', 'absent', 'uncertain'}:
            legacy_delta = str(item.get('visual_delta') or '').strip().lower()
            if legacy_delta in {'none_observed', 'no_clear_visual_delta', 'none'}:
                indicator = 'absent'
            elif legacy_delta in {'clear_indicator', 'visible_delta_observed', 'present'}:
                indicator = 'present'
            elif _bool_from_any(item.get('bug')) is True:
                indicator = 'absent'
            elif _bool_from_any(item.get('bug')) is False:
                indicator = 'present'
            else:
                indicator = 'uncertain'

        suspect_value = _bool_from_any(item.get('suspect'))
        legacy_bug = _bool_from_any(item.get('bug'))
        if suspect_value is not None:
            suspect = bool(suspect_value)
        elif legacy_bug is not None:
            suspect = bool(legacy_bug)
        else:
            suspect = indicator == 'absent'

        location = str(item.get('indicator_location') or '').strip().lower()
        if location not in {'focused_element', 'keyboard_current_item', 'parent_or_proxy', 'nearby_context', 'none', 'unclear'}:
            location = 'unclear' if indicator != 'absent' else 'none'
        confidence = str(item.get('confidence') or '').strip().lower()
        if confidence not in {'high', 'medium', 'low'}:
            confidence = 'medium'

        parsed.append({
            'tab_index': int(item.get('tab_index') if item.get('tab_index') is not None else item.get('index') or 0),
            'visual_focus_indicator': indicator,
            'indicator_location': location,
            'suspect': suspect,
            'confidence': confidence,
            'reason': str(item.get('reason') or ''),
        })
    return parsed


def _response_text(response: Any) -> str:
    output_text = getattr(response, 'output_text', None)
    if output_text:
        return str(output_text)
    chunks: list[str] = []
    for output in getattr(response, 'output', []) or []:
        for content in getattr(output, 'content', []) or []:
            text = getattr(content, 'text', None)
            if text:
                chunks.append(str(text))
    return ''.join(chunks)


def make_openai_focus_vlm_reviewer(
    client: Any,
    *,
    model: str = 'gpt-5.5-20260424',
    use_responses_api: bool = False,
    reasoning_effort: str | None = None,
    batch_size: int = 8,
):
    async def review(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        parsed: list[dict[str, Any]] = []
        effective_batch_size = max(1, int(batch_size or 1))
        for start in range(0, len(observations), effective_batch_size):
            batch = observations[start:start + effective_batch_size]
            if use_responses_api:
                kwargs: dict[str, Any] = {
                    'model': model,
                    'input': build_focus_vlm_responses_input(batch),
                }
                if reasoning_effort:
                    kwargs['reasoning'] = {'effort': reasoning_effort}
                response = client.responses.create(**kwargs)
                if inspect.isawaitable(response):
                    response = await response
                raw = _response_text(response)
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=build_focus_vlm_messages(batch),
                    response_format={'type': 'json_object'},
                )
                if inspect.isawaitable(response):
                    response = await response
                raw = response.choices[0].message.content or ''
            parsed.extend(parse_focus_vlm_response(raw))
        return parsed

    return review


def make_default_focus_vlm_reviewer(model: str):
    """Build a reviewer from a local OpenAI-compatible client.

    The submitted runs used an institutional multimodal route whose endpoint
    and credentials are not part of this double-anonymous artifact. Reviewers
    who want VLM-assisted focus-crop review can configure the standard OpenAI
    Python client through their local environment, or call
    `make_openai_focus_vlm_reviewer` with their own compatible client.
    """
    from openai import OpenAI

    try:
        client = OpenAI()
    except Exception as exc:  # pragma: no cover - depends on local env
        raise RuntimeError(
            'Focus VLM review requires a locally configured OpenAI-compatible '
            'client. Set the standard OpenAI environment variables, pass '
            '`--no-focus-vlm`, or inject a reviewer with '
            '`make_openai_focus_vlm_reviewer`.'
        ) from exc
    return make_openai_focus_vlm_reviewer(client, model=model)
