# Issue Template

```yaml
template_id: links.link_purpose.reddit.opaque_inline_external_link_text
template_name: Reddit inline external link text lacks destination purpose
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
  Inline external link text is a vague phrase that does not identify the
  destination article or resource.
boundary: >-
  Include only inline content links whose text and legal programmatic context
  do not identify the destination. Do not include comment action links.
instances:
  - reddit.rd20.lp.opaque_inline_external_link_text
```

## Pattern

Inline external links can fail when the link text does not identify the target resource.

## Boundary

Only the opaque inline external link belongs here.

## Instances

- `reddit.rd20.lp.opaque_inline_external_link_text`
