# Issue Template

```yaml
template_id: focus.visible_focus.filter_dropdown_subcontrols_no_visible_focus
template_name: Admin filter-panel subcontrols have no visible focus indicator
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
  Magento admin filter-panel subcontrols can receive keyboard focus after the filter panel
  is expanded, but the focused subcontrol has no user-perceivable focus indicator.
boundary: >-
  Include subcontrols inside expanded admin grid filter panels. Do not include the Filters
  disclosure button, compact grid toolbar controls, datepicker triggers, or row action
  buttons.
instances:
  - shopping_admin.pa27.f21t6c.filter_dropdown_subcontrols_no_visible_focus
  - shopping_admin.pa62.f21t6c.filter_dropdown_subcontrols_no_visible_focus
```

## Pattern

Magento admin filter-panel subcontrols are keyboard focusable after expansion, but the focused subcontrol has no visible focus indication.

## Boundary

Only subcontrols inside expanded admin grid filter panels belong here.

## Instances

- `shopping_admin.pa27.f21t6c.filter_dropdown_subcontrols_no_visible_focus`
- `shopping_admin.pa62.f21t6c.filter_dropdown_subcontrols_no_visible_focus`
