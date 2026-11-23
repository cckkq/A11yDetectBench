# Issue Instance

```yaml
instance_id: shopping_admin.pa03.e4.magento_admin_status_message_without_live_semantics
template_id: error.e4.magento_admin_status_message_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA03

page:
  site: shopping_admin
  page_name: My Account
  start_url: http://localhost:7780/admin/admin/system_account/index/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: input#current_password
  description: the Current User Identity Verification password input in the Magento Admin My Account page
  coverage_policy: single

probe: Enter an invalid value in the target current password input and save the account form.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Entering an invalid value in the target current password input produces
    active same-page account-save status feedback at `#messages
    .message.message-error.error`, but that message node and its relevant
    ancestors do not expose role, aria-live, or equivalent status-message
    semantics.
```

## Selector Check

- `document.querySelectorAll('input#current_password')` resolves to one visible Current User Identity Verification password input on PA03.
- The `#messages .message.message-error.error` message is created by the same-page account-save error feedback path after an invalid current password submission.
- The source record reports that the account-save success and failure message containers use Magento Admin message classes without role or aria-live semantics.
- The visible error message is evidence for this issue, but it is not the target selector. The target selector is the stable current password input path.
