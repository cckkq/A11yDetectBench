# Merge Instance

```yaml
instance_id: gitlab.explore.link_function
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL95
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: Explore
  start_url: http://localhost:8023/explore
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl95.lf.create_new_dropdown_anchor_without_widget_role
      target:
        selector: 'header a[data-qa-selector=''new_menu_toggle'']'
        description: the `Create new...` anchor element in the GitLab Explore top navigation
        coverage_policy: single
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched `Create new...` anchor element is exposed as a link, but activation
        opens the create menu in place. The element has `data-toggle='dropdown'`
        and no ARIA widget role or expanded state for the dropdown-control behavior.

    - issue_id: gitlab.gl95.lf.merge_requests_dropdown_anchor_without_widget_role
      target:
        selector: 'header a[data-qa-selector=''merge_requests_shortcut_button'']'
        description: the `Merge requests` anchor element in the GitLab Explore top navigation
        coverage_policy: single
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched `Merge requests` anchor element is exposed as a link, but activation
        opens the merge-request menu in place. The element has
        `data-toggle='dropdown'` and no ARIA widget role or expanded state for
        the dropdown-control behavior.
```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL95 states that the main 6.1 Link Function GT failures are the same topbar dropdown-as-link pattern as GL01: `Create new...` and `Merge requests`.
- The GL95 clean atomic instances split the old grouped topbar id into two explicit targets: `create_new_dropdown_anchor_without_widget_role` and `merge_requests_dropdown_anchor_without_widget_role`.
- Fresh live GL95 probe after refreshing GitLab auth found one visible `header a[data-qa-selector='new_menu_toggle']` anchor element and one visible `header a[data-qa-selector='merge_requests_shortcut_button']` anchor element.
- The live probe confirmed both target anchor elements have `data-toggle='dropdown'`, no explicit widget role, and no `aria-expanded` state.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/explore + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for GL95 link function, not one L2 task per topbar dropdown.
- The two entries in `gold.issues[]` preserve the GL95 source-record link-function failure groups already anchored by clean atomic issue instances.
