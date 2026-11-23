# Issue Template

```yaml
template_id: focus.visible_focus.explore_tab_controls_no_visible_focus
template_name: GitLab dashboard and explore tab controls have no visible focus indicator
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
  GitLab Dashboard or Explore tab controls can receive keyboard focus, but the focused
  tab control has no user-perceivable focus indicator beyond its existing selected/current
  page styling.
boundary: >-
  Include only GitLab Dashboard or Explore tab controls under this template. Do not include
  project avatar links, topbar controls, profile controls, or other navigation widgets.
instances:
  - gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus
  - gitlab.gl96.f21t4.explore_tab_controls_no_visible_focus
```

## Pattern

GitLab Dashboard or Explore tab controls are keyboard focusable, but the focused tab has no distinct visible focus indication.

## Boundary

Only the tab controls named by the instances belong here.

## Instances

- `gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus`
- `gitlab.gl96.f21t4.explore_tab_controls_no_visible_focus`
