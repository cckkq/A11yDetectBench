# Merge Instance

```yaml
instance_id: shopping_admin.pa41.error_identification
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
  issue_family: error_identification
  wcag_target: WCAG 3.3.1 Error Identification
  assessment_requirement: E.1 Error Identification
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
```

## Source And Live Check
- This L2 merge source contains the complete error-identification inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: shopping_admin + http://localhost:7780/admin/reports/report_sales/sales/ + error_identification + WCAG 3.3.1 Error Identification.
- This merge instance should generate one ERROR L2 task for Sales Orders Report / error_identification.
- gold.issues[] contains 1 reviewed clean-source issue entries.
