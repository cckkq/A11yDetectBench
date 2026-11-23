# Issue Instance

```yaml
instance_id: reddit.rd11.e2.generic_rejection_without_guidance
template_id: error.e2.generic_rejection_without_guidance
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
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The page detects the password mismatch but does not provide an actionable
    correction direction such as entering matching password values, reviewing the
    repeated password field, or otherwise explaining how to correct the mismatch.
```

## Selector Check

- `document.querySelectorAll('input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]')` resolves to the two visible password inputs on RD11 Account.
- A fresh Playwright probe with refreshed Reddit auth entered different valid-length values in the two password inputs and saved changes.
- The probe must stay on the mismatched-password path. Submitting matching password values is out of scope because it can save a valid account update and mutate the shared test account.
- The page stayed on RD11 Account and displayed one visible `ul.form-error-list` message.
- The visible message is evidence for this issue, but it is not the target selector. The target selector is the stable password input pair.
