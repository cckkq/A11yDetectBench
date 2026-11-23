# Issue Instance

```yaml
instance_id: gitlab.gl01.custom_selector_context_change
template_id: keyboard.on_input.custom_selector_change_triggers_context_change
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01
page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: button#sort-projects-dropdown
  description: the project sort dropdown on the GitLab Dashboard
  coverage_policy: single
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
gold:
  expected_verdict: issue_found
  evidence_rule: The target control (the project sort dropdown on the GitLab Dashboard) changes
    page context, navigation state, result ordering, or equivalent page state immediately
    after the control value or selection changes, without a separate submit or apply action
    and without prior warning. Merely opening a menu is not sufficient.
```

## Selector Check

- Playwright selector audit: Playwright resolved button#sort-projects-dropdown to one visible custom sort dropdown button.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
