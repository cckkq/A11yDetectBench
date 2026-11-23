# Merge Instance

```yaml
instance_id: gitlab.gl11.status_messages
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11
  review_status: clean_source_inventory_checked
page:
  site: gitlab
  page_name: Profile settings
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
  assessment_requirement: E.4 Status Messages
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl11.e4.field_level_error_text_without_live_semantics
    target:
      selector: input#user_name[name="user[name]"]
      description: the Full name input in the GitLab profile form
      coverage_policy: single
    criterion:
      issue_family: status_messages
      wcag_target: WCAG 4.1.3 Status Messages
    evidence_rule: >-
      Clearing the target Full name input produces active same-page field-level error/status
      feedback at `input#user_name[name="user[name]"] + p.gl-field-error`, but that message
      node and its relevant ancestors do not expose role, aria-live, or equivalent status-message
      semantics. Other conforming alert or status messages on the same page do not rescue
      this field-level message path.
```

## Source And Live Check
- This L2 merge source contains the complete status-messages inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: gitlab + http://localhost:8023/-/profile + status_messages + WCAG 4.1.3 Status Messages.
- This merge instance should generate one ERROR L2 task for Profile settings / status_messages.
- gold.issues[] contains 1 reviewed clean-source issue entries.
