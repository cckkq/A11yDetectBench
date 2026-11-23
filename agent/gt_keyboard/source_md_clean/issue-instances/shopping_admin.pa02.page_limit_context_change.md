# Issue Instance

```yaml
instance_id: shopping_admin.pa02.page_limit_context_change
template_id: keyboard.on_input.native_select_change_triggers_context_change
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA02
page:
  site: shopping_admin
  page_name: Notifications
  start_url: http://localhost:7780/admin/admin/notification/index/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: select#notificationGrid_page-limit
  description: the notifications grid page-limit selector
  coverage_policy: single
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
gold:
  expected_verdict: issue_found
  evidence_rule: The target control (the notifications grid page-limit selector) changes page
    context, navigation state, result ordering, or equivalent page state immediately after
    the control value or selection changes, without a separate submit or apply action and
    without prior warning. Merely opening a menu is not sufficient.
```

## Selector Check

- Playwright selector audit: Playwright resolved select#notificationGrid_page-limit to one visible native select.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
