# PASS Instance

```yaml
instance_id: gitlab.gl99.lp.snippet_cancel_link_has_form_context
template_id: links.link_purpose.pass.gitlab.snippet_cancel_link_has_form_context
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL99
  matched_positive: gitlab.gl99.lp.empty_help_icon_anchor_without_name

page:
  site: gitlab
  page_name: New Snippet
  start_url: http://localhost:8023/-/snippets/new
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'form a[href=''/-/snippets'']'
  description: the Cancel link at the end of the new snippet form
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element has visible text `Cancel` and appears beside the Create
    snippet submit control at the end of the new snippet form. The form context
    identifies the action as canceling snippet creation and the href returns to
    the snippets list, so the Link Purpose issue is not present for this target.
```

## Selector Check

- A construction-time selector check confirmed one visible matching Cancel link on GL99.
- A Playwright click probe navigated from `/-/snippets/new` to `/dashboard/snippets`.
