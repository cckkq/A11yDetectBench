# Issue Instance

```yaml
instance_id: shopping_admin.pa01.global_search_shortcut_active_outside_input
template_id: keyboard.character_key.global_search_shortcut_active_outside_input
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA01
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
  expected_verdict: issue_found
  evidence_rule: Pressing / or ? while focus is outside an editable field moves focus to the
    Magento Admin global search input targeted by slash and question-mark shortcuts. The task
    path does not expose a way to turn off, remap, or limit that single-character shortcut
    to cases where the search input already has focus.
```

## Selector Check

- Playwright selector audit: Playwright resolved input#search-global to one visible global search input.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
