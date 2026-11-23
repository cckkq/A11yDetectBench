# Issue Instance

```yaml
instance_id: gitlab.gl16.e2.rule_violation_without_actionable_suggestion
template_id: error.e2.rule_violation_without_actionable_suggestion
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL16

page:
  site: gitlab
  page_name: Emails
  start_url: http://localhost:8023/-/profile/emails
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input#email_email[name="email[email]"]'
  description: the add-email input in the GitLab Emails settings form
  coverage_policy: single

probe: Enter `abc` in the target field and submit the add-email form.

criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The page detects the add-email value as invalid but does not provide an
    accepted email format, an example email address, an alternate address
    recovery direction, or another actionable correction direction. Other better
    validation paths on the same page do not rescue this add-email path.
```

## Selector Check

- `document.querySelectorAll('input#email_email[name="email[email]"]')` resolves to one visible input on GL16.
- The matched input has `id="email_email"`, `name="email[email]"`, label text `Email`, and is the field used by the add-email validation path.
- A fresh Playwright probe with refreshed GitLab auth entered `abc` in this input and submitted the add-email form. The page then displayed the visible alert message `Email is invalid`.
- The alert message is evidence for this issue, but it is not the target selector. The target selector is the stable add-email input path.
