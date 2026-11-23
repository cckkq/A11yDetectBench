# Issue Template

```yaml
template_id: links.link_purpose.gitlab.empty_gravatar_avatar_anchor_without_name
template_name: GitLab external Gravatar avatar anchor elements have empty names
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
  Profile header external Gravatar avatar anchor elements are exposed as links without
  accessible names.
boundary: >-
  Include only profile header external Gravatar avatar links. Do not include
  project-card avatar links or named user-menu avatar controls.
instances:
  - gitlab.gl03.lp.empty_gravatar_avatar_anchor_without_name
  - gitlab.gl06.lp.empty_gravatar_avatar_anchor_without_name
```

## Pattern

External Gravatar avatar anchor elements lack accessible link names.

## Boundary

Only profile header external Gravatar links belong here.

## Instances

- `gitlab.gl03.lp.empty_gravatar_avatar_anchor_without_name`
- `gitlab.gl06.lp.empty_gravatar_avatar_anchor_without_name`
