# Issue Instance

```yaml
instance_id: shopping.p07.e4.shared_footer_newsletter_error_without_live_semantics
template_id: error.e4.shared_footer_newsletter_error_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P07

page:
  site: shopping
  page_name: Stored Payment Methods
  start_url: http://localhost:7770/vault/cards/listaction/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: form#newsletter-validate-detail input#newsletter
  description: the footer newsletter Email input on the stored payment methods page
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
    aria-live, or equivalent status-message semantics. Other conforming success
    feedback on the same page does not rescue this newsletter error message
    path.
```

## Selector Check

- `document.querySelectorAll('form#newsletter-validate-detail input#newsletter')` resolves to one visible newsletter Email input on P07.
- `document.querySelectorAll('form#newsletter-validate-detail')` resolves to the visible footer newsletter form on P07.
- The associated `div#newsletter-error` message appears after the newsletter form is submitted with an invalid Email value.
- The visible message is evidence for this issue, but it is not the target selector. The source record reports that this newsletter error path lacks role, aria-live, or equivalent status-message semantics even though other same-page feedback may be conforming.
