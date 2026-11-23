# Issue Instance

```yaml
instance_id: shopping.p02.select_limiter
template_id: keyboard.on_input.native_select_change_triggers_context_change
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P02
page:
  site: shopping
  page_name: Order History
  start_url: http://localhost:7770/sales/order/history/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: select#limiter
  description: the Show per page selector on the shopping order history page
  coverage_policy: single
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
gold:
  expected_verdict: issue_found
  evidence_rule: The target control (the Show per page selector on the shopping order history
    page) changes page context, navigation state, result ordering, or equivalent page state
    immediately after the control value or selection changes, without a separate submit or
    apply action and without prior warning. Merely opening a menu is not sufficient.
```

## Selector Check

- Playwright selector audit: Playwright resolved select#limiter to one visible native select.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
