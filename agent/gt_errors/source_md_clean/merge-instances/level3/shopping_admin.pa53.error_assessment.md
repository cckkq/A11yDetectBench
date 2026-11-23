# Merge Instance

```yaml
instance_id: shopping_admin.pa53.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA53
  review_status: clean_source_inventory_checked
page:
  site: shopping_admin
  page_name: Bestsellers Report
  start_url: http://localhost:7780/admin/reports/report_sales/bestsellers/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa53.e1.invalid_input_degrades_to_page_level_failure
    target:
      selector: input#sales_report_from[name="from"], input#sales_report_to[name="to"]
      description: the From and To date inputs in the Magento Admin Bestsellers Report form
      coverage_policy: representative_group
    criterion:
      issue_family: error_identification
      wcag_target: WCAG 3.3.1 Error Identification
    evidence_rule: >-
      The invalid Bestsellers Report date path is handled as a generic processing failure
      instead of identifying the target From or To date field and describing the input error
      to the user in understandable text.
  - issue_id: shopping_admin.pa53.e2.invalid_input_degrades_to_page_level_failure
    target:
      selector: input#sales_report_from[name="from"], input#sales_report_to[name="to"]
      description: the From and To date inputs in the Magento Admin Bestsellers Report form
      coverage_policy: representative_group
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The invalid Bestsellers Report date path is handled as a generic processing failure
      and does not provide an accepted date format, an example date, a field-specific
      recovery step, or another actionable correction direction for the target From/To
      date inputs.
```

## Source And Live Check
- This L3 merge source contains the reviewed ERROR E.1-E.4 inventory for this BASE-induced page owner key.
- Reviewed L3 families on this page: error_identification, error_suggestion.
- The E2 entry is an L3-only inventory item traced to the same PA53 invalid-date page-level failure path recorded in the source records and E2 template family.
- Completeness is scoped to the reviewed L3 inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: shopping_admin + http://localhost:7780/admin/reports/report_sales/bestsellers/ + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Bestsellers Report.
- gold.issues[] contains 2 reviewed issue entries.
- This generated merge source includes 1 L3-only issue beyond the current clean L1 source inventory.
