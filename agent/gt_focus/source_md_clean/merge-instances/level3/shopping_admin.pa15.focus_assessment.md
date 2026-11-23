# Merge Instance

```yaml
instance_id: shopping_admin.pa15.focus_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA15
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Catalog Price Rules
  start_url: http://localhost:7780/admin/catalog_rule/promo_catalog/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Focus assessment scope F.1-F.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa15.f21t1.datepicker_trigger_no_visible_focus
    target:
      selector: button.ui-datepicker-trigger
      description: the Start and End date picker trigger buttons in the Catalog Price Rules
        filter row
      coverage_policy: representative_group
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      The target date picker trigger buttons receive keyboard focus, but no user-perceivable
      focus indicator is visible while one is keyboard-focused.
  - issue_id: shopping_admin.pa15.f21t6b.admin_action_buttons_no_visible_focus
    target:
      selector: button#apply_rules
      description: the Apply Rules button in the top toolbar of the Catalog Price Rules page
      coverage_policy: single
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      The Apply Rules toolbar button receives keyboard focus, but no user-perceivable focus
      indicator is visible while it is keyboard-focused.
```

## Source And Live Check

- This L3 merge source uses the full Focus assessment scope F.1-F.6.
- Completeness of `gold.issues[]` is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Current reviewed negative gold for this page only contains the listed F.1/F.5 issues; no F.2/F.3/F.4/F.6 gold is added here.

## Merge Scope

- L3 owner key: shopping_admin + http://localhost:7780/admin/catalog_rule/promo_catalog/ + Focus assessment scope F.1-F.6.
- gold.issues[] contains 2 reviewed clean-source issue entries.
