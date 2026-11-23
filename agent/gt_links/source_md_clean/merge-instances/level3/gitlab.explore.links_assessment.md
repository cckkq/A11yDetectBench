# Merge Instance

```yaml
instance_id: gitlab.explore.links_assessment
task_level: level3
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
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl95.lf.create_new_dropdown_anchor_without_widget_role
    target:
      selector: header a[data-qa-selector='new_menu_toggle']
      description: the `Create new...` anchor element in the GitLab Explore top navigation
      coverage_policy: single
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched `Create new...` anchor element is exposed as a link, but activation opens the create menu in place.
      The element has `data-toggle='dropdown'` and no ARIA widget role or expanded state for the dropdown-control behavior.
  - issue_id: gitlab.gl95.lf.merge_requests_dropdown_anchor_without_widget_role
    target:
      selector: header a[data-qa-selector='merge_requests_shortcut_button']
      description: the `Merge requests` anchor element in the GitLab Explore top navigation
      coverage_policy: single
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched `Merge requests` anchor element is exposed as a link, but activation opens the merge-request menu in
      place. The element has `data-toggle='dropdown'` and no ARIA widget role or expanded state for the dropdown-control behavior.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `gitlab + http://localhost:8023/explore`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 2 issues: 2 link_function.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
