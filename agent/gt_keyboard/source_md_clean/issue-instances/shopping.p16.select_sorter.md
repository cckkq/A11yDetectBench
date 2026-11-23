# Issue Instance

```yaml
instance_id: shopping.p16.select_sorter
template_id: keyboard.on_input.native_select_change_triggers_context_change
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P16
page:
  site: shopping
  page_name: Toothbrushes Accessories Category
  start_url: http://localhost:7770/beauty-personal-care/oral-care/toothbrushes-accessories.html
target:
  selector: select#sorter
  description: the Sort By selector on the toothbrushes accessories category page
  coverage_policy: single
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
gold:
  expected_verdict: issue_found
  evidence_rule: The target control (the Sort By selector on the toothbrushes accessories
    category page) changes page context, navigation state, result ordering, or equivalent
    page state immediately after the control value or selection changes, without a separate
    submit or apply action and without prior warning. Merely opening a menu is not sufficient.
```

## Selector Check

- Playwright selector audit: Playwright resolved select#sorter to one visible native select.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
