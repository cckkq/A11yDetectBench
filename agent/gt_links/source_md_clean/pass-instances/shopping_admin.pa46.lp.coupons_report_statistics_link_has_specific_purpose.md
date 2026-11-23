# PASS Instance

```yaml
instance_id: shopping_admin.pa46.lp.coupons_report_statistics_link_has_specific_purpose
template_id: links.link_purpose.pass.shopping_admin.coupons_report_statistics_link_has_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA46
  matched_positive: shopping_admin.pa46.lp.tooltip_help_what_is_this_without_target_context

page:
  site: shopping_admin
  page_name: Coupons Report
  start_url: http://localhost:7780/admin/reports/report_sales/coupons/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#anchor-content a[href*="/reports/report_statistics/"]'
  description: the statistics link in the Coupons Report page content
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element has visible text `statistics` and its href points to the
    report statistics page. The link text identifies the destination report
    area, so the Link Purpose issue is not present for this target.
```

## Selector Check

- The selector targets the visible `statistics` link in the Coupons Report page content on PA46.
- This target is different from the `What is this?` help-link positive target.
