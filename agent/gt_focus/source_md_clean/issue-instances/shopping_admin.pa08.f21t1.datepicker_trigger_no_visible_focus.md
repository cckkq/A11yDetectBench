# Issue Instance

```yaml
instance_id: shopping_admin.pa08.f21t1.datepicker_trigger_no_visible_focus
template_id: focus.visible_focus.datepicker_trigger_no_visible_focus
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA08

page:
  site: shopping_admin
  page_name: Billing Agreements
  start_url: http://localhost:7780/admin/paypal/billing_agreement/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: button.ui-datepicker-trigger
  description: the four date picker trigger buttons next to Created From, Created To, Updated From, and Updated To in the Billing Agreements grid filter row
  coverage_policy: representative_group

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: The target date picker trigger buttons receive keyboard focus, but no user-perceivable focus indicator is visible while one is keyboard-focused.
```

## Selector Check

- Playwright on PA08 resolved `button.ui-datepicker-trigger` to four visible buttons in the Billing Agreements grid filter row.
- The matched buttons are adjacent to the Created From, Created To, Updated From, and Updated To fields named by the legacy task.
