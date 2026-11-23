# Issue Instance

```yaml
instance_id: shopping_admin.pa40.lp.product_reviews_show_reviews_without_row_context
template_id: links.link_purpose.shopping_admin.product_reviews_show_reviews_without_row_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA40

page:
  site: shopping_admin
  page_name: Product Reviews Report
  start_url: http://localhost:7780/admin/reports/report_review/product/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#gridProducts_table td.col-actions a'
  description: the `Show Reviews` links in the Product Reviews Report grid Action column
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links have computed AX name `Show Reviews` and no description.
    Their action cells and associated column header only identify `Action`; the
    product names are in sibling cells without row-header, headers/id, or ARIA
    association.
```

## Selector Check

- `document.querySelectorAll('#gridProducts_table td.col-actions a')` resolves to 20 elements on PA40.
- The matched elements have visible text `Show Reviews`, no `aria-label`, and no `title`.
- Their associated column header is `Action`, and product names such as `Erica Evercool Sports Bra` are ordinary sibling cells rather than programmatic link context.
