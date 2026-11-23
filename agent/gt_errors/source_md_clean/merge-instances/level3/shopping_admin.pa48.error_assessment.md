# Merge Instance

```yaml
instance_id: shopping_admin.pa48.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA48
  review_status: clean_source_inventory_checked
page:
  site: shopping_admin
  page_name: Braintree Settlement Report
  start_url: http://localhost:7780/admin/braintree/report/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa48.e1.invalid_date_summary_and_generic_failure_mixed
    target:
      selector: input[name="createdAt[from]"], input[name="createdAt[to]"]
      description: >-
        the Created At from/to filter inputs in the Magento Admin Braintree Settlement Report
        grid
      coverage_policy: representative_group
    criterion:
      issue_family: error_identification
      wcag_target: WCAG 3.3.1 Error Identification
    evidence_rule: >-
      The invalid Created At filter path is handled only by a generic invalid-date summary
      or a generic failure flow, rather than identifying the specific target filter field
      relation and describing the input error to the user in understandable text.
  - issue_id: shopping_admin.pa48.e2.invalid_date_summary_and_generic_failure_mixed
    target:
      selector: input[name="createdAt[from]"], input[name="createdAt[to]"]
      description: >-
        the Created At from/to filter inputs in the Magento Admin Braintree Settlement Report
        grid
      coverage_policy: representative_group
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The invalid Created At filter path is handled only by a generic invalid-date summary
      or a generic failure flow and does not provide an accepted date format, an example date,
      a field-specific recovery step, or another actionable correction direction for the target
      Created At fields.
```

## Source And Live Check
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: error_identification, error_suggestion.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: shopping_admin + http://localhost:7780/admin/braintree/report/ + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Braintree Settlement Report.
- gold.issues[] contains 2 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
