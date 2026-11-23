# Issue Template

```yaml
template_id: focus.visible_focus.grid_small_selectors_no_visible_focus
template_name: Admin grid small controls have no visible focus indicator
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
  Magento admin grid small controls, such as mass-action selectors or active-filter remove
  buttons, can receive keyboard focus but have no user-perceivable focus indicator.
boundary: >-
  Include compact grid toolbar controls and active-filter remove controls. Do not include
  row action buttons, expanded filter-panel subcontrols, datepicker triggers, or left-nav
  controls.
instances:
  - shopping_admin.pa02.f21t6a.grid_small_selectors_no_visible_focus
  - shopping_admin.pa04.f21t6a.grid_small_selectors_no_visible_focus
```

## Pattern

Magento admin grid small controls are keyboard focusable, but the focused control has no visible focus indication.

## Boundary

Only compact grid controls and active-filter remove controls belong here.

## Instances

- `shopping_admin.pa02.f21t6a.grid_small_selectors_no_visible_focus`
- `shopping_admin.pa04.f21t6a.grid_small_selectors_no_visible_focus`
