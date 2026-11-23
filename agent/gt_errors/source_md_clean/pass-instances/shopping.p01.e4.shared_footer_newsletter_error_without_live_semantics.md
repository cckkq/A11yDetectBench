# PASS Instance

```yaml
instance_id: shopping.p01.e4.shared_footer_newsletter_error_without_live_semantics
template_id: error.e4.shared_footer_newsletter_error_without_live_semantics
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P01
  matched_positive: shopping.p01.e4.shared_footer_newsletter_error_without_live_semantics
page:
  site: shopping
  page_name: My Account
  start_url: http://localhost:7770/customer/account/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: form#newsletter-validate-detail input#newsletter
  description: the footer newsletter Email input on the Magento account page
  coverage_policy: single
probe: >-
  Enter `not-an-email` in the target newsletter Email input and submit the newsletter form.
criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same target interaction so the triggered same-page status, error, or
    progress message is programmatically exposed through role, aria-live, or equivalent status-message
    semantics. A reported E.4 issue on this matched target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping.p01.e4.shared_footer_newsletter_error_without_live_semantics`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
