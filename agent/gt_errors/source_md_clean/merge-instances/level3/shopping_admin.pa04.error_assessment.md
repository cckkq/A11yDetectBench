# Merge Instance

```yaml
instance_id: shopping_admin.pa04.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04
  review_status: clean_source_inventory_checked
page:
  site: shopping_admin
  page_name: Orders
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa04.e2.invalid_date_without_expected_format
    target:
      selector: input[name="created_at[from]"], input[name="created_at[to]"]
      description: the Purchase Date from/to filter inputs in the Magento Admin Orders grid
      coverage_policy: representative_group
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The page detects the Purchase Date filter values as invalid but does not provide an
      accepted date format, an example date, a placeholder, or another actionable correction
      direction. The active-filter summary text that reports the invalid date is not itself
      a correction suggestion.
```

## Source And Live Check
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: error_suggestion.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: shopping_admin + http://localhost:7780/admin/sales/order/ + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Orders.
- gold.issues[] contains 1 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
