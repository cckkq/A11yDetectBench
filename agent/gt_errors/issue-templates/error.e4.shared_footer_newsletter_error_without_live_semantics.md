# Issue Template

- template_id: `error.e4.shared_footer_newsletter_error_without_live_semantics`
- template_name: `Shared footer newsletter error message has no live semantics`
- domain: `error`
- primary_wcag: `4.1.3 Status Messages`
- assessment_mapping: `E.4 Status Messages`
- pattern_summary: `An error message appears in the shared footer newsletter component, but the #newsletter-error path has no status or live-region semantics, so the same-page error is not automatically announced`

## Recognition Rule
- The page reuses the footer newsletter component and can trigger a real newsletter-input error.
- The error text is in `#newsletter-error` or the corresponding shared error node.
- The error node and its ancestors lack `role="alert"`, `role="status"`, `role="log"`, or `aria-live`.
- Even if another valid success message exists, the page-level E.4 result is FAIL when this newsletter error is not programmatically exposed.

## Boundary Rule
- Use only for pages where reuse of the footer newsletter component has been manually confirmed; do not extrapolate the template.
- Exclude page-local error scenes that are not shared newsletter messages.
- Exclude records that establish only an ordinary content change and do not confirm the newsletter error path.

## Canonical Examples
- `shopping.p01.e4.shared_footer_newsletter_error_without_live_semantics`
- `shopping.p07.e4.shared_footer_newsletter_error_without_live_semantics`
