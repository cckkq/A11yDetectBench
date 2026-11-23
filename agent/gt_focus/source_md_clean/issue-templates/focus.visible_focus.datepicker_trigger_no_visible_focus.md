# Issue Template

```yaml
template_id: focus.visible_focus.datepicker_trigger_no_visible_focus
template_name: Admin datepicker trigger buttons have no visible focus indicator
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
  Magento admin datepicker trigger buttons can receive keyboard focus, but the focused
  trigger has no user-perceivable focus indicator in the rendered page.
boundary: >-
  Include datepicker trigger buttons next to date fields. Do not include date inputs,
  compact grid toolbar controls, action buttons, or filter-panel multiselect controls.
instances:
  - shopping_admin.pa08.f21t1.datepicker_trigger_no_visible_focus
  - shopping_admin.pa15.f21t1.datepicker_trigger_no_visible_focus
```

## Pattern

Magento admin datepicker trigger buttons are keyboard focusable, but the focused trigger has no visible focus indication.

## Boundary

Only datepicker trigger buttons belong here.

## Instances

- `shopping_admin.pa08.f21t1.datepicker_trigger_no_visible_focus`
- `shopping_admin.pa15.f21t1.datepicker_trigger_no_visible_focus`
