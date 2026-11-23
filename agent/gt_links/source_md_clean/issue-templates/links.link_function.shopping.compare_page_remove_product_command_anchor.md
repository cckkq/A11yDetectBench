# Issue Template

```yaml
template_id: links.link_function.shopping.compare_page_remove_product_command_anchor
template_name: Compare page remove-product anchor elements trigger removal commands
domain: links
criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function
  ai_web:
    requirement_key: linkFunction
    requirement_name: Link function
    guidance_link_key: WCAG_4_1_2
    source_files:
      - accessibility-insights-web-main/src/assessments/links/test-steps/link-function.tsx
      - accessibility-insights-web-main/src/content/test/links/link-function.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: >-
      Links must navigate to another page, location, or resource. Controls that
      perform an action or change local state must not be exposed as ordinary
      links.
  wcag:
    number: 4.1.2
    name: Name, Role, Value
    link_name: WCAG 4.1.2
    url: https://www.w3.org/WAI/WCAG21/Understanding/name-role-value.html
    criterion_text: >-
      For all user interface components, the name and role can be
      programmatically determined; states, properties, and values that can be
      set by the user can be programmatically set; and notification of changes
      to these items is available to user agents, including assistive
      technologies.
pattern: >-
  Compare table `Remove Product` anchor elements start row-removal commands instead of
  navigating.
boundary: >-
  Include only visible `Remove Product` anchor elements inside the compare table. Do
  not include hidden mini-cart remove templates or the print command.
instances:
  - shopping.p19.lf.compare_page_remove_product_command_anchor
  - shopping.p20.lf.compare_page_remove_product_command_anchor
```

## Pattern

Compare table remove anchor elements execute product-removal commands while exposed as links.

## Boundary

Only visible compare table `Remove Product` anchor elements belong here.

## Instances

- `shopping.p19.lf.compare_page_remove_product_command_anchor`
- `shopping.p20.lf.compare_page_remove_product_command_anchor`
