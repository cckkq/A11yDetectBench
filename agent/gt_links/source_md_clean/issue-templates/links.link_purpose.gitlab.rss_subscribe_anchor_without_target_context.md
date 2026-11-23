# Issue Template

```yaml
template_id: links.link_purpose.gitlab.rss_subscribe_anchor_without_target_context
template_name: GitLab Subscribe RSS links lack feed target context
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
  RSS feed links named only `Subscribe` do not programmatically identify the
  feed being subscribed to.
boundary: >-
  Include only RSS or Atom feed anchor elements whose accessible name is generic
  `Subscribe` and whose feed target is not supplied by legitimate programmatic
  context.
instances:
  - gitlab.gl02.lp.profile_rss_subscribe_anchor_without_target_context
  - gitlab.gl50.lp.dashboard_activity_rss_subscribe_anchor_without_target_context
```

## Pattern

RSS `Subscribe` links lack feed target context.

## Boundary

Only feed subscription anchor elements with generic `Subscribe` names belong here.

## Instances

- `gitlab.gl02.lp.profile_rss_subscribe_anchor_without_target_context`
- `gitlab.gl50.lp.dashboard_activity_rss_subscribe_anchor_without_target_context`
