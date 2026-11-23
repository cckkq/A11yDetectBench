# Issue Instance

```yaml
instance_id: shopping_admin.pa48.e2.invalid_date_summary_and_generic_failure_mixed
template_id: error.e2.invalid_date_summary_and_generic_failure_mixed
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA48

page:
  site: shopping_admin
  page_name: Braintree Settlement Report
  start_url: http://localhost:7780/admin/braintree/report/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input[name="createdAt[from]"], input[name="createdAt[to]"]'
  description: the Created At from/to filter inputs in the Magento Admin Braintree Settlement Report grid
  coverage_policy: representative_group

probe: Open the Filters panel, enter `not-a-date` in both target Created At fields, and apply filters.

criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The invalid Created At filter path is handled only by a generic invalid-date
    summary or a generic failure flow and does not provide an accepted date
    format, an example date, a field-specific recovery step, or another
    actionable correction direction for the target Created At fields.
```

## Selector Check

- `document.querySelectorAll('input[name="createdAt[from]"], input[name="createdAt[to]"]')` resolves to the Created At from/to filter inputs on PA48 after the Filters panel is open.
- A fresh Playwright probe with refreshed Magento Admin auth opened PA48, chose Filters, and observed both Created At filter inputs.
- The source record reports that applying `not-a-date` in the Created At filter fields produces the invalid-date summary path without a correction suggestion.
- The target selector is the stable Created At input pair, not the later summary text or failure dialog.
