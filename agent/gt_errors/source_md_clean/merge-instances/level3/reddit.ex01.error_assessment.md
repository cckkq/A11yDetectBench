# Merge Instance

```yaml
instance_id: reddit.ex01.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: EX01
  review_status: clean_source_inventory_checked
page:
  site: reddit
  page_name: Login
  start_url: http://localhost:9999/login
  auth_state_file: null
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: reddit.ex01.e2.generic_rejection_without_guidance
    target:
      selector: input#login-username[name="_username"], input#login-password[name="_password"]
      description: the username and password inputs in the Reddit login form
      coverage_policy: representative_group
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The page detects the submitted login credentials as invalid but does not provide an
      actionable correction direction for the username/password path, such as checking the
      entered credentials, retrying the relevant field, or explaining which credential input
      needs attention.
```

## Source And Live Check
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: error_suggestion.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: reddit + http://localhost:9999/login + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Login.
- gold.issues[] contains 1 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
