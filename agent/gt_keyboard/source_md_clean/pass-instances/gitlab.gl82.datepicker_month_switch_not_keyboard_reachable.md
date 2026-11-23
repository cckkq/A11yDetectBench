# PASS Instance

```yaml
instance_id: gitlab.gl82.datepicker_month_switch_not_keyboard_reachable
template_id: keyboard.keyboard_nonreachable.datepicker_month_switch_not_keyboard_reachable
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL82
  matched_positive: gitlab.gl82.datepicker_month_switch_not_keyboard_reachable
page:
  site: gitlab
  page_name: Value Stream Analytics
  start_url: >-
    http://localhost:8023/byteblaze/dotfiles/-/value_stream_analytics?created_after=2026-02-10&created_before=2026-03-11&stage_id=issue&sort=end_event&direction=desc&page=1
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .pika-single:not(.is-hidden) .pika-prev, .pika-single:not(.is-hidden) .pika-next
  description: the previous and next month buttons in the opened Value Stream date-range datepicker
  coverage_policy: representative_group
setup: >-
  Open the Value Stream date-range datepicker before inspecting the visible Pika month navigation
  buttons.
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl82.datepicker_month_switch_not_keyboard_reachable`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
