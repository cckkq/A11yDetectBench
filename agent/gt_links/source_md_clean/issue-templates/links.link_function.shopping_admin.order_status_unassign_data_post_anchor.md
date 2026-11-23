# Issue Template

```yaml
template_id: links.link_function.shopping_admin.order_status_unassign_data_post_anchor
template_name: Admin order-status Unassign anchor elements submit commands
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
  Order status `Unassign` anchor elements are data-post commands rather than
  navigation links.
boundary: >-
  Include only `Unassign` anchor elements in the Order Status grid. Do not include
  normal grid links that navigate to edit or view pages.
instances:
  - shopping_admin.pa61.lf.order_status_unassign_data_post_anchor
```

## Pattern

Order status `Unassign` anchor elements submit commands while exposed as links.

## Boundary

Only Order Status grid `Unassign` command anchor elements belong here.

## Instances

- `shopping_admin.pa61.lf.order_status_unassign_data_post_anchor`
