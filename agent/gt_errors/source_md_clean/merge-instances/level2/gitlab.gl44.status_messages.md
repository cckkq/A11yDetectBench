# Merge Instance

```yaml
instance_id: gitlab.gl44.status_messages
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL44
  review_status: clean_source_inventory_checked
page:
  site: gitlab
  page_name: New Group Import Group Pane
  start_url: http://localhost:8023/groups/new#import-group-pane
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
  assessment_requirement: E.4 Status Messages
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl44.e4.gitlab_source_url_error_text_without_live_semantics
    target:
      selector: input#import_gitlab_url[name="bulk_import_gitlab_url"]
      description: the GitLab source URL input in the GitLab import group form
      coverage_policy: single
    criterion:
      issue_family: status_messages
      wcag_target: WCAG 4.1.3 Status Messages
    evidence_rule: >-
      Leaving the target GitLab source URL input empty produces active same-page field-level
      error/status feedback at `input#import_gitlab_url[name="bulk_import_gitlab_url"] + p.gl-field-error`,
      but that message node and its relevant ancestors do not expose role, aria-live, or equivalent
      status-message semantics. Other conforming group-name or group-path feedback on the
      same page does not rescue this field-level message path.
  - issue_id: gitlab.gl44.e4.personal_access_token_error_text_without_live_semantics
    target:
      selector: input#import_gitlab_token[name="bulk_import_gitlab_access_token"]
      description: the Personal access token input in the GitLab import group form
      coverage_policy: single
    criterion:
      issue_family: status_messages
      wcag_target: WCAG 4.1.3 Status Messages
    evidence_rule: >-
      Leaving the target Personal access token input empty produces active same-page field-level
      error/status feedback at `input#import_gitlab_token[name="bulk_import_gitlab_access_token"]
      + p.gl-field-error`, but that message node and its relevant ancestors do not expose
      role, aria-live, or equivalent status-message semantics. Other conforming group-name
      or group-path feedback on the same page does not rescue this field-level message path.
```

## Source And Live Check
- This L2 merge source contains the complete status-messages inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: gitlab + http://localhost:8023/groups/new#import-group-pane + status_messages + WCAG 4.1.3 Status Messages.
- This merge instance should generate one ERROR L2 task for New Group Import Group Pane / status_messages.
- gold.issues[] contains 2 reviewed clean-source issue entries.
