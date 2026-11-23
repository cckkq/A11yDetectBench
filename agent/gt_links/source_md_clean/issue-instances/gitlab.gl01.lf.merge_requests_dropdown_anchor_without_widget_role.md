# Issue Instance

```yaml
instance_id: gitlab.gl01.lf.merge_requests_dropdown_anchor_without_widget_role
template_id: links.link_function.gitlab.merge_requests_dropdown_anchor_without_widget_role
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01
  legacy_instance_id: gitlab.gl01.lf.topbar_dropdown_anchor_without_widget_role
  split_from_legacy_group: true

page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: "header a[data-qa-selector='merge_requests_shortcut_button']"
  description: the `Merge requests` anchor element in the GitLab Dashboard top navigation
  coverage_policy: single

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched `Merge requests` anchor element is exposed as a link, but activation opens
    the merge-request menu in place. The element has `data-toggle="dropdown"` and
    no ARIA widget role for the dropdown-control behavior.
```

## Selector Check

- `document.querySelectorAll("header a[data-qa-selector='merge_requests_shortcut_button']")` resolves to one element on GL01.
- The matched element has name `Merge requests`, href `/dashboard/merge_requests?assignee_username=byteblaze`, `data-toggle="dropdown"`, no explicit widget role, and is visible.
- This clean L1 instance is split from legacy grouped instance `gitlab.gl01.lf.topbar_dropdown_anchor_without_widget_role` so that one instance covers one target.
