# Merge Instance

```yaml
instance_id: shopping_admin.pa08.keyboard_nonreachable
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA08
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Billing Agreements
  start_url: http://localhost:7780/admin/paypal/billing_agreement/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
  assessment_requirement: 1.1 Keyboard navigation
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa08.datepicker_month_switch_not_keyboard_reachable
    target:
      selector: '#ui-datepicker-div .ui-datepicker-prev, #ui-datepicker-div .ui-datepicker-next'
      description: the previous and next month links in the opened Billing Agreements datepicker
      coverage_policy: representative_group
    criterion:
      issue_family: keyboard_nonreachable
      wcag_target: WCAG 2.1.1 Keyboard
    evidence_rule: >-
      The target (the previous and next month links in the opened Billing Agreements datepicker)
      is visible and pointer-operable or part of an active widget, but expected keyboard navigation
      cannot reach or complete operation of that same target. Reporting a different keyboard
      issue on the page does not satisfy this rule.
```

## Source And Live Check

- This L2 merge source is restricted to a BASE-induced page/family owner key.
- Completeness is scoped to reviewed Keyboard inventory inside that owner key, not a new full-site audit.
- No BASE-external page or page/family owner is introduced here.

## Merge Scope

- Owner key: shopping_admin + PA08 + keyboard_nonreachable + WCAG 2.1.1 Keyboard.
- gold.issues[] contains 1 reviewed issue entries.
