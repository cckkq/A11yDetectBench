# Issue Template

```yaml
template_id: links.link_purpose.shopping.order_view_order_without_row_header_context
template_name: Shopping order View Order links lack order context
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
  Repeated `View Order` links in customer order tables expose only action text
  without programmatically associated order context.
boundary: >-
  Include only order-table links named `View Order`. Do not merge `View Order`
  with `Reorder`; they are different actions.
instances:
  - shopping.p01.lp.order_view_order_without_row_header_context
  - shopping.p02.lp.order_view_order_without_row_header_context
```

## Pattern

Order-table `View Order` links lack programmatic order context.

## Boundary

Only `View Order` action links belong here.

## Instances

- `shopping.p01.lp.order_view_order_without_row_header_context`
- `shopping.p02.lp.order_view_order_without_row_header_context`
