import base64
import asyncio
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from agent.current_focus_marker import BoundingBox
from agent.evidence_assisted_observation import (
    EvidenceMarkerTarget,
    EvidencePack,
    MarkerResolution,
    append_evidence_pack_prompt,
    apply_evidence_screenshot_markers,
    apply_evidence_text_markers,
    build_evidence_pack_prompt_suffix,
    install_evidence_assisted_observation,
    load_evidence_pack_manifest,
)


def png_b64(width=100, height=100, color=(255, 255, 255)):
    image = Image.new('RGB', (width, height), color)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def decode_png(data):
    return Image.open(BytesIO(base64.b64decode(data))).convert('RGB')


class EvidencePackManifestTest(unittest.TestCase):
    def test_loads_manifest_as_binary_suspects_without_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'candidate-manifest.suspects.json'
            path.write_text(json.dumps({
                'task_id': 'gitlab.gl11.collapse_sidebar_not_tabbable.verify.level2.v1',
                'instance_id': 'gitlab.gl11.collapse_sidebar_not_tabbable',
                'family': 'keyboard_nonreachable',
                'suspect_candidates': [{
                    'marker_id': 'A11Y-K1',
                    'selector': 'aside .toggle-sidebar-button',
                    'text': 'Collapse sidebar',
                    'candidate_type': 'genuinely_not_observed_reached',
                }],
            }), encoding='utf-8')

            pack = load_evidence_pack_manifest(
                path,
                expected_task_id='gitlab.gl11.collapse_sidebar_not_tabbable.verify.level2.v1',
                expected_instance_id='gitlab.gl11.collapse_sidebar_not_tabbable',
                expected_family='keyboard_nonreachable',
            )

        self.assertEqual(pack.candidates[0].marker_id, 'A11Y-K1')
        self.assertEqual(pack.candidates[0].selector, 'aside .toggle-sidebar-button')
        self.assertIn('not observed in the Tab trace', pack.candidates[0].evidence)

    def test_rejects_task_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'candidate-manifest.suspects.json'
            path.write_text(json.dumps({
                'task_id': 'task.a',
                'instance_id': 'instance.a',
                'family': 'visible_focus',
                'suspect_candidates': [],
            }), encoding='utf-8')

            with self.assertRaisesRegex(ValueError, 'task_id mismatch'):
                load_evidence_pack_manifest(path, expected_task_id='task.b')


class EvidencePackPromptTest(unittest.TestCase):
    def test_prompt_suffix_is_compact_and_non_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'candidate-manifest.suspects.json'
            path.write_text(json.dumps({
                'task_id': 'shopping_admin.pa15.visible_focus.verify.level2.v1',
                'instance_id': 'shopping_admin.pa15.visible_focus',
                'family': 'visible_focus',
                'suspect_candidates': [{
                    'marker_id': 'A11Y-F1',
                    'selector': '#apply_rules',
                    'text': 'Apply Rules',
                    'tab_index': 18,
                    'why_included': 'long reason that should not be copied wholesale',
                }],
            }), encoding='utf-8')
            pack = load_evidence_pack_manifest(path)

        suffix = build_evidence_pack_prompt_suffix(pack)
        prompt = append_evidence_pack_prompt('Task body.', pack)

        self.assertIn('A11Y-F1: Apply Rules', suffix)
        self.assertIn('Tab stop 18', suffix)
        self.assertIn('not ranked', suffix)
        self.assertIn('Verify before reporting', prompt)
        for disallowed in ('confirmed', 'violation', 'FAIL', 'score', 'rank='):
            self.assertNotIn(disallowed, suffix)


class EvidenceMarkerTextTest(unittest.TestCase):
    def test_marks_dom_line_with_a11y_id_and_short_header(self):
        target = EvidenceMarkerTarget(
            marker_id='A11Y-K1',
            backend_node_id=40,
            summary='a role=button labeled Collapse sidebar',
            bbox=None,
            family='keyboard_nonreachable',
        )

        marked = apply_evidence_text_markers('[40]<a role=button>Collapse sidebar</a>', [target])

        self.assertIn('Evidence marker note:', marked)
        self.assertIn('A11Y-K1: [40] a role=button labeled Collapse sidebar', marked)
        self.assertIn('A11Y-K1 [40]<a role=button>Collapse sidebar</a>', marked)
        self.assertNotIn('verdict=true', marked)

    def test_coexists_with_current_focus_marker(self):
        target = EvidenceMarkerTarget(
            marker_id='A11Y-F1',
            backend_node_id=40,
            summary='button labeled Apply Rules',
            bbox=None,
            family='visible_focus',
        )

        marked = apply_evidence_text_markers('CURRENT_FOCUS [40]<button>Apply Rules</button>', [target])

        self.assertIn('A11Y-F1 CURRENT_FOCUS [40]<button>Apply Rules</button>', marked)


class EvidenceMarkerScreenshotTest(unittest.TestCase):
    def test_draws_non_page_marker_outside_bbox(self):
        original = png_b64()
        target = EvidenceMarkerTarget(
            marker_id='A11Y-F1',
            backend_node_id=40,
            summary='button labeled Apply Rules',
            bbox=BoundingBox(20, 20, 30, 20),
            family='visible_focus',
        )

        marked = apply_evidence_screenshot_markers(original, [target])

        self.assertNotEqual(marked, original)
        image = decode_png(marked)
        pixels = image.load()
        orange_pixels = [
            pixels[x, y]
            for x in range(image.width)
            for y in range(image.height)
            if pixels[x, y][0] > 200 and 100 < pixels[x, y][1] < 200 and pixels[x, y][2] < 80
        ]
        self.assertGreater(len(orange_pixels), 0)
        inside_pixels = [pixels[x, y] for x in range(20, 50) for y in range(20, 40)]
        self.assertTrue(all(not (pixel[0] > 200 and 100 < pixel[1] < 200 and pixel[2] < 80) for pixel in inside_pixels))


class EvidenceObservationWrapperTest(unittest.TestCase):
    def test_wrapper_forces_fresh_state_and_does_not_duplicate_marker_headers(self):
        class FakeDOMState:
            selector_map = {}

            def llm_representation(self, include_attributes=None):
                return '[40]<button>Apply Rules</button>'

        class FakeSession:
            def __init__(self):
                self.cached_values = []
                self.state = SimpleNamespace(dom_state=FakeDOMState(), screenshot=None)

            async def get_browser_state_summary(self, include_screenshot=True, cached=False, include_recent_events=False):
                self.cached_values.append(cached)
                return self.state

        pack = EvidencePack(
            path=Path('candidate-manifest.suspects.json'),
            task_id='task.a',
            instance_id='instance.a',
            family='visible_focus',
            candidates=(),
        )
        target = EvidenceMarkerTarget('A11Y-F1', 40, 'button labeled Apply Rules', None, 'visible_focus')
        session = FakeSession()
        install_evidence_assisted_observation(
            session,
            pack,
            target_resolver=lambda _session, _state, _pack: MarkerResolution(targets=(target,), debug={'resolved_count': 1}),
        )

        first = asyncio.run(session.get_browser_state_summary(cached=True))
        second = asyncio.run(session.get_browser_state_summary(cached=True))
        text = second.dom_state.llm_representation()

        self.assertEqual(session.cached_values, [False, False])
        self.assertEqual(text.count('Evidence marker note:'), 1)
        self.assertEqual(text.count('A11Y-F1 [40]'), 1)
        self.assertIn('A11Y-F1 [40]<button>Apply Rules</button>', first.dom_state.llm_representation())


if __name__ == '__main__':
    unittest.main()
