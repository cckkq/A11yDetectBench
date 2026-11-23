# Issue Instance

```yaml
instance_id: shopping_admin.pa11.collapsible_panel_expanded_content_partially_not_tabbable
template_id: keyboard.keyboard_nonreachable.collapsible_panel_expanded_content_partially_not_tabbable
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
  selector: '#ui-datepicker-div .ui-datepicker-prev, #ui-datepicker-div .ui-datepicker-next'
  description: the previous and next month links in the datepicker opened from the Schedule
    Design Update panel
  coverage_policy: representative_group
setup: Expand the Schedule Design Update panel, then open one of its datepicker trigger buttons
  before inspecting the datepicker month links.
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the previous and next month links in the datepicker opened from
    the Schedule Design Update panel) is visible and pointer-operable or part of an active
    widget, but expected keyboard navigation cannot reach or complete operation of that same
    target. Reporting a different keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: After expanding Schedule Design Update and opening a panel datepicker, Playwright resolved visible Previous and Next links.
- Setup for selector visibility: Expand the Schedule Design Update panel, then open one of its datepicker trigger buttons before inspecting the datepicker month links.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
