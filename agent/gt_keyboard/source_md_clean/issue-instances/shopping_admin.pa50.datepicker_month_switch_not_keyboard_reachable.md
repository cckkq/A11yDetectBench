# Issue Instance

```yaml
instance_id: shopping_admin.pa50.datepicker_month_switch_not_keyboard_reachable
template_id: keyboard.keyboard_nonreachable.datepicker_month_switch_not_keyboard_reachable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA50
page:
  site: shopping_admin
  page_name: Customer Order Count Report
  start_url: http://localhost:7780/admin/reports/report_customer/orders/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: '#ui-datepicker-div .ui-datepicker-prev, #ui-datepicker-div .ui-datepicker-next'
  description: the previous and next month links in the opened Customer Orders datepicker
  coverage_policy: representative_group
setup: Open a Customer Orders report datepicker before inspecting the month navigation links.
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the previous and next month links in the opened Customer Orders
    datepicker) is visible and pointer-operable or part of an active widget, but expected
    keyboard navigation cannot reach or complete operation of that same target. Reporting
    a different keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: After opening the report datepicker, Playwright resolved visible Previous and Next links.
- Setup for selector visibility: Open a Customer Orders report datepicker before inspecting the month navigation links.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
