# Issue Template

```yaml
template_id: keyboard.character_key.global_search_shortcut_active_outside_input
template_name: Global search shortcut is active outside input
domain: keyboard
criterion:
  issue_family: character_key_shortcuts
  wcag_target: WCAG 2.1.4 Character Key Shortcuts
  assessment_requirement: 1.6 Character key shortcuts
  ai_web:
    requirement_key: character-key-shortcuts
    requirement_name: Character key shortcuts
    guidance_link_key: WCAG_2_1_4
    source_files:
      - accessibility-insights-web-main/src/assessments/keyboard-interaction/test-steps/character-key-shortcuts.tsx
      - accessibility-insights-web-main/src/content/test/keyboard/character-key-shortcuts.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: Single-character keyboard shortcuts must be turn-offable, remappable,
      or active only when the relevant component has focus.
  wcag:
    number: 2.1.4
    name: Character Key Shortcuts
    link_name: WCAG 2.1.4
    url: https://www.w3.org/WAI/WCAG21/Understanding/character-key-shortcuts.html
    criterion_text: >-
      If a keyboard shortcut is implemented in content using only letter
      (including upper- and lower-case letters), punctuation, number, or symbol
      characters, then at least one of the following is true: a mechanism is
      available to turn the shortcut off; a mechanism is available to remap the
      shortcut to use one or more non-printable keyboard characters; or the
      keyboard shortcut for a user interface component is only active when that
      component has focus.
pattern: A single-character shortcut moves focus to global search while focus is outside an
  editable target.
boundary: Include the global search input that receives focus from the shortcut behavior.
instances:
- shopping_admin.pa01.global_search_shortcut_active_outside_input
- shopping_admin.pa49.global_search_shortcut_active_outside_input
```

## Pattern

A single-character shortcut moves focus to global search while focus is outside an editable target.

## Boundary

Include the global search input that receives focus from the shortcut behavior.

## Instances

- `shopping_admin.pa01.global_search_shortcut_active_outside_input`
- `shopping_admin.pa49.global_search_shortcut_active_outside_input`
