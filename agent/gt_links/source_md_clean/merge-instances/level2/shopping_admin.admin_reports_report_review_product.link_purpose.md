# Merge Instance

```yaml
instance_id: shopping_admin.admin_reports_report_review_product.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA40
  review_status: source_and_live_checked

page:
  site: shopping_admin
  page_name: Product Reviews Report
  start_url: http://localhost:7780/admin/reports/report_review/product/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa40.lp.product_reviews_show_reviews_without_row_context
      target:
        selector: '#gridProducts_table td.col-actions a'
        description: the `Show Reviews` links in the Product Reviews Report grid Action column
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links have computed AX name `Show Reviews` and no description. Their action cells and associated column header only identify `Action`; product names are in sibling cells without row-header, headers/id, or ARIA association.
```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA40 says the stable 6.2 failure group is the Product Reviews Report grid `Show Reviews` action links.
- Fresh live PA40 probe found 20 visible `#gridProducts_table td.col-actions a` links with text `Show Reviews`.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/reports/report_review/product/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for PA40 link purpose.
