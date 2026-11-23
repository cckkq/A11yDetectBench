# PASS Instance

```yaml
instance_id: gitlab.gl24.lp.help_topic_links_have_specific_purpose
template_id: links.link_purpose.pass.gitlab.help_topic_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL24
  matched_positive: gitlab.gl24.lp.empty_markdown_heading_permalink_anchor_without_name

page:
  site: gitlab
  page_name: Help
  start_url: http://localhost:8023/help
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body .md a:not(.anchor)'
  description: the visible documentation topic links in the GitLab Help markdown content
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have specific visible names such as `Use GitLab`,
    `Administer GitLab`, and `Two-factor authentication`, with hrefs pointing
    to the corresponding help or documentation pages. The link text identifies
    each target topic, so the Link Purpose issue is not present for this target.
```

## Selector Check

- A construction-time selector check confirmed visible matching non-permalink markdown links on GL24.
