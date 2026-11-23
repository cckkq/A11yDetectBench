# Issue Instance

```yaml
instance_id: reddit.rd15.lp.comment_reply_without_comment_context
template_id: links.link_purpose.reddit.comment_reply_without_comment_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD15

page:
  site: reddit
  page_name: Comment Thread
  start_url: http://localhost:9999/f/AskReddit/10224/why-bleaching-your-butthole-isn-t-called-changing-your-ring
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'a.comment__reply-link[data-form-url]'
  description: the repeated Reply anchor elements in Reddit comment action rows
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links are named only Reply. The link names do not identify
    which comment the reply action belongs to, and the comment text or author is
    not provided as programmatically determined link context.
```

## Selector Check

- With a valid Reddit login state, the `target.selector` value resolves to 16 visible elements on RD15.
- The matched anchor elements have text `Reply`, class `comment__reply-link text-sm`, and `data-form-url` values such as `/comment_form/AskReddit/10224/411494`.
