# Issue Instance

```yaml
instance_id: gitlab.gl96.f21t4.explore_tab_controls_no_visible_focus
template_id: focus.visible_focus.explore_tab_controls_no_visible_focus
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL96

page:
  site: gitlab
  page_name: Explore Topics
  start_url: http://localhost:8023/explore/projects/topics
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: a.nav-link.gl-tab-nav-item[href="/explore/projects/topics"]
  description: the active Topics tab control on the GitLab Explore Topics page
  coverage_policy: single

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The Explore Topics page Topics tab receives keyboard focus, but no distinct
    user-perceivable focus indicator is visible beyond the tab's existing
    selected/current underline state. Mouse clicks, JavaScript focus,
    browser-use overlays, and imperceptible computed-style differences do not
    count as focus evidence.
```

## Selector Check

- Playwright on GL96 resolved `a.nav-link.gl-tab-nav-item[href="/explore/projects/topics"]` to one visible tab with text `Topics`.
- The target is the active `Topics` tab in the shared Projects tab strip on the Explore Topics page, not the missing topic tag list links.
- Fresh-auth keyboard probing reached the tab with sequential Tab navigation; the focused tab kept only the selected/current underline state and did not add a distinct user-perceivable focus indicator.
