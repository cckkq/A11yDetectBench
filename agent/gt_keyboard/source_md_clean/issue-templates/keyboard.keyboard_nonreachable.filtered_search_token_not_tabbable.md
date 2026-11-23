# Issue Template

```yaml
template_id: keyboard.keyboard_nonreachable.filtered_search_token_not_tabbable
template_name: Filtered-search token is not tabbable
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
pattern: A visible filtered-search token is part of the active filter UI but cannot be reached
  by Tab.
boundary: Include the concrete filter token chip and remove-token path for the current query.
instances:
- gitlab.gl27.filtered_search_token_not_tabbable
- gitlab.gl28.filtered_search_token_not_tabbable
```

## Pattern

A visible filtered-search token is part of the active filter UI but cannot be reached by Tab.

## Boundary

Include the concrete filter token chip and remove-token path for the current query.

## Instances

- `gitlab.gl27.filtered_search_token_not_tabbable`
- `gitlab.gl28.filtered_search_token_not_tabbable`
