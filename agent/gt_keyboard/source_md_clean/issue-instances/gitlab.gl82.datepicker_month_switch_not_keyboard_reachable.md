# Issue Instance

```yaml
instance_id: gitlab.gl82.datepicker_month_switch_not_keyboard_reachable
template_id: keyboard.keyboard_nonreachable.datepicker_month_switch_not_keyboard_reachable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL82
page:
  site: gitlab
  page_name: Value Stream Analytics
  start_url: http://localhost:8023/byteblaze/dotfiles/-/value_stream_analytics?created_after=2026-02-10&created_before=2026-03-11&stage_id=issue&sort=end_event&direction=desc&page=1
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .pika-single:not(.is-hidden) .pika-prev, .pika-single:not(.is-hidden) .pika-next
  description: the previous and next month buttons in the opened Value Stream date-range datepicker
  coverage_policy: representative_group
setup: Open the Value Stream date-range datepicker before inspecting the visible Pika month
  navigation buttons.
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the previous and next month buttons in the opened Value Stream
    date-range datepicker) is visible and pointer-operable or part of an active widget, but
    expected keyboard navigation cannot reach or complete operation of that same target. Reporting
    a different keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: After opening the date-range datepicker, Playwright resolved the non-hidden Pika previous and next buttons.
- Setup for selector visibility: Open the Value Stream date-range datepicker before inspecting the visible Pika month navigation buttons.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
