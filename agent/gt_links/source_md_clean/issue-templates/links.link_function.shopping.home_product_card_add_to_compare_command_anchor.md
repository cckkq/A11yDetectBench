# Issue Template

```yaml
template_id: links.link_function.shopping.home_product_card_add_to_compare_command_anchor
template_name: Home product-card Add to Compare anchor elements perform commands
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
  Product-card `Add to Compare` anchor elements perform an add-to-compare command
  instead of navigating to link content.
boundary: >-
  Include only product-card `Add to Compare` anchor elements on the shopping home page.
  Do not include product-name links, image links, wishlist links, or cart links.
instances:
  - shopping.p29.lf.home_product_card_add_to_compare_command_anchor
```

## Pattern

Home product-card compare anchor elements execute a compare command while exposed as links.

## Boundary

Only home page `Add to Compare` product-card anchor elements belong here.

## Instances

- `shopping.p29.lf.home_product_card_add_to_compare_command_anchor`
