# PASS Instance

```yaml
instance_id: shopping_admin.pa04.e2.invalid_date_without_expected_format
template_id: error.e2.invalid_date_without_expected_format
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04
  matched_positive: shopping_admin.pa04.e2.invalid_date_without_expected_format
page:
  site: shopping_admin
  page_name: Orders
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: input[name="created_at[from]"], input[name="created_at[to]"]
  description: the Purchase Date from/to filter inputs in the Magento Admin Orders grid
  coverage_policy: representative_group
probe: Open the Filters panel, enter `not-a-date` in both target fields, and apply filters.
criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same target path so any automatically detected input error provides an
    actionable correction suggestion. A reported E.2 issue on this matched target is a false
    alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa04.e2.invalid_date_without_expected_format`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
