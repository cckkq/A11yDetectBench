# Issue Template

```yaml
template_id: links.link_purpose.shopping.generic_view_all_without_programmatic_context
template_name: Shopping View All links lack programmatic destination context
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
  Generic `View All` links rely on visual section context that is not
  programmatically bound to the link.
boundary: >-
  Include only generic `View All` links whose destination collection is not
  provided by legal programmatic link context.
instances:
  - shopping.p03.lp.generic_view_all_without_programmatic_context
  - shopping.p21.lp.generic_view_all_without_programmatic_context
```

## Pattern

Generic `View All` links lack programmatic destination context.

## Boundary

Only the target `View All` link belongs here.

## Instances

- `shopping.p03.lp.generic_view_all_without_programmatic_context`
- `shopping.p21.lp.generic_view_all_without_programmatic_context`
