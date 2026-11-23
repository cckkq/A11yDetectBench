# Issue Template

- template_id: `error.e4.progress_scene_without_live_semantics`
- template_name: `Progress or waiting state appears without live semantics`
- domain: `error`
- primary_wcag: `4.1.3 Status Messages`
- assessment_mapping: `E.4 Status Messages`
- pattern_summary: `After a user action, a visible Please wait... or similar waiting/progress scene appears on the same page, but the loading-mask path has no status or live-region semantics`

## Recognition Rule
- After a user action, waiting or progress text such as `Please wait...` appears on the same page.
- The text is a non-focus progress/status scene rather than static decorative text.
- The loading-mask node and its ancestors lack `role="alert"`, `role="status"`, `role="log"`, or `aria-live`.
- No other live region actually carries this progress text for automatic announcement.

## Boundary Rule
- Exclude waiting or prompt text inside a dialog or modal that takes focus.
- Exclude static warning or loading text present at page load.
- Exclude ordinary no-results or filter-summary text.

## Canonical Examples
- `shopping_admin.pa19.e4.progress_scene_without_live_semantics`
- `shopping_admin.pa20.e4.progress_scene_without_live_semantics`
