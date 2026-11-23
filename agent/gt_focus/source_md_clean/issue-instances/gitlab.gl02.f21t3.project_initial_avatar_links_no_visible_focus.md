# Issue Instance

```yaml
instance_id: gitlab.gl02.f21t3.project_initial_avatar_links_no_visible_focus
template_id: focus.visible_focus.project_initial_avatar_links_no_visible_focus
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL02

page:
  site: gitlab
  page_name: byteblaze user profile
  start_url: http://localhost:8023/byteblaze
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: .projects-list a.project
  description: the large initial-letter avatar links repeated on the byteblaze user profile page
  coverage_policy: representative_group

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The large initial-letter avatar links receive keyboard focus, but no
    user-perceivable focus indicator is visible while one of those links is
    keyboard-focused. Mouse clicks, JavaScript focus, browser-use overlays, and
    imperceptible computed-style differences do not count as focus evidence.
```

## Selector Check

- Playwright on GL02 resolved `.projects-list a.project` to 10 visible large initial-letter avatar links on the byteblaze profile page.
- The matched links correspond to the `D`, `S`, and `G` style project avatar links named by the source record.
- The source record marks GL02 visible focus as FAIL for these repeated large initial-letter avatar links.
