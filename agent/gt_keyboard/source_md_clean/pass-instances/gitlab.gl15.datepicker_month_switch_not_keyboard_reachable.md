# PASS Instance

```yaml
instance_id: gitlab.gl15.datepicker_month_switch_not_keyboard_reachable
template_id: keyboard.keyboard_nonreachable.datepicker_month_switch_not_keyboard_reachable
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL15
  matched_positive: gitlab.gl15.datepicker_month_switch_not_keyboard_reachable
page:
  site: gitlab
  page_name: Personal Access Tokens
  start_url: http://localhost:8023/-/profile/personal_access_tokens
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .pika-single .pika-prev, .pika-single .pika-next
  description: >-
    the previous and next month buttons in the opened personal access token expiration datepicker
  coverage_policy: representative_group
setup: >-
  Open the Expiration date datepicker by activating the #personal_access_token_expires_at
  field before inspecting the month navigation buttons.
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

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl15.datepicker_month_switch_not_keyboard_reachable`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
