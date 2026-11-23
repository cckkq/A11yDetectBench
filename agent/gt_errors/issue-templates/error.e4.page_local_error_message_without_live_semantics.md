# Issue Template

- template_id: `error.e4.page_local_error_message_without_live_semantics`
- template_name: `Page-local error message appears without an automatically announced container`
- domain: `error`
- primary_wcag: `4.1.3 Status Messages`
- assessment_mapping: `E.4 Status Messages`
- pattern_summary: `A page-local error message is visibly present, but its node and ancestors lack status or live-region semantics, so assistive technology does not announce it`

## Recognition Rule
- After user interaction, page-local error text appears on the same page.
- The message is produced by the current interaction and is not shared-component or ordinary result content.
- The error node and its ancestors lack `role="alert"`, `role="status"`, `role="log"`, or `aria-live`.
- A live region elsewhere on the page cannot cover this actual page-local error message.

## Boundary Rule
- Exclude the shared footer newsletter family.
- Exclude the Magento admin `.message.message-*` container family.
- Exclude `Please wait...` and other progress/waiting scenes.
- Exclude a current canonical record that treats the feedback only as ordinary native validation or a form list rather than a separate E.4 scene.

## Canonical Examples
- `shopping.p06.e4.page_local_error_message_without_live_semantics`
- `shopping.p15.e4.page_local_error_message_without_live_semantics`
