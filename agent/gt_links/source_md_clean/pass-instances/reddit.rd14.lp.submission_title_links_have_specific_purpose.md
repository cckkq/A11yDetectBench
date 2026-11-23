# PASS Instance

```yaml
instance_id: reddit.rd14.lp.submission_title_links_have_specific_purpose
template_id: links.link_purpose.pass.reddit.submission_title_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD14
  matched_positive: reddit.rd14.lp.generic_more_link_without_list_context

page:
  site: reddit
  page_name: AskReddit Forum
  start_url: http://localhost:9999/f/AskReddit
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.submission a.submission__link'
  description: the visible submission title links in the AskReddit listing
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched links have specific visible submission titles and hrefs pointing
    to the corresponding submission or source URLs. The link text identifies
    the target, so the Link Purpose issue is not present for this target.
```

## Selector Check

- The selector targets visible submission title links on RD14.
- This target is different from the generic `More` pagination positive target.
