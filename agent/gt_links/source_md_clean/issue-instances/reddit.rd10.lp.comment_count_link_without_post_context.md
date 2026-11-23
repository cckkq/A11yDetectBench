# Issue Instance

```yaml
instance_id: reddit.rd10.lp.comment_count_link_without_post_context
template_id: links.link_purpose.reddit.comment_count_link_without_post_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD10

page:
  site: reddit
  page_name: User Profile
  start_url: http://localhost:9999/user/MarvelsGrantMan136
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.submission a.text-sm[href^=''/f/'']:has(> strong)'
  description: the No comments and N comments anchor elements in the user profile post listing
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links have names such as No comments or N comments. The link
    names do not identify which post comment page will open, and the post title
    is not provided as programmatically determined link context.
```

## Selector Check

- With a valid Reddit login state, the `target.selector` value resolves to 24 visible elements on RD10.
- The matched anchor elements have names such as `No comments`, `140 comments`, and `62 comments`; their hrefs point to different `/f/...` submission pages.
