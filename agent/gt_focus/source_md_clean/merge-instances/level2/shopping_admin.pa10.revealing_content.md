# Merge Instance

```yaml
instance_id: shopping_admin.pa10.revealing_content
task_level: level2
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
  issue_family: revealing_content
  wcag_target: WCAG 2.4.3 Focus Order
  assessment_requirement: F.5 Revealing Content
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

- This L2 merge source contains the current clean Focus inventory for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Focus-specific evidence rules remain in each issue evidence_rule and in the shared Focus prompt/evaluator contract; no extra markdown fields are introduced.

## Merge Scope

- L2 owner key: shopping_admin + http://localhost:7780/admin/catalog/product/ + revealing_content + WCAG 2.4.3 Focus Order.
- gold.issues[] contains 1 reviewed clean-source issue entry.
