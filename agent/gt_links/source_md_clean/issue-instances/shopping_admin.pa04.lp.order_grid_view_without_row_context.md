# Issue Instance

```yaml
instance_id: shopping_admin.pa04.lp.order_grid_view_without_row_context
template_id: links.link_purpose.shopping_admin.order_grid_view_without_row_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04

page:
  site: shopping_admin
  page_name: Orders
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: a.action-menu-item
  description: the `View` links in the Orders grid Action column
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links have computed AX name `View` and no description. Their
    action cells and associated column header only identify `Action`; order
    numbers and customer names are in sibling cells without row-header,
    headers/id, or ARIA association.
```

## Selector Check

- `document.querySelectorAll('a.action-menu-item')` resolves to 200 elements on PA04 after the Magento UI grid finishes binding.
- The matched elements have visible text `View`, no `aria-label`, and no `title`.
- The action cell text is only `View`, the associated column header is `Action`, and the order number/customer cells are ordinary sibling cells rather than programmatic link context.
