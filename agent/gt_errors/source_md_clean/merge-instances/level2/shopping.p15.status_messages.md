# Merge Instance

```yaml
instance_id: shopping.p15.status_messages
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P15
  review_status: clean_source_inventory_checked
page:
  site: shopping
  page_name: Contact Us
  start_url: http://localhost:7770/contact/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
  assessment_requirement: E.4 Status Messages
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p15.e4.page_local_error_message_without_live_semantics
    target:
      selector: form#contact-form input#email
      description: the Email input in the Magento contact form
      coverage_policy: single
    criterion:
      issue_family: status_messages
      wcag_target: WCAG 4.1.3 Status Messages
    evidence_rule: >-
      Entering an invalid value in the target contact Email input produces active same-page
      field-level error/status feedback at `div#email-error`, but that message node and its
      relevant ancestors do not expose role, aria-live, or equivalent status-message semantics.
```

## Source And Live Check
- This L2 merge source contains the complete status-messages inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: shopping + http://localhost:7770/contact/ + status_messages + WCAG 4.1.3 Status Messages.
- This merge instance should generate one ERROR L2 task for Contact Us / status_messages.
- gold.issues[] contains 1 reviewed clean-source issue entries.
