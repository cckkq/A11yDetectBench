# Issue Instance

```yaml
instance_id: shopping_admin.pa04.f21t6a.grid_small_selectors_no_visible_focus
template_id: focus.visible_focus.grid_small_selectors_no_visible_focus
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04

page:
  site: shopping_admin
  page_name: Orders
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: .admin__data-grid-filters-current button.action-remove
  description: the Remove icon button next to the Purchase Date active filter in the Orders grid
  coverage_policy: single

setup: Ensure the Orders grid has an active Purchase Date filter row before checking the Remove icon; create that filter state through the grid filter controls if it is absent.

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The Orders grid active-filter Remove icon receives keyboard focus, but no
    user-perceivable focus indicator is visible while that icon button is
    keyboard-focused. Mouse clicks, JavaScript focus, browser-use overlays, and
    imperceptible computed-style differences do not count as focus evidence.
```

## Selector Check

- Playwright on PA04 observed `.admin__data-grid-filters-current button.action-remove` as one visible `Remove` button in the Active filters area.
- The page also exposed `created_at[from]` and `created_at[to]` Purchase Date filter inputs used to create the active filter state.
- The source record identifies the `Purchase Date: Invalid date - ...` active-filter Remove/X icon as the target.
