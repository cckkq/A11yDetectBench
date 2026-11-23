# Issue Instance

```yaml
instance_id: shopping_admin.pa58.f21t6b.admin_action_buttons_no_visible_focus
template_id: focus.visible_focus.admin_action_buttons_no_visible_focus
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA58
page:
  site: shopping_admin
  page_name: Stores
  start_url: http://localhost:7780/admin/admin/system_store/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: button#add_store, button#add_group
  description: the Create Store View and Create Store top-toolbar buttons on the Stores page
  coverage_policy: representative_group
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
gold:
  expected_verdict: issue_found
  evidence_rule: The Create Store View and Create Store buttons receive keyboard focus, but no user-perceivable focus indicator is visible while one is keyboard-focused.
```

## Selector Check

- Playwright on PA58 resolved `button#add_store` to one visible `Create Store View` button.
- Playwright on PA58 resolved `button#add_group` to one visible `Create Store` button.
