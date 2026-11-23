# Merge Instance

```yaml
instance_id: shopping_admin.pa04.focus_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Orders
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Focus assessment scope F.1-F.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa04.f21t6a.grid_small_selectors_no_visible_focus
    target:
      selector: .admin__data-grid-filters-current button.action-remove
      description: the Remove icon button next to the Purchase Date active filter in the Orders
        grid
      coverage_policy: single
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      The Orders grid active-filter Remove icon receives keyboard focus, but no user-perceivable
      focus indicator is visible while that icon button is keyboard-focused. Mouse clicks,
      JavaScript focus, browser-use overlays, and imperceptible computed-style differences
      do not count as focus evidence.
```

## Source And Live Check

- This L3 merge source uses the full Focus assessment scope F.1-F.6.
- Completeness of `gold.issues[]` is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Current reviewed negative gold for this page only contains the listed F.1/F.5 issues; no F.2/F.3/F.4/F.6 gold is added here.

## Merge Scope

- L3 owner key: shopping_admin + http://localhost:7780/admin/sales/order/ + Focus assessment scope F.1-F.6.
- gold.issues[] contains 1 reviewed clean-source issue entry.
