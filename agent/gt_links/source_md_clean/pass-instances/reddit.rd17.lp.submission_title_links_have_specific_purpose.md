# PASS Instance

```yaml
instance_id: reddit.rd17.lp.submission_title_links_have_specific_purpose
template_id: links.link_purpose.pass.reddit.submission_title_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD17
  matched_positive: reddit.rd17.lp.comment_count_link_without_post_context

page:
  site: reddit
  page_name: Relationship Advice Forum
  start_url: http://localhost:9999/f/relationship_advice
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.submission a.submission__link'
  description: the visible submission title anchor elements in the relationship_advice forum listing
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have specific visible names such as `[UPDATE] My (f23)
    boyfriend...` and other full submission titles, and their hrefs point to
    the corresponding submission URL. The link text identifies the target, so
    the Link Purpose issue is not present for this target.
```

## Selector Check

- `document.querySelectorAll('article.submission a.submission__link')` resolves to 25 visible post title anchor elements.
