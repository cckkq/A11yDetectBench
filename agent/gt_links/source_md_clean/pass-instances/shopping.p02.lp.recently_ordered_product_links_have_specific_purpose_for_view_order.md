# PASS Instance

```yaml
instance_id: shopping.p02.lp.recently_ordered_product_links_have_specific_purpose_for_view_order
template_id: links.link_purpose.pass.shopping.recently_ordered_product_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P02
  matched_positive: shopping.p02.lp.order_view_order_without_row_header_context

page:
  site: shopping
  page_name: Order History
  start_url: http://localhost:7770/sales/order/history/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.block-reorder a.product-item-link'
  description: the product-name links in the Recently Ordered block
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched links have visible product names and hrefs pointing to the
    corresponding product detail pages. Each link name identifies the target
    product, so the Link Purpose issue is not present for this target.
```

## Selector Check

- The selector targets visible product-name links in the Recently Ordered block on P02.
- This target is different from the repeated `View Order` positive target in the orders table.
