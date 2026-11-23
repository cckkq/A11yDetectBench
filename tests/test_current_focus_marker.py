import asyncio
import base64
import unittest
from io import BytesIO
from types import SimpleNamespace

from PIL import Image

from agent.current_focus_marker import (
    BoundingBox,
    FocusMarkerTarget,
    apply_focus_screenshot_marker,
    apply_focus_text_marker,
    install_current_focus_marker,
)


def png_b64(width=100, height=100, color=(255, 255, 255)):
    image = Image.new('RGB', (width, height), color)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def decode_png(data):
    return Image.open(BytesIO(base64.b64decode(data))).convert('RGB')


class CurrentFocusMarkerTextTest(unittest.TestCase):
    def test_marks_current_focus_inline_with_compact_note(self):
        text = '\n'.join(
            [
                '[12]<a href="/projects">Projects</a>',
                '[40]<button id="sort-projects-dropdown" aria-label="Updated date" />',
                '[51]<input name="search" />',
            ]
        )
        target = FocusMarkerTarget(
            marker='CURRENT_FOCUS',
            backend_node_id=40,
            summary='button#sort-projects-dropdown labeled Updated date',
        )

        marked = apply_focus_text_marker(text, [target])

        self.assertIn('Current focus: [40] button#sort-projects-dropdown labeled Updated date', marked)
        self.assertIn('Focus marker note: artificial, not page UI or page-provided visible focus.', marked)
        self.assertIn('CURRENT_FOCUS [40]<button id="sort-projects-dropdown" aria-label="Updated date" />', marked)
        self.assertEqual(marked.count('CURRENT_FOCUS'), 1)
        for disallowed in ('computed style', 'bbox', 'tab trace', 'candidate', 'WCAG'):
            self.assertNotIn(disallowed, marked)

    def test_inline_marker_preserves_dom_tree_indentation(self):
        target = FocusMarkerTarget(marker='CURRENT_FOCUS', backend_node_id=40, summary='button#save labeled Save')

        marked = apply_focus_text_marker('  [40]<button id="save">Save</button>', [target])

        self.assertIn('  CURRENT_FOCUS [40]<button id="save">Save</button>', marked)

    def test_marks_keyboard_current_item_separately(self):
        text = '\n'.join(
            [
                '[12]<div role="listbox" aria-activedescendant="opt-34" />',
                '[34]<div id="opt-34" role="option">Updated date</div>',
            ]
        )
        targets = [
            FocusMarkerTarget(marker='CURRENT_FOCUS', backend_node_id=12, summary='listbox'),
            FocusMarkerTarget(marker='KEYBOARD_CURRENT', backend_node_id=34, summary='option#opt-34 labeled Updated date'),
        ]

        marked = apply_focus_text_marker(text, targets)

        self.assertIn('Current focus: [12] listbox', marked)
        self.assertIn('Keyboard-current item: [34] option#opt-34 labeled Updated date', marked)
        self.assertIn('CURRENT_FOCUS [12]<div role="listbox" aria-activedescendant="opt-34" />', marked)
        self.assertIn('KEYBOARD_CURRENT [34]<div id="opt-34" role="option">Updated date</div>', marked)

    def test_unlisted_focus_gets_no_inline_marker(self):
        text = '[40]<button id="sort-projects-dropdown" />'
        target = FocusMarkerTarget(
            marker='CURRENT_FOCUS',
            backend_node_id=None,
            summary='button#not-in-selector-map labeled Save',
        )

        marked = apply_focus_text_marker(text, [target])

        self.assertIn('Current focus: not listed (button#not-in-selector-map labeled Save)', marked)
        self.assertNotIn('CURRENT_FOCUS [40]', marked)


class CurrentFocusMarkerScreenshotTest(unittest.TestCase):
    def test_draws_marker_on_original_screenshot_slot_without_covering_bbox(self):
        original = png_b64()
        bbox = BoundingBox(x=20, y=20, width=30, height=20)

        marked = apply_focus_screenshot_marker(original, bbox)

        self.assertNotEqual(marked, original)
        image = decode_png(marked)
        self.assertEqual(image.size, (100, 100))

        pixels = image.load()
        magenta_pixels = [
            pixels[x, y]
            for x in range(image.width)
            for y in range(image.height)
            if pixels[x, y][0] > 180 and pixels[x, y][1] < 120 and pixels[x, y][2] > 180
        ]
        self.assertGreater(len(magenta_pixels), 0)
        inside_pixels = [pixels[x, y] for x in range(20, 50) for y in range(20, 40)]
        self.assertTrue(all(not (pixel[0] > 180 and pixel[1] < 120 and pixel[2] > 180) for pixel in inside_pixels))

    def test_invalid_screenshot_or_bbox_returns_original(self):
        original = png_b64()

        self.assertEqual(apply_focus_screenshot_marker('not-base64', BoundingBox(1, 1, 5, 5)), 'not-base64')
        self.assertEqual(apply_focus_screenshot_marker(original, BoundingBox(1, 1, 0, 5)), original)


class CurrentFocusMarkerWrapperTest(unittest.TestCase):
    def test_wrapper_marks_returned_state_from_existing_session_method(self):
        class FakeDOMState:
            _root = object()
            selector_map = {}

            def llm_representation(self, include_attributes=None):
                return '[40]<button id="save">Save</button>'

        class FakeSession:
            def __init__(self):
                self.calls = 0

            async def get_browser_state_summary(self, include_screenshot=True, cached=False, include_recent_events=False):
                self.calls += 1
                return SimpleNamespace(dom_state=FakeDOMState(), screenshot=None)

        session = FakeSession()
        install_current_focus_marker(
            session,
            focus_getter=lambda _session, _state: [
                FocusMarkerTarget(marker='CURRENT_FOCUS', backend_node_id=40, summary='button#save labeled Save')
            ],
        )

        state = asyncio.run(session.get_browser_state_summary())

        self.assertEqual(session.calls, 1)
        self.assertIn('CURRENT_FOCUS [40]<button id="save">Save</button>', state.dom_state.llm_representation())

    def test_wrapper_replaces_existing_marker_without_duplicating_headers(self):
        class FakeDOMState:
            _root = object()
            selector_map = {}

            def llm_representation(self, include_attributes=None):
                return '[40]<button id="save">Save</button>'

        class FakeSession:
            def __init__(self):
                self.state = SimpleNamespace(dom_state=FakeDOMState(), screenshot=None)

            async def get_browser_state_summary(self, include_screenshot=True, cached=False, include_recent_events=False):
                return self.state

        session = FakeSession()
        install_current_focus_marker(
            session,
            focus_getter=lambda _session, _state: [
                FocusMarkerTarget(marker='CURRENT_FOCUS', backend_node_id=40, summary='button#save labeled Save')
            ],
        )

        state = asyncio.run(session.get_browser_state_summary())
        state = asyncio.run(session.get_browser_state_summary(cached=True))
        text = state.dom_state.llm_representation()

        self.assertEqual(text.count('Focus marker note:'), 1)
        self.assertEqual(text.count('Current focus:'), 1)
        self.assertEqual(text.count('CURRENT_FOCUS'), 1)

    def test_wrapper_prefers_keyboard_current_item_for_screenshot_marker(self):
        class FakeDOMState:
            _root = object()
            selector_map = {}

            def llm_representation(self, include_attributes=None):
                return '[12]<div role="listbox" />\n[34]<div role="option">Updated date</div>'

        class FakeSession:
            async def get_browser_state_summary(self, include_screenshot=True, cached=False, include_recent_events=False):
                return SimpleNamespace(dom_state=FakeDOMState(), screenshot=png_b64())

        session = FakeSession()
        install_current_focus_marker(
            session,
            focus_getter=lambda _session, _state: [
                FocusMarkerTarget(marker='CURRENT_FOCUS', backend_node_id=12, summary='listbox', bbox=BoundingBox(5, 5, 10, 10)),
                FocusMarkerTarget(
                    marker='KEYBOARD_CURRENT',
                    backend_node_id=34,
                    summary='option labeled Updated date',
                    bbox=BoundingBox(60, 60, 10, 10),
                ),
            ],
        )

        state = asyncio.run(session.get_browser_state_summary())
        image = decode_png(state.screenshot)
        pixels = image.load()

        self.assertTrue(any(pixels[x, 54][0] > 180 and pixels[x, 54][1] < 120 and pixels[x, 54][2] > 180 for x in range(54, 78)))
        self.assertFalse(any(pixels[x, 0][0] > 180 and pixels[x, 0][1] < 120 and pixels[x, 0][2] > 180 for x in range(0, 25)))


class CurrentFocusMarkerRuntimeTargetTest(unittest.TestCase):
    def test_body_focus_without_listed_element_is_ignored(self):
        from agent.current_focus_marker import _target_from_payload

        target = _target_from_payload(
            {'exists': True, 'tag': 'body', 'id': '', 'role': '', 'label': '', 'rect': {'x': 0, 'y': 0, 'width': 100, 'height': 100}},
            backend_node_id=1,
            state=SimpleNamespace(dom_state=SimpleNamespace(selector_map={})),
            marker='CURRENT_FOCUS',
        )

        self.assertIsNone(target)

    def test_runtime_rect_is_scaled_by_device_pixel_ratio(self):
        from agent.current_focus_marker import _target_from_payload

        target = _target_from_payload(
            {
                'exists': True,
                'tag': 'button',
                'id': 'save',
                'role': '',
                'label': 'Save',
                'devicePixelRatio': 2,
                'rect': {'x': 10, 'y': 20, 'width': 30, 'height': 15},
            },
            backend_node_id=40,
            state=SimpleNamespace(dom_state=SimpleNamespace(selector_map={40: object()})),
            marker='CURRENT_FOCUS',
        )

        self.assertEqual(target.bbox, BoundingBox(20, 40, 60, 30))


if __name__ == '__main__':
    unittest.main()
