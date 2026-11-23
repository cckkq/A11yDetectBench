# Issue Instance

```yaml
instance_id: reddit.rd06.lf.reply_anchor_inserts_form_without_widget_role
template_id: links.link_function.reddit.reply_anchor_inserts_form_without_widget_role
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD06

page:
  site: reddit
  page_name: Comments Listing
  start_url: http://localhost:9999/comments
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'a.comment__reply-link[data-form-url]'
  description: the visible Reply anchor elements under Reddit comments on the Recent comments page
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Activating a matched Reply anchor element inserts or reveals a reply form in place.
    The action does not navigate to link content, but the target remains exposed
    as a link.
```

## Selector Check

- With a valid Reddit login state, the `target.selector` value resolves to 25 visible elements on RD06.
- The matched anchor elements have text `Reply`, class `comment__reply-link text-sm`, and `data-form-url` values such as `/comment_form/personalfinance/130785/2561512`.
