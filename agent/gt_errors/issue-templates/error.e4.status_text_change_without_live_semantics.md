# Issue Template

- template_id: `error.e4.status_text_change_without_live_semantics`
- template_name: `Status text changes on the same page without live semantics`
- domain: `error`
- primary_wcag: `4.1.3 Status Messages`
- assessment_mapping: `E.4 Status Messages`
- pattern_summary: `Local success, error, or status text updates in place, but its container is not a live region, so assistive technology is not informed of the status change`

## Recognition Rule
- Success, error, or validation status text updates in the same context.
- The changed text is a status message for the current interaction rather than ordinary content reflow.
- The text node and its ancestors lack `role="alert"`, `role="status"`, `role="log"`, or `aria-live`.
- A nearby empty or unrelated live region does not expose this status text.

## Boundary Rule
- Exclude dialog or alertdialog text that takes focus.
- Exclude success or failure text on a new page after navigation.
- Exclude a disabled state with no actual status-text change.

## Canonical Examples
- `gitlab.gl70.e4.status_text_change_without_live_semantics`
