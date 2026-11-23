# Issue Instance

```yaml
instance_id: gitlab.gl15.datepicker_month_switch_not_keyboard_reachable
template_id: keyboard.keyboard_nonreachable.datepicker_month_switch_not_keyboard_reachable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL15
page:
  site: gitlab
  page_name: Personal Access Tokens
  start_url: http://localhost:8023/-/profile/personal_access_tokens
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .pika-single .pika-prev, .pika-single .pika-next
  description: the previous and next month buttons in the opened personal access token expiration
    datepicker
  coverage_policy: representative_group
setup: 'Open the Expiration date datepicker by activating the #personal_access_token_expires_at
  field before inspecting the month navigation buttons.'
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the previous and next month buttons in the opened personal access
    token expiration datepicker) is visible and pointer-operable or part of an active widget,
    but expected keyboard navigation cannot reach or complete operation of that same target.
    Reporting a different keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: After opening #personal_access_token_expires_at, Playwright resolved .pika-single .pika-prev and .pika-single .pika-next to one visible button each.
- Setup for selector visibility: Open the Expiration date datepicker by activating the #personal_access_token_expires_at field before inspecting the month navigation buttons.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
