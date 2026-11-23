# PASS Instance

```yaml
instance_id: shopping_admin.pa08.datepicker_month_switch_not_keyboard_reachable
template_id: keyboard.keyboard_nonreachable.datepicker_month_switch_not_keyboard_reachable
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
    agent/gt/issue-instances/shopping_admin.pa08.datepicker_month_switch_not_keyboard_reachable.md
  page_id: PA08
  matched_positive: shopping_admin.pa08.datepicker_month_switch_not_keyboard_reachable
page:
  site: shopping_admin
  page_name: Billing Agreements
  start_url: http://localhost:7780/admin/paypal/billing_agreement/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: '#ui-datepicker-div .ui-datepicker-prev, #ui-datepicker-div .ui-datepicker-next'
  description: the previous and next month links in the opened Billing Agreements datepicker
  coverage_policy: representative_group
setup: Open a Billing Agreements datepicker before inspecting the month navigation links.
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa08.datepicker_month_switch_not_keyboard_reachable`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
