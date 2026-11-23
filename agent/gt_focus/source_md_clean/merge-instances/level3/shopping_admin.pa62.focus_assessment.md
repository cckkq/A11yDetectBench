# Merge Instance

```yaml
instance_id: shopping_admin.pa62.focus_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA62
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Sources
  start_url: http://localhost:7780/admin/inventory/source/index/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Focus assessment scope F.1-F.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa62.f21t6c.filter_dropdown_subcontrols_no_visible_focus
    target:
      selector: >-
        .admin__data-grid-filters > .admin__form-field:nth-child(5) .admin__action-multiselect-wrap,
        .admin__data-grid-filters > .admin__form-field:nth-child(7) .admin__action-multiselect-wrap
      description: >-
        the Is Enabled and Pickup Location subcontrols inside the expanded Filter panel of
        the Sources grid
      coverage_policy: representative_group
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      The Is Enabled and Pickup Location filter subcontrols receive keyboard focus, but no
      user-perceivable focus indicator is visible while one is keyboard-focused.
```

## Source And Live Check

- This L3 merge source uses the full Focus assessment scope F.1-F.6.
- Completeness of `gold.issues[]` is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Current reviewed negative gold for this page only contains the listed F.1/F.5 issues; no F.2/F.3/F.4/F.6 gold is added here.

## Merge Scope

- L3 owner key: shopping_admin + http://localhost:7780/admin/inventory/source/index/ + Focus assessment scope F.1-F.6.
- gold.issues[] contains 1 reviewed clean-source issue entry.
