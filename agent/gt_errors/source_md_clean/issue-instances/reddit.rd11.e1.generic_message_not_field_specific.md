# Issue Instance

```yaml
instance_id: reddit.rd11.e1.generic_message_not_field_specific
template_id: error.e1.generic_message_not_field_specific
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD11

page:
  site: reddit
  page_name: Account
  start_url: http://localhost:9999/user/MarvelsGrantMan136/account
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]'
  description: the New password and repeat password inputs in the Reddit account form
  coverage_policy: representative_group

probe: Enter different valid-length values in the target fields and save changes. Do not submit matching password values or otherwise save a valid account update.

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

- `document.querySelectorAll('input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]')` resolves to the two visible password inputs on RD11 Account.
- A fresh Playwright probe with refreshed Reddit auth entered different valid-length values in the two password inputs and saved changes.
- The probe must stay on the mismatched-password path. Submitting matching password values is out of scope because it can save a valid account update and mutate the shared test account.
- The page stayed on RD11 Account and displayed one visible `ul.form-error-list` message.
- The visible message is evidence for this issue, but it is not the target selector. The target selector is the stable password input pair.
