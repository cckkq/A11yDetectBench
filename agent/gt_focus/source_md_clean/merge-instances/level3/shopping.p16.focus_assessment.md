# Merge Instance

```yaml
instance_id: shopping.p16.focus_assessment
task_level: level3
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
  assessment_scope: Focus assessment scope F.1-F.6
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

- This L3 merge source uses the full Focus assessment scope F.1-F.6.
- Completeness of `gold.issues[]` is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Current reviewed negative gold for this page only contains the listed F.1/F.5 issues; no F.2/F.3/F.4/F.6 gold is added here.

## Merge Scope

- L3 owner key: shopping + http://localhost:7770/beauty-personal-care/oral-care/toothbrushes-accessories.html + Focus assessment scope F.1-F.6.
- gold.issues[] contains 1 reviewed clean-source issue entry.
