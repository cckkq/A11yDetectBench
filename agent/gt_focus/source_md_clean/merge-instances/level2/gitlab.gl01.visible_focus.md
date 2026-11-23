# Merge Instance

```yaml
instance_id: gitlab.gl01.visible_focus
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01
  review_status: current_clean_inventory
page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
  assessment_requirement: F.1 Visible Focus
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl01.f21t3.project_initial_avatar_links_no_visible_focus
    target:
      selector: .projects-list a.project
      description: the project-row initial-letter avatar links in the GitLab Dashboard project
        list
      coverage_policy: representative_group
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      The project-row initial-letter avatar links receive keyboard focus, but no user-perceivable
      focus indicator is visible while one of those links is keyboard-focused. Mouse clicks,
      JavaScript focus, browser-use overlays, and imperceptible computed-style differences
      do not count as focus evidence.
  - issue_id: gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus
    target:
      selector: a.shortcuts-activity.nav-link[href="/dashboard/projects"]
      description: the Yours tab control at the top of the GitLab Dashboard page
      coverage_policy: single
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      The Dashboard Yours tab receives keyboard focus, but no user-perceivable focus indicator
      is visible while that tab is keyboard-focused. Mouse clicks, JavaScript focus, browser-use
      overlays, and imperceptible computed-style differences do not count as focus evidence.
```

## Source And Live Check

- This L2 merge source contains the current clean Focus inventory for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Focus-specific evidence rules remain in each issue evidence_rule and in the shared Focus prompt/evaluator contract; no extra markdown fields are introduced.

## Merge Scope

- L2 owner key: gitlab + http://localhost:8023/ + visible_focus + WCAG 2.4.7 Focus Visible.
- gold.issues[] contains 2 reviewed clean-source issue entries.
