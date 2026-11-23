# PASS Instance

```yaml
instance_id: shopping_admin.pa62.f21t6c.filter_dropdown_subcontrols_no_visible_focus
template_id: focus.visible_focus.filter_dropdown_subcontrols_no_visible_focus
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA62
  matched_positive: shopping_admin.pa62.f21t6c.filter_dropdown_subcontrols_no_visible_focus
page:
  site: shopping_admin
  page_name: Sources
  start_url: http://localhost:7780/admin/inventory/source/index/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: >-
    .admin__data-grid-filters > .admin__form-field:nth-child(5) .admin__action-multiselect-wrap,
    .admin__data-grid-filters > .admin__form-field:nth-child(7) .admin__action-multiselect-wrap
  description: >-
    the Is Enabled and Pickup Location subcontrols inside the expanded Filter panel of the
    Sources grid
  coverage_policy: representative_group
setup: Ensure the Sources filter panel is expanded before checking the target subcontrols.
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to add
    a user-perceivable focus indicator for the same keyboard-focused or keyboard-current target.
    A reported visible-focus issue on this matched target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa62.f21t6c.filter_dropdown_subcontrols_no_visible_focus`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Focus runtime counterfactual patch; the target remains the same keyboard path.
