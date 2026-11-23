# PASS Instance

```yaml
instance_id: gitlab.gl06.lp.project_title_links_have_specific_purpose
template_id: links.link_purpose.pass.gitlab.project_title_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL06
  matched_positive: gitlab.gl06.lp.empty_gravatar_avatar_anchor_without_name

page:
  site: gitlab
  page_name: User Projects
  start_url: http://localhost:8023/users/byteblaze/projects
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body .project-row a.text-plain.js-prefetch-document[href^=''/byteblaze/'']'
  description: the visible project title links in the user projects list
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched links have specific visible project names and hrefs pointing to
    the corresponding `/byteblaze/<project>` URLs. The link text identifies the
    target project, so the Link Purpose issue is not present for this target.
```

## Selector Check

- The selector targets visible project title links on GL06.
- This target is different from the empty-name Gravatar avatar positive target.
