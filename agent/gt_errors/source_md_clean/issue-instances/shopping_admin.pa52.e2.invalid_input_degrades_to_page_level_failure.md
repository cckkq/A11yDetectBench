# Issue Instance

```yaml
instance_id: shopping_admin.pa52.e2.invalid_input_degrades_to_page_level_failure
template_id: error.e2.invalid_input_degrades_to_page_level_failure
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA52

page:
  site: shopping_admin
  page_name: Product Views Report
  start_url: http://localhost:7780/admin/reports/report_product/viewed/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input#sales_report_from[name="from"], input#sales_report_to[name="to"]'
  description: the From and To date inputs in the Magento Admin Product Views Report form
  coverage_policy: representative_group

probe: Enter `abc` in the target From field, enter `13/99/9999` in the target To field, and choose Show Report.

criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The invalid Product Views Report date path degrades to a broken or blank page
    state and does not provide an accepted date format, an example date, a
    field-specific recovery step, or another actionable correction direction for
    the target From/To date inputs.
```

## Selector Check

- `document.querySelectorAll('input#sales_report_from[name="from"], input#sales_report_to[name="to"]')` resolves to the two visible From and To date inputs on PA52.
- `document.querySelectorAll('button#filter_form_submit')` resolves to the visible Show Report button on PA52.
- The source record reports that the `From=abc` and `To=13/99/9999` path reaches a broken or blank page state with no correction suggestion.
- The target selector is the stable From/To date input pair, not the later broken page state.
