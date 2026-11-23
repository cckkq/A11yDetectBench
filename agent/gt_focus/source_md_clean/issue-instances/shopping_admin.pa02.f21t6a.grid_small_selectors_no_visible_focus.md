# Issue Instance

```yaml
instance_id: shopping_admin.pa02.f21t6a.grid_small_selectors_no_visible_focus
template_id: focus.visible_focus.grid_small_selectors_no_visible_focus
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA02

page:
  site: shopping_admin
  page_name: Notifications
  start_url: http://localhost:7780/admin/admin/notification/index/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#notificationGrid_massaction-mass-select'
  description: the Mass-action Select All small selector at the top of the Notifications grid
  coverage_policy: single

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The Notifications grid Mass-action Select All selector receives keyboard
    focus, but no user-perceivable focus indicator is visible while it is
    keyboard-focused. Mouse clicks, JavaScript focus, browser-use overlays, and
    imperceptible computed-style differences do not count as focus evidence.
```

## Selector Check

- Playwright on PA02 resolved `#notificationGrid_massaction-mass-select` to one visible select control.
- The matched control text included `Select All Unselect All Select Visible Unselect Visible`.
- The source record and legacy task both identify this Notifications grid Mass-action small selector as the target.
