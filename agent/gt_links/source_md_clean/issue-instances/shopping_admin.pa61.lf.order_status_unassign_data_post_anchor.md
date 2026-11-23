# Issue Instance

```yaml
instance_id: shopping_admin.pa61.lf.order_status_unassign_data_post_anchor
template_id: links.link_function.shopping_admin.order_status_unassign_data_post_anchor
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA61

page:
  site: shopping_admin
  page_name: Order Status
  start_url: http://localhost:7780/admin/sales/order_status/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'a[href="#"][data-post*="unassign"]'
  description: the Unassign command anchor elements in the order status grid
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched anchor elements are exposed as links with `href="#"`, but their
    `data-post` payload submits `/admin/sales/order_status/unassign/` commands
    for status/state pairs. They do not navigate to link content and do not
    expose a button or command role.
```

## Selector Check

- After logging into Shopping Admin, the `target.selector` value resolves to ten visible elements on PA61.
- The matched anchor elements have text `Unassign` and `data-post` payloads for different order status/state pairs.
