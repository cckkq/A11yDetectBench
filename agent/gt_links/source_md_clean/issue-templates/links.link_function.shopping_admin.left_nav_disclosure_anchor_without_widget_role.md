# Issue Template

```yaml
template_id: links.link_function.shopping_admin.left_nav_disclosure_anchor_without_widget_role
template_name: Admin left navigation anchor elements disclose submenus instead of navigating
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
  Magento admin top-level left navigation uses anchor elements as submenu disclosure
  controls instead of navigation links.
boundary: >-
  Include only top-level admin left navigation anchor elements that expand submenus.
  Do not include submenu links that navigate to real admin pages.
instances:
  - shopping_admin.pa03.lf.left_nav_disclosure_anchor_without_widget_role
  - shopping_admin.pa76.lf.left_nav_disclosure_anchor_without_widget_role
```

## Pattern

Top-level admin menu anchor elements expand submenus while exposed as links.

## Boundary

Only top-level left navigation disclosure anchor elements belong here.

## Instances

- `shopping_admin.pa03.lf.left_nav_disclosure_anchor_without_widget_role`
- `shopping_admin.pa76.lf.left_nav_disclosure_anchor_without_widget_role`
