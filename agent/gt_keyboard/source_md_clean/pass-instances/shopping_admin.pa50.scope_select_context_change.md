# PASS Instance

```yaml
instance_id: shopping_admin.pa50.scope_select_context_change
template_id: keyboard.on_input.custom_selector_change_triggers_context_change
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA50
  matched_positive: shopping_admin.pa50.scope_select_context_change
page:
  site: shopping_admin
  page_name: Customer Order Count Report
  start_url: http://localhost:7780/admin/reports/report_customer/orders/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: button#store-change-button
  description: the All Websites scope selector button on the customer orders report
  coverage_policy: single
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa50.scope_select_context_change`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
