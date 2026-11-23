# Issue Template

- template_id: `error.e4.field_level_error_text_without_live_semantics`
- template_name: `Field-level error text appears without live semantics`
- domain: `error`
- primary_wcag: `4.1.3 Status Messages`
- assessment_mapping: `E.4 Status Messages`
- pattern_summary: `Field-level error text appears in the same page and conveys error/status information, but its node and ancestors have no role or aria-live semantics, so assistive technology cannot perceive it without focus being moved`

## Recognition Rule
- After user interaction, field-level error text appears on the same page or changes from hidden to active user-facing text.
- The text conveys error/status information for the current interaction rather than static help text.
- The text node and its ancestors lack `role="alert"`, `role="status"`, `role="log"`, or `aria-live`.
- A separate valid alert/status message cannot cover this worse status/error message scene.

## Boundary Rule
- Exclude a control with only an invalid state and no actual user-facing error text.
- Exclude error text already placed in a visible `role="alert"` or live region.
- Exclude ordinary result refreshes, empty-state text, or filter changes unless they first qualify as a status message.

## Canonical Examples
- `gitlab.gl11.e4.field_level_error_text_without_live_semantics`
- `gitlab.gl44.e4.field_level_error_text_without_live_semantics`
