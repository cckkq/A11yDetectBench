# PASS Instance

```yaml
instance_id: shopping_admin.pa05.grid_toolbar_expanded_menu_items_not_tabbable
template_id: keyboard.keyboard_nonreachable.grid_toolbar_expanded_menu_items_not_tabbable
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
    agent/gt/issue-instances/shopping_admin.pa05.grid_toolbar_expanded_menu_items_not_tabbable.md
  page_id: PA05
  matched_positive: shopping_admin.pa05.grid_toolbar_expanded_menu_items_not_tabbable
page:
  site: shopping_admin
  page_name: Invoices Grid
  start_url: http://localhost:7780/admin/sales/invoice/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .admin__data-grid-header .action-menu-item
  description: the visible items in the opened Magento Admin Invoices grid Actions menu
  coverage_policy: representative_group
setup: Open the grid Actions menu before inspecting the expanded menu items.
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa05.grid_toolbar_expanded_menu_items_not_tabbable`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
