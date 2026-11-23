# Merge Instance

```yaml
instance_id: shopping_admin.pa62.visible_focus
task_level: level2
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
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
  assessment_requirement: F.1 Visible Focus
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

- This L2 merge source contains the current clean Focus inventory for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Focus-specific evidence rules remain in each issue evidence_rule and in the shared Focus prompt/evaluator contract; no extra markdown fields are introduced.

## Merge Scope

- L2 owner key: shopping_admin + http://localhost:7780/admin/inventory/source/index/ + visible_focus + WCAG 2.4.7 Focus Visible.
- gold.issues[] contains 1 reviewed clean-source issue entry.
