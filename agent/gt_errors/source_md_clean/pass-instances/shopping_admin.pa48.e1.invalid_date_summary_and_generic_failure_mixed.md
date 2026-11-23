# PASS Instance

```yaml
instance_id: shopping_admin.pa48.e1.invalid_date_summary_and_generic_failure_mixed
template_id: error.e1.invalid_date_summary_and_generic_failure_mixed
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA48
  matched_positive: shopping_admin.pa48.e1.invalid_date_summary_and_generic_failure_mixed
page:
  site: shopping_admin
  page_name: Braintree Settlement Report
  start_url: http://localhost:7780/admin/braintree/report/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: input[name="createdAt[from]"], input[name="createdAt[to]"]
  description: >-
    the Created At from/to filter inputs in the Magento Admin Braintree Settlement Report
    grid
  coverage_policy: representative_group
probe: Open the Filters panel, enter `not-a-date` in both target Created At fields, and apply filters.
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

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa48.e1.invalid_date_summary_and_generic_failure_mixed`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
