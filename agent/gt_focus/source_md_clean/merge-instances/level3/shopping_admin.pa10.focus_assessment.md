# Merge Instance

```yaml
instance_id: shopping_admin.pa10.focus_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA10
  review_status: current_clean_inventory
page:
  site: shopping_admin
  page_name: Products
  start_url: http://localhost:7780/admin/catalog/product/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Focus assessment scope F.1-F.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa10.f25t1.split_button_revealed_menu_no_focus_shift
    target:
      selector: .page-actions button.action-toggle.primary.add
      description: the Add Product split-button trigger and revealed product-type menu
      coverage_policy: single
    criterion:
      issue_family: revealing_content
      wcag_target: WCAG 2.4.3 Focus Order
    evidence_rule: >-
      Keyboard activation reveals the menu, but focus does not move into the revealed menu
      content.
```

## Source And Live Check

- This L3 merge source uses the full Focus assessment scope F.1-F.6.
- Completeness of `gold.issues[]` is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Current reviewed negative gold for this page only contains the listed F.1/F.5 issues; no F.2/F.3/F.4/F.6 gold is added here.

## Merge Scope

- L3 owner key: shopping_admin + http://localhost:7780/admin/catalog/product/ + Focus assessment scope F.1-F.6.
- gold.issues[] contains 1 reviewed clean-source issue entry.
