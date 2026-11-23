# Merge Instance

```yaml
instance_id: shopping_admin.admin_reports_report_sales_coupons.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA46
  review_status: source_and_live_checked

page:
  site: shopping_admin
  page_name: Coupons Report
  start_url: http://localhost:7780/admin/reports/report_sales/coupons/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa46.lp.tooltip_help_what_is_this_without_target_context
      target:
        selector: 'main#anchor-content a.admin__field-tooltip-action.action-help'
        description: the `What is this?` help link in the Coupons Report store-view switcher
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link has computed AX name `What is this?` and no description. Its title repeats the same generic text, and the surrounding tooltip container does not programmatically identify the scope or control that the help link explains.
```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA46 says the stable 6.2 failure is the `What is this?` scope help link.
- Fresh live PA46 probe found one visible `main#anchor-content a.admin__field-tooltip-action.action-help` link with text `What is this?`.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/reports/report_sales/coupons/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for PA46 link purpose.
