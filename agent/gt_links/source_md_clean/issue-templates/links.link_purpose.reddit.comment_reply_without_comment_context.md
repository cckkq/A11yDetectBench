# Issue Template

```yaml
template_id: links.link_purpose.reddit.comment_reply_without_comment_context
template_name: Reddit comment Reply links lack comment context
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
  Repeated comment Reply links do not programmatically identify which comment
  will be replied to.
boundary: >-
  Include only comment action-row anchor elements named Reply. Do not merge Reply,
  Permalink, and Parent because they are different actions.
instances:
  - reddit.rd15.lp.comment_reply_without_comment_context
  - reddit.rd18.lp.comment_reply_without_comment_context
```

## Pattern

Reply links do not identify the comment being replied to.

## Boundary

Only comment action-row anchor elements named `Reply` belong here.

## Instances

- `reddit.rd15.lp.comment_reply_without_comment_context`
- `reddit.rd18.lp.comment_reply_without_comment_context`
