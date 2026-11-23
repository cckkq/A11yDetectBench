# PASS Instance

```yaml
instance_id: gitlab.gl02.lp.project_title_links_have_specific_purpose
template_id: links.link_purpose.pass.gitlab.project_title_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL02
  matched_positive: gitlab.gl02.lp.dashboard_projects_view_all_without_section_context

page:
  site: gitlab
  page_name: User Profile
  start_url: http://localhost:8023/byteblaze
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body .project-row a.text-plain.js-prefetch-document[href^=''/byteblaze/'']'
  description: the visible project title anchor elements in the Personal projects overview list
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have specific visible project names and hrefs pointing
    to the corresponding `/byteblaze/<project>` URLs. The link text identifies
    the target project, so the Link Purpose issue is not present for this target.
```

## Selector Check

- A construction-time selector check confirmed visible matching project title anchor elements on GL02.
