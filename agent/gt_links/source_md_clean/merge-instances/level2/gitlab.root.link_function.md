# Merge Instance

```yaml
instance_id: gitlab.root.link_function
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl01.lf.create_new_dropdown_anchor_without_widget_role
      target:
        selector: 'header a[data-qa-selector=''new_menu_toggle'']'
        description: the `Create new...` anchor element in the GitLab Dashboard top navigation
        coverage_policy: single
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched `Create new...` anchor element is exposed as a link, but activation
        opens the create menu in place. The element has `data-toggle='dropdown'`
        and no ARIA widget role for the dropdown-control behavior.

    - issue_id: gitlab.gl01.lf.merge_requests_dropdown_anchor_without_widget_role
      target:
        selector: 'header a[data-qa-selector=''merge_requests_shortcut_button'']'
        description: the `Merge requests` anchor element in the GitLab Dashboard top navigation
        coverage_policy: single
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched `Merge requests` anchor element is exposed as a link, but activation
        opens the merge-request menu in place. The element has
        `data-toggle='dropdown'` and no ARIA widget role for the dropdown-control
        behavior.

```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL01 states that the main 6.1 Link Function GT failures are L01 `Create new...` and L03 `Merge requests` dropdown-as-link anchor elements.
- The same GL01 record states L02 `Issues` and L04 `To-Do List` are real navigation links and should not be included.
- The record states `Help` and user-menu dropdowns are Beyond-Insights coverage gaps, not part of the main GT verdict.
- Fresh live GL01 probe after refreshing GitLab auth found one visible `header a[data-qa-selector='new_menu_toggle']` anchor element and one visible `header a[data-qa-selector='merge_requests_shortcut_button']` anchor element.
- The live probe confirmed both target anchor elements have `data-toggle='dropdown'` and no explicit widget role.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/ + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for GL01 link function, not one L2 task per topbar dropdown.
- The two entries in `gold.issues[]` preserve all GL01 main source-record link-function failure groups.
