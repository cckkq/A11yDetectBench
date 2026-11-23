# Issue Instance

```yaml
instance_id: reddit.rd02.submissions_toggle_context_change
template_id: keyboard.on_input.native_select_change_triggers_context_change
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD02
page:
  site: reddit
  page_name: Forums
  start_url: http://localhost:9999/forums
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: 'button[aria-label="Sort by: Submissions"]'
  description: the Submissions sort toggle in the Reddit forums page navigation
  coverage_policy: single
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
gold:
  expected_verdict: issue_found
  evidence_rule: The target control (the Submissions sort toggle in the Reddit forums page
    navigation) changes page context, navigation state, result ordering, or equivalent page
    state immediately after the control value or selection changes, without a separate submit
    or apply action and without prior warning. Merely opening a menu is not sufficient.
```

## Selector Check

- Playwright selector audit: Playwright resolved button[aria-label="Sort by: Submissions"] to one visible sort toggle button.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
