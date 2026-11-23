# Issue Instance

```yaml
instance_id: shopping_admin.pa04.e2.invalid_date_without_expected_format
template_id: error.e2.invalid_date_without_expected_format
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04

page:
  site: shopping_admin
  page_name: Orders
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input[name="created_at[from]"], input[name="created_at[to]"]'
  description: the Purchase Date from/to filter inputs in the Magento Admin Orders grid
  coverage_policy: representative_group

probe: Open the Filters panel, enter `not-a-date` in both target fields, and apply filters.

criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The page detects the Purchase Date filter values as invalid but does not
    provide an accepted date format, an example date, a placeholder, or another
    actionable correction direction. The active-filter summary text that reports
    the invalid date is not itself a correction suggestion.
```

## Selector Check

- `document.querySelectorAll('input[name="created_at[from]"], input[name="created_at[to]"]')` resolves to the Purchase Date from/to filter inputs on PA04 after the Filters panel is open.
- The matched inputs are the fields used by the Orders grid Purchase Date filter.
- A fresh Playwright probe with refreshed Magento Admin auth opened the Filters panel and observed both `created_at[from]` and `created_at[to]` inputs on the page.
- The source record reports that applying invalid Purchase Date values displays an active-filter summary with an invalid-date message, without an accepted date format or example.
