# Issue Instance

```yaml
instance_id: gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus
template_id: focus.visible_focus.explore_tab_controls_no_visible_focus
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01

page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: a.shortcuts-activity.nav-link[href="/dashboard/projects"]
  description: the Yours tab control at the top of the GitLab Dashboard page
  coverage_policy: single

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The Dashboard Yours tab receives keyboard focus, but no user-perceivable
    focus indicator is visible while that tab is keyboard-focused. Mouse
    clicks, JavaScript focus, browser-use overlays, and imperceptible
    computed-style differences do not count as focus evidence.
```

## Selector Check

- Playwright on GL01 resolved `a.shortcuts-activity.nav-link[href="/dashboard/projects"]` to one visible tab with text `Yours 14`.
- The selector targets the Dashboard top tab named by the legacy Focus task, not the project avatar links or top navbar.
- The source record marks GL01 visible focus as FAIL for the Dashboard `Yours` tab and the project-list initial avatar links.
