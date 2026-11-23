# Issue Template

```yaml
template_id: links.link_purpose.gitlab.dashboard_overview_view_all_without_section_context
template_name: GitLab profile projects View all link lacks section context
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
  The GitLab profile overview projects link named only `View all` relies on a
  visual section heading rather than programmatically determined link context.
boundary: >-
  This template is only for the visible `View all` link in the profile overview
  projects section. Do not include the hidden Activity `View all` DOM node.
instances:
  - gitlab.gl02.lp.dashboard_projects_view_all_without_section_context
```

## Pattern

The profile overview projects `View all` link lacks programmatic section context.

## Boundary

Only the visible projects `View all` link belongs here; the hidden Activity `View all` DOM node is excluded.

## Instances

- `gitlab.gl02.lp.dashboard_projects_view_all_without_section_context`
