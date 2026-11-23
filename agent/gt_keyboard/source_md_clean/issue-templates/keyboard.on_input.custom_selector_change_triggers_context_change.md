# Issue Template

```yaml
template_id: keyboard.on_input.custom_selector_change_triggers_context_change
template_name: Custom selector changes context on input
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
pattern: Custom dropdown-like selectors automatically change context when their value changes.
boundary: Include custom store, scope, sort, or filter controls that change context without
  a separate confirmation step.
instances:
- gitlab.gl01.custom_selector_context_change
- shopping_admin.pa01.store_view_context_change
- shopping_admin.pa49.scope_select_context_change
- shopping_admin.pa50.scope_select_context_change
```

## Pattern

Custom dropdown-like selectors automatically change context when their value changes.

## Boundary

Include custom store, scope, sort, or filter controls that change context without a separate confirmation step.

## Instances

- `gitlab.gl01.custom_selector_context_change`
- `shopping_admin.pa01.store_view_context_change`
- `shopping_admin.pa49.scope_select_context_change`
- `shopping_admin.pa50.scope_select_context_change`
