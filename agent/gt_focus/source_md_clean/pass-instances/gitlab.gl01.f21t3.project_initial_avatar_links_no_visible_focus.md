# PASS Instance

```yaml
instance_id: gitlab.gl01.f21t3.project_initial_avatar_links_no_visible_focus
template_id: focus.visible_focus.project_initial_avatar_links_no_visible_focus
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01
  matched_positive: gitlab.gl01.f21t3.project_initial_avatar_links_no_visible_focus
page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .projects-list a.project
  description: the project-row initial-letter avatar links in the GitLab Dashboard project
    list
  coverage_policy: representative_group
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to add
    a user-perceivable focus indicator for the same keyboard-focused or keyboard-current target.
    A reported visible-focus issue on this matched target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl01.f21t3.project_initial_avatar_links_no_visible_focus`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Focus runtime counterfactual patch; the target remains the same keyboard path.
