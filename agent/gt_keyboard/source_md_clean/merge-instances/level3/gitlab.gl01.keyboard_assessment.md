# Merge Instance

```yaml
instance_id: gitlab.gl01.keyboard_assessment
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
  assessment_scope: Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl01.custom_selector_context_change
    target:
      selector: button#sort-projects-dropdown
      description: the project sort dropdown on the GitLab Dashboard
      coverage_policy: single
    criterion:
      issue_family: on_input
      wcag_target: WCAG 3.2.2 On Input
    evidence_rule: >-
      The target control (the project sort dropdown on the GitLab Dashboard) changes page
      context, navigation state, result ordering, or equivalent page state immediately after
      the control value or selection changes, without a separate submit or apply action and
      without prior warning. Merely opening a menu is not sufficient.
```

## Source And Live Check

- This L3 merge source is restricted to a BASE-induced page owner key.
- Completeness is scoped to reviewed Keyboard inventory on that page, not a new full-site audit.
- Current L3 scope is limited to the listed Keyboard assessment items.

## Merge Scope

- Owner key: gitlab + GL01 + Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6.
- gold.issues[] contains 1 reviewed issue entries.
