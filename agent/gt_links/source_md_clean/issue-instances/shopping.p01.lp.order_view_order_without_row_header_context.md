# Issue Instance

```yaml
instance_id: shopping.p01.lp.order_view_order_without_row_header_context
template_id: links.link_purpose.shopping.order_view_order_without_row_header_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P01

page:
  site: shopping
  page_name: Customer Account
  start_url: http://localhost:7770/customer/account/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'table#my-orders-table a.action.view'
  description: the repeated View Order anchor elements in the customer account recent-orders table
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links are named only View Order. The action cell is associated
    with the Action column header, but the order number is an ordinary sibling
    data cell and is not linked through row headers, headers/id, or ARIA.
```

## Selector Check

- After logging into Shopping, the `target.selector` value resolves to five visible elements on P01.
- The matched anchor elements have text `View Order`, class `action view`, and hrefs for different `/sales/order/view/order_id/.../` targets.
