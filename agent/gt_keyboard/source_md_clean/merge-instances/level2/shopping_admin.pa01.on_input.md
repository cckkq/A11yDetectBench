# Merge Instance

```yaml
instance_id: shopping_admin.pa01.on_input
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA01
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Admin Dashboard
  start_url: http://localhost:7780/admin/admin/dashboard/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
  assessment_requirement: 1.4 On input
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa01.store_view_context_change
    target:
      selector: button#store-change-button
      description: the All Store Views selector button on the Magento Admin dashboard
      coverage_policy: single
    criterion:
      issue_family: on_input
      wcag_target: WCAG 3.2.2 On Input
    evidence_rule: >-
      The target control (the All Store Views selector button on the Magento Admin dashboard)
      changes page context, navigation state, result ordering, or equivalent page state immediately
      after the control value or selection changes, without a separate submit or apply action
      and without prior warning. Merely opening a menu is not sufficient.
```

## Source And Live Check

- This L2 merge source is restricted to a BASE-induced page/family owner key.
- Completeness is scoped to reviewed Keyboard inventory inside that owner key, not a new full-site audit.
- No BASE-external page or page/family owner is introduced here.

## Merge Scope

- Owner key: shopping_admin + PA01 + on_input + WCAG 3.2.2 On Input.
- gold.issues[] contains 1 reviewed issue entries.
