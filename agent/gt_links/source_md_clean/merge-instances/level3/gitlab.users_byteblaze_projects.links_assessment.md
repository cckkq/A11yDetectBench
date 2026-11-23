# Merge Instance

```yaml
instance_id: gitlab.users_byteblaze_projects.links_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL06
  review_status: source_and_live_checked
page:
  site: gitlab
  page_name: User Projects
  start_url: http://localhost:8023/users/byteblaze/projects
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl06.lf.create_new_dropdown_anchor_without_widget_role
    target:
      selector: header a[data-qa-selector='new_menu_toggle']
      description: the `Create new...` anchor element in the GitLab User Projects top navigation
      coverage_policy: single
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched `Create new...` anchor element is exposed as a link, but activation opens the create menu in place.
      The element has `data-toggle='dropdown'`, no ARIA widget role, and no `aria-expanded` state for the dropdown-control
      behavior.
  - issue_id: gitlab.gl06.lf.merge_requests_dropdown_anchor_without_widget_role
    target:
      selector: header a[data-qa-selector='merge_requests_shortcut_button']
      description: the `Merge requests` anchor element in the GitLab User Projects top navigation
      coverage_policy: single
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched `Merge requests` anchor element is exposed as a link, but activation opens the merge-request menu in
      place. The element has `data-toggle='dropdown'`, no ARIA widget role, and no `aria-expanded` state for the dropdown-control
      behavior.
  - issue_id: gitlab.gl06.lp.empty_gravatar_avatar_anchor_without_name
    target:
      selector: main#content-body .avatar-holder > a[href*='gravatar.com/avatar']
      description: the profile header external Gravatar avatar anchor element on the user projects page
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched avatar anchor element has an empty accessible name. Its child image has empty `alt`, and no aria label,
      title, or description provides the external Gravatar link purpose.
  - issue_id: gitlab.gl06.lp.profile_rss_subscribe_anchor_without_target_context
    target:
      selector: main#content-body a[title='Subscribe'][href*='.atom'], main#content-body a[aria-label='Subscribe'][href*='.atom']
      description: the `Subscribe` RSS feed anchor element on the user projects page
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched feed link is named only `Subscribe`. The name does not identify that the link subscribes to
      the Byte Blaze user feed, and the feed target is not provided as programmatically determined link context.
```

## Source And Live Check

- This L3 source reuses reviewed L2 merge source files for the same page where applicable:
  - `agent/gt_links/source_md_clean/merge-instances/level2/gitlab.users_byteblaze_projects.link_purpose.md` (`link_purpose`, 2 issues)
- This L3 source also includes L3-owned link-function issues from the source record and live DOM review; these do not expand Merge L2 scope.
- `gitlab-link-purpose-record.md` GL06 states that the main 6.1 Link Function GT failures are L01 `Create new...` and L03 `Merge requests` dropdown-as-link anchor elements.
- Fresh live L3 probe after refreshing GitLab auth found one visible `header a[data-qa-selector='new_menu_toggle']` anchor element and one visible `header a[data-qa-selector='merge_requests_shortcut_button']` anchor element on this page.
- The live probe confirmed both target anchor elements have `data-toggle='dropdown'`, no explicit widget role, and no `aria-expanded` state.
- Candidate-outside `Help` / user-menu dropdowns remain coverage gaps and are not added to this L3 inventory.

## Merge Scope

- L3 owner key: `gitlab + http://localhost:8023/users/byteblaze/projects`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 4 issues: 2 link_function and 2 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
