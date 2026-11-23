# Issue Instance

```yaml
instance_id: gitlab.gl44.e4.gitlab_source_url_error_text_without_live_semantics
template_id: error.e4.field_level_error_text_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL44

page:
  site: gitlab
  page_name: New Group Import Group Pane
  start_url: http://localhost:8023/groups/new#import-group-pane
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input#import_gitlab_url[name="bulk_import_gitlab_url"]'
  description: the GitLab source URL input in the GitLab import group form
  coverage_policy: single

probe: In the Import Group pane, complete the other required group fields, leave the target GitLab source URL field empty, and submit the import group form.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Leaving the target GitLab source URL input empty produces active same-page
    field-level error/status feedback at `input#import_gitlab_url[name="bulk_import_gitlab_url"]
    + p.gl-field-error`, but that message node and its relevant ancestors do
    not expose role, aria-live, or equivalent status-message semantics. Other
    conforming group-name or group-path feedback on the same page does not
    rescue this field-level message path.

```

## Selector Check

- `document.querySelectorAll('input#import_gitlab_url[name="bulk_import_gitlab_url"]')` resolves to one GitLab source URL input on GL44 with label text `GitLab source URL`.
- `document.querySelectorAll('input#import_gitlab_url[name="bulk_import_gitlab_url"] + p.gl-field-error')` resolves to the associated field-level message node.
- The associated `p.gl-field-error` node is hidden before the import-group submission path and contains the GitLab source URL required-field message.
- The visible message is evidence for this issue, but it is not the target selector. The matched message node has no `role`, no `aria-live`, and no `aria-atomic` attribute.