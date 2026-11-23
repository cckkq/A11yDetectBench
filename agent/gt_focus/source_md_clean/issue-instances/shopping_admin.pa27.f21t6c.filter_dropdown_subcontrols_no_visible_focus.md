# Issue Instance

```yaml
instance_id: shopping_admin.pa27.f21t6c.filter_dropdown_subcontrols_no_visible_focus
template_id: focus.visible_focus.filter_dropdown_subcontrols_no_visible_focus
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA27
page:
  site: shopping_admin
  page_name: CMS Pages
  start_url: http://localhost:7780/admin/cms/page/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .admin__data-grid-filters > .admin__form-field:nth-child(8) .admin__action-multiselect-wrap, .admin__data-grid-filters > .admin__form-field:nth-child(11) .admin__action-multiselect-wrap, .admin__data-grid-filters > .admin__form-field:nth-child(12) .admin__action-multiselect-wrap
  description: the Asset, Layout, and Status subcontrols inside the expanded Filter panel of the CMS Pages grid
  coverage_policy: representative_group
setup: Ensure the CMS Pages filter panel is expanded before checking the target subcontrols.
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
gold:
  expected_verdict: issue_found
  evidence_rule: The Asset, Layout, and Status filter subcontrols receive keyboard focus, but no user-perceivable focus indicator is visible while one is keyboard-focused.
```

## Selector Check

- Playwright on PA27 clicked `button[data-action=grid-filter-expand]` and expanded the CMS Pages filter panel.
- After expansion, the target selector resolved to three visible controls with field texts `Asset Select...`, `Layout Select...`, and `Status Select...`.
