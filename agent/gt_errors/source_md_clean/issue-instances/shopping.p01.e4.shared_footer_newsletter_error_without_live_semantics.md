# Issue Instance

```yaml
instance_id: shopping.p01.e4.shared_footer_newsletter_error_without_live_semantics
template_id: error.e4.shared_footer_newsletter_error_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P01

page:
  site: shopping
  page_name: My Account
  start_url: http://localhost:7770/customer/account/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: form#newsletter-validate-detail input#newsletter
  description: the footer newsletter Email input on the Magento account page
  coverage_policy: single

probe: Enter `not-an-email` in the target newsletter Email input and submit the newsletter form.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Entering an invalid value in the target footer newsletter Email input
    produces active same-page error/status feedback at `div#newsletter-error`,
    but that message node and its relevant ancestors do not expose role,
    aria-live, or equivalent status-message semantics.
```

## Selector Check

- `document.querySelectorAll('form#newsletter-validate-detail input#newsletter')` resolves to one visible footer newsletter Email input on P01.
- A fresh Playwright probe with refreshed Shopping auth entered `not-an-email` in the target input and submitted `form#newsletter-validate-detail`.
- The associated `div#newsletter-error` message became visible with text `Please enter a valid email address (Ex: johndoe@domain.com).`.
- The visible message is evidence for this issue, but it is not the target selector. The matched `div#newsletter-error` node has no `role`, no `aria-live`, and no `aria-atomic` attribute.
