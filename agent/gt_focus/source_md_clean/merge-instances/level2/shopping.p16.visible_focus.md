# Merge Instance

```yaml
instance_id: shopping.p16.visible_focus
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P16
  review_status: current_clean_inventory
page:
  site: shopping
  page_name: Toothbrushes and Accessories category
  start_url: http://localhost:7770/beauty-personal-care/oral-care/toothbrushes-accessories.html
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
  assessment_requirement: F.1 Visible Focus
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p16.f21t10.header_menu_expanded_item_no_visible_focus
    target:
      selector: nav.navigation a[role="menuitem"][href$="/beauty-personal-care/skin-care.html"]
      description: the Skin Care submenu item in the Shopping header mega-menu
      coverage_policy: single
    criterion:
      issue_family: visible_focus
      wcag_target: WCAG 2.4.7 Focus Visible
    evidence_rule: >-
      DOM focus may remain on ul#ui-id-1 for this ARIA composite menu. The target is current
      when ul#ui-id-1 aria-activedescendant points to the Skin Care menu item or the Skin
      Care item has ui-state-active after keyboard navigation. The item itself lacks a user-perceivable
      focus indicator. A focus ring or box-shadow on the ul#ui-id-1 container alone does not
      count as visible focus for the Skin Care item.
```

## Source And Live Check

- This L2 merge source contains the current clean Focus inventory for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Focus-specific evidence rules remain in each issue evidence_rule and in the shared Focus prompt/evaluator contract; no extra markdown fields are introduced.

## Merge Scope

- L2 owner key: shopping + http://localhost:7770/beauty-personal-care/oral-care/toothbrushes-accessories.html + visible_focus + WCAG 2.4.7 Focus Visible.
- gold.issues[] contains 1 reviewed clean-source issue entry.
