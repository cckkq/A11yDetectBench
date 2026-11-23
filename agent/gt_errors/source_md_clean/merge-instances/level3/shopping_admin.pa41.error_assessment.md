# Merge Instance

```yaml
instance_id: shopping_admin.pa41.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA41
  review_status: clean_source_inventory_checked
page:
  site: shopping_admin
  page_name: Sales Orders Report
  start_url: http://localhost:7780/admin/reports/report_sales/sales/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa41.e1.invalid_input_degrades_to_page_level_failure
    target:
      selector: input#sales_report_from[name="from"], input#sales_report_to[name="to"]
      description: the From and To date inputs in the Magento Admin Sales Orders Report form
      coverage_policy: representative_group
    criterion:
      issue_family: error_identification
      wcag_target: WCAG 3.3.1 Error Identification
    evidence_rule: >-
      The invalid Sales Orders Report date path is handled as a generic processing failure
      instead of identifying the target From or To date field and describing the input error
      to the user in understandable text.
  - issue_id: shopping_admin.pa41.e2.invalid_input_degrades_to_page_level_failure
    target:
      selector: input#sales_report_from[name="from"], input#sales_report_to[name="to"]
      description: the From and To date inputs in the Magento Admin Sales Orders Report form
      coverage_policy: representative_group
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The invalid Sales Orders Report date path is handled as a generic processing failure
      and does not provide an accepted date format, an example date, a field-specific recovery
      step, or another actionable correction direction for the target From/To date inputs.
```

## Source And Live Check
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: error_identification, error_suggestion.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: shopping_admin + http://localhost:7780/admin/reports/report_sales/sales/ + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Sales Orders Report.
- gold.issues[] contains 2 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
