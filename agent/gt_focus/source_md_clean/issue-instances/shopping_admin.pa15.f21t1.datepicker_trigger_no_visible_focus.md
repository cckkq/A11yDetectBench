# Issue Instance

```yaml
instance_id: shopping_admin.pa15.f21t1.datepicker_trigger_no_visible_focus
template_id: focus.visible_focus.datepicker_trigger_no_visible_focus
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA15
page:
  site: shopping_admin
  page_name: Catalog Price Rules
  start_url: http://localhost:7780/admin/catalog_rule/promo_catalog/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: button.ui-datepicker-trigger
  description: the Start and End date picker trigger buttons in the Catalog Price Rules filter row
  coverage_policy: representative_group
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
gold:
  expected_verdict: issue_found
  evidence_rule: The target date picker trigger buttons receive keyboard focus, but no user-perceivable focus indicator is visible while one is keyboard-focused.
```

## Selector Check

- Playwright on PA15 resolved `button.ui-datepicker-trigger` to four visible buttons on the Catalog Price Rules page.
- The matched buttons correspond to the Start From, Start To, End From, and End To date filter triggers.
