# Issue Instance

```yaml
instance_id: gitlab.gl24.lp.empty_markdown_heading_permalink_anchor_without_name
template_id: links.link_purpose.gitlab.empty_markdown_heading_permalink_anchor_without_name
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL24

page:
  site: gitlab
  page_name: Help
  start_url: http://localhost:8023/help
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body a.anchor[href^=''#'']'
  description: the markdown heading permalink anchor elements in the GitLab Help page content
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched heading permalink anchor elements have empty accessible names. Their
    heading text is visual context, but it is not exposed as each link name or
    accessible description.
```

## Selector Check

- The `target.selector` value resolves to eight visible elements on GL24.
- The matched elements have empty text, no `aria-label`, no `title`, class `anchor`, and `aria-hidden=true`.
