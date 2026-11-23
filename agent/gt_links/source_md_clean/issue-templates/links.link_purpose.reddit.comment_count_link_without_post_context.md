# Issue Template

```yaml
template_id: links.link_purpose.reddit.comment_count_link_without_post_context
template_name: Reddit comment-count links lack post context
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
  Post-list comment-count links say only No comments or N comments and do not
  programmatically include the associated post title.
boundary: >-
  Include only submission comment-count/status anchor elements in post listings. Do not
  include Comments navigation tabs or comment action links.
instances:
  - reddit.rd10.lp.comment_count_link_without_post_context
  - reddit.rd17.lp.comment_count_link_without_post_context
```

## Pattern

Comment-count links do not identify which post comments will open.

## Boundary

Only post-list comment-count/status anchor elements belong here.

## Instances

- `reddit.rd10.lp.comment_count_link_without_post_context`
- `reddit.rd17.lp.comment_count_link_without_post_context`
