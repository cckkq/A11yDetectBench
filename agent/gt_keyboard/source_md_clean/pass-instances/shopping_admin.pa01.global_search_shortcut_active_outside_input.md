# PASS Instance

```yaml
instance_id: shopping_admin.pa01.global_search_shortcut_active_outside_input
template_id: keyboard.character_key.global_search_shortcut_active_outside_input
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
    agent/gt/issue-instances/shopping_admin.pa01.global_search_shortcut_active_outside_input.md
  page_id: PA01
  matched_positive: shopping_admin.pa01.global_search_shortcut_active_outside_input
page:
  site: shopping_admin
  page_name: Admin Dashboard
  start_url: http://localhost:7780/admin/admin/dashboard/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: input#search-global
  description: the Magento Admin global search input targeted by slash and question-mark shortcuts
  coverage_policy: single
criterion:
  issue_family: character_key_shortcuts
  wcag_target: WCAG 2.1.4 Character Key Shortcuts
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa01.global_search_shortcut_active_outside_input`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
