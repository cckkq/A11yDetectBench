# Issue Instance

```yaml
instance_id: shopping_admin.pa11.category_tree_not_keyboard_reachable
template_id: keyboard.keyboard_nonreachable.category_tree_not_keyboard_reachable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA11
page:
  site: shopping_admin
  page_name: Categories
  start_url: http://localhost:7780/admin/catalog/category/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: '#tree-div a'
  description: the visible category tree node anchors under Collapse All and Expand All
  coverage_policy: representative_group
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the visible category tree node anchors under Collapse All and
    Expand All) is visible and pointer-operable or part of an active widget, but expected
    keyboard navigation cannot reach or complete operation of that same target. Reporting
    a different keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: Playwright resolved #tree-div a to nine visible category tree anchors.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
