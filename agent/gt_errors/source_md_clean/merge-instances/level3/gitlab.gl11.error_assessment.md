# Merge Instance

```yaml
instance_id: gitlab.gl11.error_assessment
task_level: level3
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
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl11.e2.rule_violation_without_actionable_suggestion
    target:
      selector: input#user_website_url[name="user[website_url]"]
      description: the Website URL input in the GitLab profile form
      coverage_policy: single
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The page detects the Website URL value as invalid but does not provide an accepted URL
      format, an example URL, or another actionable correction direction. Other better validation
      paths on the same page do not rescue this Website URL path.
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
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: error_suggestion, status_messages.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: gitlab + http://localhost:8023/-/profile + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Profile settings.
- gold.issues[] contains 2 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
