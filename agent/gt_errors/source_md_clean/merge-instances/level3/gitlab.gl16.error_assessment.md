# Merge Instance

```yaml
instance_id: gitlab.gl16.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL16
  review_status: clean_source_inventory_checked
page:
  site: gitlab
  page_name: Emails
  start_url: http://localhost:8023/-/profile/emails
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl16.e2.rule_violation_without_actionable_suggestion
    target:
      selector: input#email_email[name="email[email]"]
      description: the add-email input in the GitLab Emails settings form
      coverage_policy: single
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The page detects the add-email value as invalid but does not provide an accepted email
      format, an example email address, an alternate address recovery direction, or another
      actionable correction direction. Other better validation paths on the same page do not
      rescue this add-email path.
```

## Source And Live Check
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: error_suggestion.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: gitlab + http://localhost:8023/-/profile/emails + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Emails.
- gold.issues[] contains 1 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
