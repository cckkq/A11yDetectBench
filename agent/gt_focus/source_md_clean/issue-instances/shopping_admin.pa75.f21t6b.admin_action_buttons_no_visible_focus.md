# Issue Instance

```yaml
instance_id: shopping_admin.pa75.f21t6b.admin_action_buttons_no_visible_focus
template_id: focus.visible_focus.admin_action_buttons_no_visible_focus
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA75
page:
  site: shopping_admin
  page_name: Integrations
  start_url: http://localhost:7780/admin/admin/integration/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: button#edit.action.edit, button#delete.action.delete
  description: the row-level Edit and Remove action buttons in the Integrations list
  coverage_policy: representative_group
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
gold:
  expected_verdict: issue_found
  evidence_rule: The Integrations row-level Edit and Remove buttons receive keyboard focus, but no user-perceivable focus indicator is visible while one is keyboard-focused.
```

## Selector Check

- Playwright on PA75 resolved `button#edit.action.edit` to one visible row-level button with title `Edit`.
- Playwright on PA75 resolved `button#delete.action.delete` to one visible row-level button with title `Remove`.
