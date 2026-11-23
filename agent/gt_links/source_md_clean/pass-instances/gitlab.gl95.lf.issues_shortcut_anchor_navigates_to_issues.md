# PASS Instance

```yaml
instance_id: gitlab.gl95.lf.issues_shortcut_anchor_navigates_to_issues
template_id: links.link_function.pass.gitlab.issues_shortcut_anchor_navigates_to_issues
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL95
  matched_positive: gitlab.gl95.lf.create_new_dropdown_anchor_without_widget_role

page:
  site: gitlab
  page_name: Explore
  start_url: http://localhost:8023/explore
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'header a[data-qa-selector=''issues_shortcut_button'']'
  description: the Issues shortcut anchor element in the GitLab Explore top navigation
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

- A construction-time selector check confirmed one visible matching Issues shortcut anchor element on GL95.
- A Playwright click probe navigated from `/explore` to `/dashboard/issues?assignee_username=byteblaze`.
