# Issue Instance

```yaml
instance_id: shopping_admin.pa69.mouse_operable_data_row_controls_not_tabbable
template_id: keyboard.keyboard_nonreachable.mouse_operable_data_row_controls_not_tabbable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA69
page:
  site: shopping_admin
  page_name: Attribute Sets
  start_url: http://localhost:7780/admin/catalog/product_set/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: '#setGrid_table tbody tr[title]'
  description: the pointer-operable Attribute Sets grid rows
  coverage_policy: representative_group
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the pointer-operable Attribute Sets grid rows) is visible and
    pointer-operable or part of an active widget, but expected keyboard navigation cannot
    reach or complete operation of that same target. Reporting a different keyboard issue
    on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: Playwright resolved #setGrid_table tbody tr[title] to eight visible titled grid rows with tabindex -1.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
