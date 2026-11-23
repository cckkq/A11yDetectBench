# Merge Instance

```yaml
instance_id: gitlab.gl01.focus_assessment
task_level: level3
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
  assessment_scope: Focus assessment scope F.1-F.6
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

- This L3 merge source uses the full Focus assessment scope F.1-F.6.
- Completeness of `gold.issues[]` is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Current reviewed negative gold for this page only contains the listed F.1/F.5 issues; no F.2/F.3/F.4/F.6 gold is added here.

## Merge Scope

- L3 owner key: gitlab + http://localhost:8023/ + Focus assessment scope F.1-F.6.
- gold.issues[] contains 2 reviewed clean-source issue entries.
