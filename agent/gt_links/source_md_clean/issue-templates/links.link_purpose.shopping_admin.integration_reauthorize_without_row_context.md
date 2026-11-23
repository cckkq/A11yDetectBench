# Issue Template

```yaml
template_id: links.link_purpose.shopping_admin.integration_reauthorize_without_row_context
template_name: Admin integration Reauthorize link lacks integration context
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
  Integrations grid `Reauthorize` links expose only action text without
  programmatically associated integration context.
boundary: >-
  This template is only for `Reauthorize` links in the Integrations grid.
instances:
  - shopping_admin.pa75.lp.integration_reauthorize_without_row_context
```

## Pattern

Integrations grid `Reauthorize` links lack programmatic integration context.

## Boundary

Only Integrations grid `Reauthorize` links belong here.

## Instances

- `shopping_admin.pa75.lp.integration_reauthorize_without_row_context`
