# Merge Instance

```yaml
instance_id: shopping_admin.pa49.character_key_shortcuts
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA49
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Customer Order Total Report
  start_url: http://localhost:7780/admin/reports/report_customer/totals/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: character_key_shortcuts
  wcag_target: WCAG 2.1.4 Character Key Shortcuts
  assessment_requirement: 1.6 Character key shortcuts
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa49.global_search_shortcut_active_outside_input
    target:
      selector: input#search-global
      description: >-
        the Magento Admin global search input targeted by shortcuts on the customer totals
        report
      coverage_policy: single
    criterion:
      issue_family: character_key_shortcuts
      wcag_target: WCAG 2.1.4 Character Key Shortcuts
    evidence_rule: >-
      Pressing / or ? while focus is outside an editable field moves focus to the Magento
      Admin global search input targeted by shortcuts on the customer totals report. The task
      path does not expose a way to turn off, remap, or limit that single-character shortcut
      to cases where the search input already has focus.
```

## Source And Live Check

- This L2 merge source is restricted to a BASE-induced page/family owner key.
- Completeness is scoped to reviewed Keyboard inventory inside that owner key, not a new full-site audit.
- No BASE-external page or page/family owner is introduced here.

## Merge Scope

- Owner key: shopping_admin + PA49 + character_key_shortcuts + WCAG 2.1.4 Character Key Shortcuts.
- gold.issues[] contains 1 reviewed issue entries.
