# Merge Instance

```yaml
instance_id: shopping_admin.pa06.error_suggestion
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA06
  review_status: clean_source_inventory_checked
page:
  site: shopping_admin
  page_name: Shipments
  start_url: http://localhost:7780/admin/sales/shipment/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion
  assessment_requirement: E.2 Error Suggestion
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa06.e2.invalid_date_without_expected_format
    target:
      selector: input[name="created_at[from]"], input[name="created_at[to]"]
      description: the Ship Date From and To filter inputs in the Magento Admin Shipments
        grid
      coverage_policy: representative_group
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The page detects the Ship Date filter values as invalid but does not provide an accepted
      date format, an example date, a placeholder, or another actionable correction direction.
      The active-filter summary text that reports the invalid date is not itself a correction
      suggestion.
```

## Source And Live Check
- This L2 merge source contains the complete error-suggestion inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: shopping_admin + http://localhost:7780/admin/sales/shipment/ + error_suggestion + WCAG 3.3.3 Error Suggestion.
- This merge instance should generate one ERROR L2 task for Shipments / error_suggestion.
- gold.issues[] contains 1 reviewed clean-source issue entries.
