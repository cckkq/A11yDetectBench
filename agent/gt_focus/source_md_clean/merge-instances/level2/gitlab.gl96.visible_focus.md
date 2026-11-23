# Merge Instance

```yaml
instance_id: gitlab.gl96.visible_focus
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL96
  review_status: current_clean_inventory
page:
  site: gitlab
  page_name: Explore Topics
  start_url: http://localhost:8023/explore/projects/topics
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
  assessment_requirement: F.1 Visible Focus
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl96.f21t4.explore_tab_controls_no_visible_focus
    target:
      selector: a.nav-link.gl-tab-nav-item[href="/explore/projects/topics"]
      description: the active Topics tab control on the GitLab Explore Topics page
      coverage_policy: single
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      The Explore Topics page Topics tab receives keyboard focus, but no distinct user-perceivable
      focus indicator is visible beyond the tab's existing selected/current underline state.
      Mouse clicks, JavaScript focus, browser-use overlays, and imperceptible computed-style
      differences do not count as focus evidence.
```

## Source And Live Check

- This L2 merge source contains the current clean Focus inventory for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Focus-specific evidence rules remain in each issue evidence_rule and in the shared Focus prompt/evaluator contract; no extra markdown fields are introduced.

## Merge Scope

- L2 owner key: gitlab + http://localhost:8023/explore/projects/topics + visible_focus + WCAG 2.4.7 Focus Visible.
- gold.issues[] contains 1 reviewed clean-source issue entry.
