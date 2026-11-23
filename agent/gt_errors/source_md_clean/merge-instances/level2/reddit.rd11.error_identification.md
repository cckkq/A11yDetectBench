# Merge Instance

```yaml
instance_id: reddit.rd11.error_identification
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD11
  review_status: clean_source_inventory_checked
page:
  site: reddit
  page_name: Account
  start_url: http://localhost:9999/user/MarvelsGrantMan136/account
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: error_identification
  wcag_target: WCAG 3.3.1 Error Identification
  assessment_requirement: E.1 Error Identification
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: reddit.rd11.e1.generic_message_not_field_specific
    target:
      selector: >-
        input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]
      description: the New password and repeat password inputs in the Reddit account form
      coverage_policy: representative_group
    criterion:
      issue_family: error_identification
      wcag_target: WCAG 3.3.1 Error Identification
    evidence_rule: >-
      The page detects the password mismatch but the visible error feedback does not identify
      the password-confirmation mismatch, does not describe which target field or field relation
      is invalid, and remains a generic invalid-value message.
```

## Source And Live Check
- This L2 merge source contains the complete error-identification inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: reddit + http://localhost:9999/user/MarvelsGrantMan136/account + error_identification + WCAG 3.3.1 Error Identification.
- This merge instance should generate one ERROR L2 task for Account / error_identification.
- gold.issues[] contains 1 reviewed clean-source issue entries.
