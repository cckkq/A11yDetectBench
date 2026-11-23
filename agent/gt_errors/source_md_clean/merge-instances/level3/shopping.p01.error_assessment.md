# Merge Instance

```yaml
instance_id: shopping.p01.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P01
  review_status: clean_source_inventory_checked
page:
  site: shopping
  page_name: My Account
  start_url: http://localhost:7770/customer/account/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p01.e4.shared_footer_newsletter_error_without_live_semantics
    target:
      selector: form#newsletter-validate-detail input#newsletter
      description: the footer newsletter Email input on the Magento account page
      coverage_policy: single
    criterion:
      issue_family: status_messages
      wcag_target: WCAG 4.1.3 Status Messages
    evidence_rule: >-
      Entering an invalid value in the target footer newsletter Email input produces active
      same-page error/status feedback at `div#newsletter-error`, but that message node and
      its relevant ancestors do not expose role, aria-live, or equivalent status-message semantics.
```

## Source And Live Check
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: status_messages.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: shopping + http://localhost:7770/customer/account/ + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for My Account.
- gold.issues[] contains 1 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
