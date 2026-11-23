# Issue Instance

```yaml
instance_id: gitlab.gl02.lp.dashboard_projects_view_all_without_section_context
template_id: links.link_purpose.gitlab.dashboard_overview_view_all_without_section_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL02

page:
  site: gitlab
  page_name: User Profile
  start_url: http://localhost:8023/byteblaze
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: "main#content-body a.js-view-all[href='/users/byteblaze/projects']"
  description: the `View all` anchor element in the projects overview section
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link has computed name `View all` and no description. Its link
    name does not identify the projects destination, and the visual `Personal
    projects` heading is not supplied as a programmatically determined link
    context.
```

## Selector Check

- `document.querySelectorAll("main#content-body a.js-view-all[href='/users/byteblaze/projects']")` resolves to one element on GL02.
- The matched element is visible, has text `View all`, href `/users/byteblaze/projects`, no `aria-label`, and no `title`.
- The old probe reports AX role `link`, AX name `View all`, and no accessible description.
