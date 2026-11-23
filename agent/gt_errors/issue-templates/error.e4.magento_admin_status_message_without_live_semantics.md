# Issue Template

- template_id: `error.e4.magento_admin_status_message_without_live_semantics`
- template_name: `Magento admin status-message container has no live semantics`
- domain: `error`
- primary_wcag: `4.1.3 Status Messages`
- assessment_mapping: `E.4 Status Messages`
- pattern_summary: `A success, warning, or error message appears in Magento admin, but the .message.message-* or #messages path has no status or live-region semantics`

## Recognition Rule
- After a user action, a success, warning, or error message appears on the same page.
- The message belongs to a Magento admin `.message.message-success`, `.message.message-warning`, `.message.message-error`, or `#messages` path.
- The message node and its ancestors lack `role="alert"`, `role="status"`, `role="log"`, or `aria-live`.
- The message communicates a result without taking focus, so it is a 4.1.3 status-message scene.

## Boundary Rule
- Exclude ordinary grid-result text such as `0 records found` or `We couldn't find any records.`
- Exclude an `Attention` dialog or confirmation dialog that takes focus.
- The `Please wait...` loading-mask family belongs to the progress template instead.

## Canonical Examples
- `shopping_admin.pa03.e4.magento_admin_status_message_without_live_semantics`
- `shopping_admin.pa66.e4.magento_admin_status_message_without_live_semantics`
