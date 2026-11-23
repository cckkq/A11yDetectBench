# Issue Instance

```yaml
instance_id: shopping_admin.pa04.grid_toolbar_expanded_menu_items_not_tabbable
template_id: keyboard.keyboard_nonreachable.grid_toolbar_expanded_menu_items_not_tabbable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04
page:
  site: shopping_admin
  page_name: Orders Grid
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .admin__data-grid-header .action-menu-item
  description: the visible items in the opened Magento Admin Orders grid Actions menu
  coverage_policy: representative_group
setup: Open the grid Actions menu before inspecting the expanded menu items.
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the visible items in the opened Magento Admin Orders grid Actions
    menu) is visible and pointer-operable or part of an active widget, but expected keyboard
    navigation cannot reach or complete operation of that same target. Reporting a different
    keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: After opening the Orders grid Actions menu, Playwright resolved .admin__data-grid-header .action-menu-item to visible menu items with tabindex -1.
- Setup for selector visibility: Open the grid Actions menu before inspecting the expanded menu items.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
