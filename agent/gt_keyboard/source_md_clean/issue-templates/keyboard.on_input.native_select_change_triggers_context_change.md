# Issue Template

```yaml
template_id: keyboard.on_input.native_select_change_triggers_context_change
template_name: Native selector changes context on input
domain: keyboard
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
  assessment_requirement: 1.4 On input
  ai_web:
    requirement_key: on-input
    requirement_name: On input
    guidance_link_key: WCAG_3_2_2
    source_files:
      - accessibility-insights-web-main/src/assessments/keyboard-interaction/test-steps/on-input.tsx
      - accessibility-insights-web-main/src/content/test/keyboard/on-input.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: Changing a user interface component setting must not automatically cause
      a context change unless users are advised before using the component.
  wcag:
    number: 3.2.2
    name: On Input
    link_name: WCAG 3.2.2
    url: https://www.w3.org/WAI/WCAG21/Understanding/on-input.html
    criterion_text: Changing the setting of any user interface component does not automatically
      cause a change of context unless the user has been advised of the behavior before using
      the component.
pattern: Native select or sort controls automatically change context when their value changes.
boundary: Include native select controls and equivalent visible sort toggles that change context
  without a separate confirmation step.
instances:
- shopping.p02.select_limiter
- shopping.p16.select_sorter
- reddit.rd02.submissions_toggle_context_change
- reddit.rd14.hot_toggle_context_change
- shopping_admin.pa02.page_limit_context_change
- shopping_admin.pa60.page_limit_context_change
```

## Pattern

Native select or sort controls automatically change context when their value changes.

## Boundary

Include native select controls and equivalent visible sort toggles that change context without a separate confirmation step.

## Instances

- `shopping.p02.select_limiter`
- `shopping.p16.select_sorter`
- `reddit.rd02.submissions_toggle_context_change`
- `reddit.rd14.hot_toggle_context_change`
- `shopping_admin.pa02.page_limit_context_change`
- `shopping_admin.pa60.page_limit_context_change`
