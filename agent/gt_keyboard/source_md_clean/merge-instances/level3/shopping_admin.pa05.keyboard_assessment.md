# Merge Instance

```yaml
instance_id: shopping_admin.pa05.keyboard_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA05
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Invoices Grid
  start_url: http://localhost:7780/admin/sales/invoice/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa05.grid_toolbar_expanded_menu_items_not_tabbable
    target:
      selector: .admin__data-grid-header .action-menu-item
      description: the visible items in the opened Magento Admin Invoices grid Actions menu
      coverage_policy: representative_group
    criterion:
      issue_family: keyboard_nonreachable
      wcag_target: WCAG 2.1.1 Keyboard
    evidence_rule: >-
      The target (the visible items in the opened Magento Admin Invoices grid Actions menu)
      is visible and pointer-operable or part of an active widget, but expected keyboard navigation
      cannot reach or complete operation of that same target. Reporting a different keyboard
      issue on the page does not satisfy this rule.
```

## Source And Live Check

- This L3 merge source is restricted to a BASE-induced page owner key.
- Completeness is scoped to reviewed Keyboard inventory on that page, not a new full-site audit.
- Current L3 scope is limited to the listed Keyboard assessment items.

## Merge Scope

- Owner key: shopping_admin + PA05 + Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6.
- gold.issues[] contains 1 reviewed issue entries.
