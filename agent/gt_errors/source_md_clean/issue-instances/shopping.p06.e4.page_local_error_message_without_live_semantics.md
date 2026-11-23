# Issue Instance

```yaml
instance_id: shopping.p06.e4.page_local_error_message_without_live_semantics
template_id: error.e4.page_local_error_message_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P06

page:
  site: shopping
  page_name: Edit Account Information
  start_url: http://localhost:7770/customer/account/edit/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: input#firstname
  description: the First Name input in the Magento account edit form
  coverage_policy: single

probe: Clear the target First Name input and save the account form.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Clearing the target First Name input produces active same-page field-level
    error/status feedback at `div#firstname-error`, but that message node and
    its relevant ancestors do not expose role, aria-live, or equivalent
    status-message semantics. The unrelated password-strength live region does
    not carry this error message and does not rescue this field-level message
    path.
```

## Selector Check

- `document.querySelectorAll('input#firstname')` resolves to one visible First Name input on P06.
- A fresh Playwright probe with refreshed Shopping auth cleared the target input and submitted `form#form-validate`.
- The associated `div#firstname-error` message became visible with text `This is a required field.`.
- The visible message is evidence for this issue, but it is not the target selector. The matched `div#firstname-error` node has no `role`, no `aria-live`, and no `aria-atomic` attribute.
