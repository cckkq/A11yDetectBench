# Issue Template

```yaml
template_id: keyboard.keyboard_nonreachable.mouse_operable_data_row_controls_not_tabbable
template_name: Mouse-operable grid rows are not tabbable
domain: keyboard
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
  assessment_requirement: 1.1 Keyboard navigation
  ai_web:
    requirement_key: keyboard-navigation
    requirement_name: Keyboard navigation
    guidance_link_key: WCAG_2_1_1
    source_files:
      - accessibility-insights-web-main/src/assessments/keyboard-interaction/test-steps/keyboard-navigation.tsx
      - accessibility-insights-web-main/src/content/test/keyboard/keyboard-navigation.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: Users must be able to navigate to all interactive interface components using a keyboard.
  wcag:
    number: 2.1.1
    name: Keyboard
    link_name: WCAG 2.1.1
    url: https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html
    criterion_text: All functionality of the content is operable through a keyboard interface
      without requiring specific timings for individual keystrokes, except where the underlying
      function requires input that depends on the path of the user's movement and not just
      the endpoints.
pattern: Magento admin data-grid rows are pointer-operable controls but are skipped by sequential
  keyboard navigation.
boundary: Include the visible pointer-operable data rows in the target grid.
instances:
- shopping_admin.pa68.mouse_operable_data_row_controls_not_tabbable
- shopping_admin.pa69.mouse_operable_data_row_controls_not_tabbable
```

## Pattern

Magento admin data-grid rows are pointer-operable controls but are skipped by sequential keyboard navigation.

## Boundary

Include the visible pointer-operable data rows in the target grid.

## Instances

- `shopping_admin.pa68.mouse_operable_data_row_controls_not_tabbable`
- `shopping_admin.pa69.mouse_operable_data_row_controls_not_tabbable`
