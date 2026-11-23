# Merge Instance

```yaml
instance_id: shopping_admin.pa49.keyboard_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA49
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Customer Order Total Report
  start_url: http://localhost:7780/admin/reports/report_customer/totals/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa49.global_search_shortcut_active_outside_input
    target:
      selector: input#search-global
      description: >-
        the Magento Admin global search input targeted by shortcuts on the customer totals
        report
      coverage_policy: single
    criterion:
      issue_family: character_key_shortcuts
      wcag_target: WCAG 2.1.4 Character Key Shortcuts
    evidence_rule: >-
      Pressing / or ? while focus is outside an editable field moves focus to the Magento
      Admin global search input targeted by shortcuts on the customer totals report. The task
      path does not expose a way to turn off, remap, or limit that single-character shortcut
      to cases where the search input already has focus.
  - issue_id: shopping_admin.pa49.scope_select_context_change
    target:
      selector: button#store-change-button
      description: the All Websites scope selector button on the customer totals report
      coverage_policy: single
    criterion:
      issue_family: on_input
      wcag_target: WCAG 3.2.2 On Input
    evidence_rule: >-
      The target control (the All Websites scope selector button on the customer totals report)
      changes page context, navigation state, result ordering, or equivalent page state immediately
      after the control value or selection changes, without a separate submit or apply action
      and without prior warning. Merely opening a menu is not sufficient.
```

## Source And Live Check

- This L3 merge source is restricted to a BASE-induced page owner key.
- Completeness is scoped to reviewed Keyboard inventory on that page, not a new full-site audit.
- Current L3 scope is limited to the listed Keyboard assessment items.

## Merge Scope

- Owner key: shopping_admin + PA49 + Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6.
- gold.issues[] contains 2 reviewed issue entries.
