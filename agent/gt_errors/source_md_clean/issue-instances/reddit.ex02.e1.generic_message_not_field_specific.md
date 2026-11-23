# Issue Instance

```yaml
instance_id: reddit.ex02.e1.generic_message_not_field_specific
template_id: error.e1.generic_message_not_field_specific
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: EX02

page:
  site: reddit
  page_name: Registration
  start_url: http://localhost:9999/registration
  auth_state_file: null

target:
  selector: 'input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]'
  description: the password and repeat password inputs in the Reddit registration form
  coverage_policy: representative_group

probe: Complete the other required registration fields, enter different valid-length values in the target password fields, and submit the registration form.

criterion:
  issue_family: error_identification
  wcag_target: WCAG 3.3.1 Error Identification

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The page detects the password mismatch but the visible error feedback does
    not identify the password-confirmation mismatch, does not describe which
    target field or field relation is invalid, and remains a generic invalid-value
    message.

```

## Selector Check

- `document.querySelectorAll('input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]')` resolves to the two visible password inputs on EX02 Registration in a no-auth page state.
- A fresh Playwright probe without Reddit auth opened `http://localhost:9999/registration` and observed the registration form without being redirected away.
- The source record reports that the password-mismatch submission path displays one visible `ul.form-error-list` message.
- The visible message is evidence for this issue, but it is not the target selector. The target selector is the stable password input pair.