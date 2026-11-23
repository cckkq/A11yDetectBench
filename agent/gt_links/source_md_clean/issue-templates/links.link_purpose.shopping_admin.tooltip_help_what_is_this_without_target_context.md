# Issue Template

```yaml
template_id: links.link_purpose.shopping_admin.tooltip_help_what_is_this_without_target_context
template_name: Admin What is this help links lack target context
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
  Magento admin help links named `What is this?` expose only generic help text
  without programmatically naming the field, control, or report scope they help.
boundary: >-
  This template is for `What is this?` help links whose target object is not
  supplied by same-text context, ARIA, label, description, or another legitimate
  programmatic link context.
instances:
  - shopping_admin.pa01.lp.tooltip_help_what_is_this_without_target_context
  - shopping_admin.pa46.lp.tooltip_help_what_is_this_without_target_context
```

## Pattern

`What is this?` help links lack programmatic target context.

## Boundary

Only generic `What is this?` help links without legitimate programmatic context belong here.

## Instances

- `shopping_admin.pa01.lp.tooltip_help_what_is_this_without_target_context`
- `shopping_admin.pa46.lp.tooltip_help_what_is_this_without_target_context`
