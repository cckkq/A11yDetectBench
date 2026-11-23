# PASS Instance

```yaml
instance_id: gitlab.gl01.lf.issues_shortcut_anchor_navigates_to_issues
template_id: links.link_function.pass.gitlab.issues_shortcut_anchor_navigates_to_issues
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01
  matched_positive: gitlab.gl01.lf.create_new_dropdown_anchor_without_widget_role

page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'header a[data-qa-selector=''issues_shortcut_button'']'
  description: the Issues shortcut anchor element in the GitLab Dashboard top navigation
  coverage_policy: single

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element has the accessible name `Issues`, href
    `/dashboard/issues?assignee_username=byteblaze`, and `data-toggle="tooltip"`.
    Activation navigates to the Issues dashboard rather than opening an in-place
    dropdown menu, so the Link Function issue is not present for this target.
```

## Selector Check

- A construction-time selector check confirmed one visible matching Issues shortcut anchor element on GL01.
- A Playwright click probe navigated from `http://localhost:8023/` to `/dashboard/issues?assignee_username=byteblaze`.
