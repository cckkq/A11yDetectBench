# PASS Instance

```yaml
instance_id: shopping.p03.lp.recently_ordered_product_links_have_specific_purpose
template_id: links.link_purpose.pass.shopping.recently_ordered_product_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P03
  matched_positive: shopping.p03.lp.generic_view_all_without_programmatic_context

page:
  site: shopping
  page_name: Downloadable Products
  start_url: http://localhost:7770/downloadable/customer/products/
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
    The matched anchor elements have visible product names and hrefs pointing to the
    corresponding product detail pages. Each link name identifies the target
    product, so the Link Purpose issue is not present for this target.
```

## Selector Check

- The selector targets visible product-name anchor elements in the same Recently Ordered block as `.block-reorder a.action.view` on P03.
- These anchor elements are different DOM targets from the `View All` positive target.
