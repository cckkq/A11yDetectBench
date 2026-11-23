# Issue Instance

```yaml
instance_id: shopping.p02.lp.order_reorder_without_row_header_context
template_id: links.link_purpose.shopping.order_reorder_without_row_header_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P02

page:
  site: shopping
  page_name: Order History
  start_url: http://localhost:7770/sales/order/history/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'table#my-orders-table a.action.order'
  description: the repeated Reorder anchor elements in the order history table
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links are named only Reorder. The action cell is associated
    with the Action column header, but the order number is an ordinary sibling
    data cell and is not linked through row headers, headers/id, or ARIA.
```

## Selector Check

- After logging into Shopping, the `target.selector` value resolves to ten visible elements on P02.
- The matched anchor elements have text `Reorder`, class `action order`, `href="#"`, and `data-post` values for different `/sales/order/reorder/order_id/.../` targets.
