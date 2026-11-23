# Issue Instance

```yaml
instance_id: shopping_admin.pa62.lp.source_grid_edit_without_row_context
template_id: links.link_purpose.shopping_admin.source_grid_edit_without_row_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA62

page:
  site: shopping_admin
  page_name: Sources
  start_url: http://localhost:7780/admin/inventory/source/index/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: a.action-menu-item
  description: the `Edit` link in the inventory Sources grid Action column
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link has computed AX name `Edit` and no description. Its action
    cell and associated column header only identify `Action`; the source code
    and source name are in sibling cells without row-header, headers/id, or ARIA
    association.
```

## Selector Check

- `document.querySelectorAll('a.action-menu-item')` resolves to one element on PA62.
- The matched element has visible text `Edit`, no `aria-label`, no `title`, and href ending in `/source_code/default/`.
- The action cell text is only `Edit`, the associated column header is `Action`, and `default Default Source` is ordinary sibling-cell text rather than programmatic link context.
