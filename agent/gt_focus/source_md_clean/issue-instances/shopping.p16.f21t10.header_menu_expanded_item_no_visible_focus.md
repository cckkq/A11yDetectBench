# Issue Instance

```yaml
instance_id: shopping.p16.f21t10.header_menu_expanded_item_no_visible_focus
template_id: focus.visible_focus.header_menu_expanded_item_no_visible_focus
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P16

page:
  site: shopping
  page_name: Toothbrushes and Accessories category
  start_url: http://localhost:7770/beauty-personal-care/oral-care/toothbrushes-accessories.html
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: nav.navigation a[role="menuitem"][href$="/beauty-personal-care/skin-care.html"]
  description: the Skin Care submenu item in the Shopping header mega-menu
  coverage_policy: single

setup: Prepare the header mega-menu expanded state with Beauty & Personal Care open and the Skin Care submenu item exposed for assessment.

criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    DOM focus may remain on ul#ui-id-1 for this ARIA composite menu. The
    target is current when ul#ui-id-1 aria-activedescendant points to the
    Skin Care menu item or the Skin Care item has ui-state-active after
    keyboard navigation. The item itself lacks a user-perceivable focus
    indicator. A focus ring or box-shadow on the ul#ui-id-1 container alone
    does not count as visible focus for the Skin Care item.
```

## Selector Check

- Playwright on P16 resolved `nav.navigation a[role="menuitem"][href$="/beauty-personal-care/skin-care.html"]` to the `Skin Care` submenu link.
- Keyboard navigation `Tab` to `ul#ui-id-1`, then `ArrowDown`, `ArrowDown` made `Skin Care` the active descendant in probe output.
- The target is intentionally a non-current category item on P16, avoiding current-category styling on `Beauty & Personal Care`, `Oral Care`, or `Toothbrushes & Accessories`.
- The source template excludes product-card controls from this menu template, so the selector is restricted to the header navigation menu.
