# PASS Instance

```yaml
instance_id: shopping_admin.pa41.e1.invalid_input_degrades_to_page_level_failure
template_id: error.e1.invalid_input_degrades_to_page_level_failure
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA41
  matched_positive: shopping_admin.pa41.e1.invalid_input_degrades_to_page_level_failure
page:
  site: shopping_admin
  page_name: Sales Orders Report
  start_url: http://localhost:7780/admin/reports/report_sales/sales/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: input#sales_report_from[name="from"], input#sales_report_to[name="to"]
  description: the From and To date inputs in the Magento Admin Sales Orders Report form
  coverage_policy: representative_group
probe: Enter `abc` in the target From field, enter `13/99/9999` in the target To field, and choose Show Report.
criterion:
  issue_family: error_identification
  wcag_target: WCAG 3.3.1 Error Identification
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same target path so the page no longer lacks user-facing identification
    for the automatically detected input error. A reported E.1 issue on this matched target
    is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa41.e1.invalid_input_degrades_to_page_level_failure`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
