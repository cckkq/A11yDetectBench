# Merge Instance

```yaml
instance_id: gitlab.help.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL24
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: Help
  start_url: http://localhost:8023/help
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl24.lp.empty_markdown_heading_permalink_anchor_without_name
      target:
        selector: 'main#content-body a.anchor[href^=''#'']'
        description: the markdown heading permalink anchor elements in the GitLab Help page content
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched heading permalink anchor elements have empty accessible names. Their
        heading text is visual context, but it is not exposed as each link name
        or accessible description.
```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL24 states that the stable 6.2 Link Purpose failure is the focusable empty-name markdown heading permalink anchor elements.
- Fresh live GL24 probe after refreshing GitLab auth found eight visible anchor elements matching `main#content-body a.anchor[href^='#']`.
- The matched anchor elements have empty text/name fields and fragment hrefs for the help-page headings.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/help + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for GL24 link purpose.
- The single `gold.issues[]` entry preserves the GL24 source-record link-purpose failure group already anchored by a clean atomic issue instance.
