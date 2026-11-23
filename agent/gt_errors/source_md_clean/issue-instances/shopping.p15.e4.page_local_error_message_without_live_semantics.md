# Issue Instance

```yaml
instance_id: shopping.p15.e4.page_local_error_message_without_live_semantics
template_id: error.e4.page_local_error_message_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P15

page:
  site: shopping
  page_name: Contact Us
  start_url: http://localhost:7770/contact/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: form#contact-form input#email
  description: the Email input in the Magento contact form
  coverage_policy: single

probe: Enter `not-an-email` in the target Email input, fill the other required contact fields, and submit the contact form.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Entering an invalid value in the target contact Email input produces active
    same-page field-level error/status feedback at `div#email-error`, but that
    message node and its relevant ancestors do not expose role, aria-live, or
    equivalent status-message semantics.
```

## Selector Check

- `document.querySelectorAll('form#contact-form input#email')` resolves to one visible contact Email input on P15.
- A fresh Playwright probe filled the contact Name and comment fields, entered `not-an-email` in the target input, and submitted `form#contact-form`.
- The associated `div#email-error` message became visible with text `Please enter a valid email address (Ex: johndoe@domain.com).`.
- The visible message is evidence for this issue, but it is not the target selector. The matched `div#email-error` node has no `role`, no `aria-live`, and no `aria-atomic` attribute.
