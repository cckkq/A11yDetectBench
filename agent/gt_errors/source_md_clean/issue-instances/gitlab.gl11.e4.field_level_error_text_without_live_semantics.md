# Issue Instance

```yaml
instance_id: gitlab.gl11.e4.field_level_error_text_without_live_semantics
template_id: error.e4.field_level_error_text_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11

page:
  site: gitlab
  page_name: Profile settings
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input#user_name[name="user[name]"]'
  description: the Full name input in the GitLab profile form
  coverage_policy: single

probe: Clear the target Full name input and submit the profile form.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Clearing the target Full name input produces active same-page field-level
    error/status feedback at `input#user_name[name="user[name]"] +
    p.gl-field-error`, but that message node and its relevant ancestors do not
    expose role, aria-live, or equivalent status-message semantics. Other
    conforming alert or status messages on the same page do not rescue this
    field-level message path.
```

## Selector Check

- `document.querySelectorAll('input#user_name[name="user[name]"]')` resolves to one Full name input on GL11.
- `document.querySelectorAll('input#user_name[name="user[name]"] + p.gl-field-error')` resolves to the associated field-level message node.
- A fresh Playwright probe with refreshed GitLab auth cleared the target Full name input and submitted the profile form; the associated message became visible with text `Using emojis in names seems fun, but please try to set a status message instead`.
- The visible message is evidence for this issue, but it is not the target selector. The matched `p.gl-field-error` node has no `role`, no `aria-live`, and no `aria-atomic` attribute.
