# Issue Instance

```yaml
instance_id: reddit.ex01.e2.generic_rejection_without_guidance
template_id: error.e2.generic_rejection_without_guidance
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: EX01

page:
  site: reddit
  page_name: Login
  start_url: http://localhost:9999/login
  auth_state_file: null

target:
  selector: 'input#login-username[name="_username"], input#login-password[name="_password"]'
  description: the username and password inputs in the Reddit login form
  coverage_policy: representative_group

probe: Enter invalid credentials in the target fields and submit the login form.

criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The page detects the submitted login credentials as invalid but does not
    provide an actionable correction direction for the username/password path,
    such as checking the entered credentials, retrying the relevant field, or
    explaining which credential input needs attention.

```

## Selector Check

- `document.querySelectorAll('input#login-username[name="_username"], input#login-password[name="_password"]')` resolves to the two visible credential inputs on EX01 Login in a no-auth page state.
- A fresh Playwright probe without Reddit auth opened `http://localhost:9999/login` and observed the login form without being redirected away.
- The source record reports that submitting wrong credentials displays a same-page `ul.form-error-list` message.
- The visible error message is evidence for this issue, but it is not the target selector. The target selector is the stable credential input pair.