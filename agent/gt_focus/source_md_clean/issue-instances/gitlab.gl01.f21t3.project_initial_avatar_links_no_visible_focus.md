# Issue Instance

```yaml
instance_id: gitlab.gl01.f21t3.project_initial_avatar_links_no_visible_focus
template_id: focus.visible_focus.project_initial_avatar_links_no_visible_focus
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
  selector: .projects-list a.project
  description: the project-row initial-letter avatar links in the GitLab Dashboard project list
  coverage_policy: representative_group

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The project-row initial-letter avatar links receive keyboard focus, but no
    user-perceivable focus indicator is visible while one of those links is
    keyboard-focused. Mouse clicks, JavaScript focus, browser-use overlays, and
    imperceptible computed-style differences do not count as focus evidence.
```

## Selector Check

- Playwright on GL01 resolved `.projects-list a.project` to 14 visible project-row avatar links in the Dashboard project list.
- The matched links are the repeated initial-letter project avatars on the left side of the project rows.
- The source record marks GL01 visible focus as FAIL for the Dashboard `Yours` tab and the project-list initial avatar links.
