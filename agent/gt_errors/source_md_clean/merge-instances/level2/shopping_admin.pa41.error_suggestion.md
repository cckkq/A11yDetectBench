# Merge Instance

```yaml
instance_id: shopping_admin.pa41.error_suggestion
task_level: level2
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
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion
  assessment_requirement: E.2 Error Suggestion
gold:
  expected_verdict: issue_found
  issues:
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
- This L2 merge source contains the complete error-suggestion inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: shopping_admin + http://localhost:7780/admin/reports/report_sales/sales/ + error_suggestion + WCAG 3.3.3 Error Suggestion.
- This merge instance should generate one ERROR L2 task for Sales Orders Report / error_suggestion.
- gold.issues[] contains 1 reviewed clean-source issue entries.
