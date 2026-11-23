# Issue Template

```yaml
template_id: focus.revealing_content.split_button_revealed_menu_no_focus_shift
template_name: Admin split-button revealed menu does not receive focus
domain: focus
criterion:
  issue_family: revealing_content
  wcag_target: WCAG 2.4.3 Focus Order
  assessment_requirement: F.5 Revealing Content
  ai_web:
    requirement_key: revealing-content
    requirement_name: Revealing content
    guidance_link_key: WCAG_2_4_3
    source_files:
      - accessibility-insights-web-main/src/assessments/visible-focus-order/test-steps/revealing-content.tsx
      - accessibility-insights-web-main/src/content/test/focus/revealing-content.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: >-
      Activating a component that reveals hidden content must move input focus into the
      revealed content.
  wcag:
    number: 2.4.3
    name: Focus Order
    link_name: WCAG 2.4.3
    url: https://www.w3.org/WAI/WCAG21/Understanding/focus-order.html
    criterion_text: >-
      If a Web page can be navigated sequentially and the navigation sequences affect
      meaning or operation, focusable components receive focus in an order that preserves
      meaning and operability.
pattern: >-
  A Magento admin split-button reveals menu content after keyboard activation, but focus
  does not move into the newly revealed content and subsequent keyboard navigation skips
  or leaves that content inoperable.
boundary: >-
  Include split-button or dropdown-trigger controls that reveal non-modal menu content.
  Do not include modal dialogs, visible-focus-only failures inside revealed content, or
  focus-return failures after closing content.
instances:
  - shopping_admin.pa10.f25t1.split_button_revealed_menu_no_focus_shift
```

## Pattern

A split-button reveals menu content, but keyboard focus does not move into the revealed content.

## Boundary

Only non-modal split-button or dropdown-trigger revealed-menu focus-order failures belong here.

## Instances

- `shopping_admin.pa10.f25t1.split_button_revealed_menu_no_focus_shift`
