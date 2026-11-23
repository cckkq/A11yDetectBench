# Issue Template

```yaml
template_id: focus.visible_focus.project_initial_avatar_links_no_visible_focus
template_name: GitLab project initial avatar links have no visible focus indicator
domain: focus
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
  assessment_requirement: F.1 Visible Focus
  ai_web:
    requirement_key: visible-focus
    requirement_name: Visible focus
    guidance_link_key: WCAG_2_4_7
    source_files:
      - accessibility-insights-web-main/src/assessments/visible-focus-order/test-steps/visible-focus.tsx
      - accessibility-insights-web-main/src/content/test/focus/visible-focus.tsx
      - accessibility-insights-web-main/src/content/guideline-metadata.ts
    requirement_text: >-
      Components must provide a visible indication when they have the input focus.
  wcag:
    number: 2.4.7
    name: Focus Visible
    link_name: WCAG 2.4.7
    url: https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html
    criterion_text: >-
      Any keyboard operable user interface has a mode of operation where the keyboard
      focus indicator is visible.
pattern: >-
  GitLab project-list initial-letter avatar links can receive keyboard focus, but the
  focused avatar link has no user-perceivable focus indicator in the rendered page.
boundary: >-
  Include only GitLab project-list initial-letter avatar links. Do not include dashboard
  tab controls, topbar controls, search fields, or image-avatar cases that require a
  separate visual assessment.
instances:
  - gitlab.gl01.f21t3.project_initial_avatar_links_no_visible_focus
  - gitlab.gl02.f21t3.project_initial_avatar_links_no_visible_focus
```

## Pattern

GitLab project-list initial-letter avatar links are keyboard focusable, but the focused avatar link has no visible focus indication.

## Boundary

Only project-list initial-letter avatar links belong here.

## Instances

- `gitlab.gl01.f21t3.project_initial_avatar_links_no_visible_focus`
- `gitlab.gl02.f21t3.project_initial_avatar_links_no_visible_focus`
