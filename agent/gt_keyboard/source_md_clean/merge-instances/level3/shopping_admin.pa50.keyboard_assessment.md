# Merge Instance

```yaml
instance_id: shopping_admin.pa50.keyboard_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA50
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Customer Order Count Report
  start_url: http://localhost:7780/admin/reports/report_customer/orders/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa50.datepicker_month_switch_not_keyboard_reachable
    target:
      selector: '#ui-datepicker-div .ui-datepicker-prev, #ui-datepicker-div .ui-datepicker-next'
      description: the previous and next month links in the opened Customer Orders datepicker
      coverage_policy: representative_group
    criterion:
      issue_family: keyboard_nonreachable
      wcag_target: WCAG 2.1.1 Keyboard
    evidence_rule: >-
      The target (the previous and next month links in the opened Customer Orders datepicker)
      is visible and pointer-operable or part of an active widget, but expected keyboard navigation
      cannot reach or complete operation of that same target. Reporting a different keyboard
      issue on the page does not satisfy this rule.
  - issue_id: shopping_admin.pa50.scope_select_context_change
    target:
      selector: button#store-change-button
      description: the All Websites scope selector button on the customer orders report
      coverage_policy: single
    criterion:
      issue_family: on_input
      wcag_target: WCAG 3.2.2 On Input
    evidence_rule: >-
      The target control (the All Websites scope selector button on the customer orders report)
      changes page context, navigation state, result ordering, or equivalent page state immediately
      after the control value or selection changes, without a separate submit or apply action
      and without prior warning. Merely opening a menu is not sufficient.
```

## Source And Live Check

- This L3 merge source is restricted to a BASE-induced page owner key.
- Completeness is scoped to reviewed Keyboard inventory on that page, not a new full-site audit.
- Current L3 scope is limited to the listed Keyboard assessment items.

## Merge Scope

- Owner key: shopping_admin + PA50 + Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6.
- gold.issues[] contains 2 reviewed issue entries.
