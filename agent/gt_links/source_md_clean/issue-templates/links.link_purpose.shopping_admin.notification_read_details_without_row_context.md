# Issue Template

```yaml
template_id: links.link_purpose.shopping_admin.notification_read_details_without_row_context
template_name: Admin notification Read Details link lacks notification context
domain: links
criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose
  ai_web:
    requirement_key: linkPurpose
    requirement_name: Link purpose
    guidance_link_key: WCAG_2_4_4
    source_files:
      - accessibility-insights-web-main/src/assessments/links/test-steps/link-purpose.tsx
      - accessibility-insights-web-main/src/content/test/links/link-purpose.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: >-
      The purpose of a link must be described by its link text alone, or by the
      link text together with preceding page context.
  wcag:
    number: 2.4.4
    name: Link Purpose (In Context)
    link_name: WCAG 2.4.4
    url: https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html
    criterion_text: >-
      The purpose of each link can be determined from the link text alone or
      from the link text together with its programmatically determined link
      context, except where the purpose of the link would be ambiguous to users
      in general.
pattern: >-
  Notifications grid `Read Details` links expose only action text without
  programmatically associated notification context.
boundary: >-
  This template is only for `Read Details`. `Remove` is a separate action
  template.
instances:
  - shopping_admin.pa02.lp.notification_read_details_without_row_context
  - shopping_admin.pa82.lp.notification_read_details_without_row_context
```

## Pattern

Notifications grid `Read Details` links lack programmatic notification context.

## Boundary

Only `Read Details` belongs here. `Remove` is a separate action template.

## Instances

- `shopping_admin.pa02.lp.notification_read_details_without_row_context`
- `shopping_admin.pa82.lp.notification_read_details_without_row_context`
