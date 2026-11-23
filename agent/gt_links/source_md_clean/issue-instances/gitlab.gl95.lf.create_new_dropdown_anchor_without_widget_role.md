# Issue Instance

```yaml
instance_id: gitlab.gl95.lf.create_new_dropdown_anchor_without_widget_role
template_id: links.link_function.gitlab.create_new_dropdown_anchor_without_widget_role
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL95
  legacy_instance_id: gitlab.gl95.lf.topbar_dropdown_anchor_without_widget_role
  split_from_legacy_group: true

page:
  site: gitlab
  page_name: Explore
  start_url: http://localhost:8023/explore
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: "header a[data-qa-selector='new_menu_toggle']"
  description: the `Create new...` anchor element in the GitLab Explore top navigation
  coverage_policy: single

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched `Create new...` anchor element is exposed as a link, but activation opens
    the create menu in place. The element has `data-toggle="dropdown"` and
    no ARIA widget role for the dropdown-control behavior.
```

## Selector Check

- `document.querySelectorAll("header a[data-qa-selector='new_menu_toggle']")` resolves to one element on GL95.
- The matched element has name `Create new...`, href `/projects/new`, `data-toggle="dropdown"`, no explicit widget role, and is visible.
- This clean L1 instance is split from legacy grouped instance `gitlab.gl95.lf.topbar_dropdown_anchor_without_widget_role` so that one instance covers one target.
