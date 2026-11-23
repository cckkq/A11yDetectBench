# Merge Instance

```yaml
instance_id: reddit.ex02.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: EX02
  review_status: clean_source_inventory_checked
page:
  site: reddit
  page_name: Registration
  start_url: http://localhost:9999/registration
  auth_state_file: null
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: reddit.ex02.e1.generic_message_not_field_specific
    target:
      selector: >-
        input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]
      description: the password and repeat password inputs in the Reddit registration form
      coverage_policy: representative_group
    criterion:
      issue_family: error_identification
      wcag_target: WCAG 3.3.1 Error Identification
    evidence_rule: >-
      The page detects the password mismatch but the visible error feedback does not identify
      the password-confirmation mismatch, does not describe which target field or field relation
      is invalid, and remains a generic invalid-value message.
  - issue_id: reddit.ex02.e2.generic_rejection_without_guidance
    target:
      selector: >-
        input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]
      description: the password and repeat password inputs in the Reddit registration form
      coverage_policy: representative_group
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The page detects the password mismatch but does not provide an actionable correction
      suggestion telling the user to re-enter matching passwords or otherwise explain how
      to recover from the invalid password-confirmation path.
```

## Source And Live Check
- This L3 merge source contains the reviewed ERROR E.1-E.4 inventory for this BASE-induced page owner key.
- Reviewed L3 families on this page: error_identification, error_suggestion.
- The E2 entry is an L3-only inventory item traced to the same EX02 password-mismatch path recorded in the source records and E2 template family.
- Completeness is scoped to the reviewed L3 inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: reddit + http://localhost:9999/registration + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Registration.
- gold.issues[] contains 2 reviewed issue entries.
- This generated merge source includes 1 L3-only issue beyond the current clean L1 source inventory.
