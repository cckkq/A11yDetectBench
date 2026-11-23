# Merge Instance

```yaml
instance_id: reddit.ex01.error_suggestion
task_level: level2
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
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion
  assessment_requirement: E.2 Error Suggestion
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
- This L2 merge source contains the complete error-suggestion inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: reddit + http://localhost:9999/login + error_suggestion + WCAG 3.3.3 Error Suggestion.
- This merge instance should generate one ERROR L2 task for Login / error_suggestion.
- gold.issues[] contains 1 reviewed clean-source issue entries.
