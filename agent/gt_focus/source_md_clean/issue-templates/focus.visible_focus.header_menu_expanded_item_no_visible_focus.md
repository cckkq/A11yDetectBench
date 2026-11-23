# Issue Template

```yaml
template_id: focus.visible_focus.header_menu_expanded_item_no_visible_focus
template_name: Shopping header mega-menu expanded items have no visible focus indicator
domain: focus
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
  assessment_requirement: F.1 Visible Focus
  ai_web:
    requirement_key: visible-focus
    requirement_name: Visible focus
    guidance_link_key: WCAG_2_4_7
    source_files:
      - accessibility-insights-web-main/src/assessments/visible-focus-order/test-steps/visible-focus.tsx
      - accessibility-insights-web-main/src/content/test/focus/visible-focus.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: >-
      Components must provide a visible indication when they have the input focus.
  wcag:
    number: 2.4.7
    name: Focus Visible
    link_name: WCAG 2.4.7
    url: https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html
    criterion_text: >-
      Any keyboard operable user interface has a mode of operation where the keyboard
      focus indicator is visible.
pattern: >-
  Shopping frontend header mega-menu items can become the current keyboard menu item after
  the menu is expanded, but the current item has no user-perceivable focus indicator in
  the rendered page.
boundary: >-
  Include only expanded header mega-menu category or submenu items. Do not include product
  cards, account menus, search fields, or other non-mega-menu header controls.
instances:
  - shopping.p16.f21t10.header_menu_expanded_item_no_visible_focus
  - shopping.p29.f21t10.header_menu_expanded_item_no_visible_focus
```

## Pattern

Shopping header mega-menu items are keyboard-reachable after expansion, but the current menu item has no visible focus indication.

## Boundary

Only expanded header mega-menu items belong here.

## Instances

- `shopping.p16.f21t10.header_menu_expanded_item_no_visible_focus`
- `shopping.p29.f21t10.header_menu_expanded_item_no_visible_focus`
