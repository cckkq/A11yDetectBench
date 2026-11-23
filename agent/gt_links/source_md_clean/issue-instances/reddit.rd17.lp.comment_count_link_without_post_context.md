# Issue Instance

```yaml
instance_id: reddit.rd17.lp.comment_count_link_without_post_context
template_id: links.link_purpose.reddit.comment_count_link_without_post_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD17

page:
  site: reddit
  page_name: Relationship Advice Forum
  start_url: http://localhost:9999/f/relationship_advice
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.submission a.text-sm[href^=''/f/'']:has(> strong)'
  description: the N comments anchor elements in the relationship_advice post listing
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links have names such as N comments. The link names do not
    identify which post comment page will open, and the post title is not
    provided as programmatically determined link context.
```

## Selector Check

- With a valid Reddit login state, the `target.selector` value resolves to 25 visible elements on RD17.
- The matched anchor elements have names such as `8 comments`, `142 comments`, and `88 comments`; their hrefs point to different `/f/...` submission pages.
