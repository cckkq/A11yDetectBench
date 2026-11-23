# Issue Instance

```yaml
instance_id: reddit.rd14.lp.generic_more_link_without_list_context
template_id: links.link_purpose.reddit.generic_more_link_without_list_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD14

page:
  site: reddit
  page_name: AskReddit Forum
  start_url: http://localhost:9999/f/AskReddit
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'a.button[rel=''next'']'
  description: the More pagination anchor element at the bottom of the AskReddit listing
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link name is only More. It does not programmatically identify
    that it continues or loads more items from the AskReddit listing.
```

## Selector Check

- With a valid Reddit login state, the `target.selector` value resolves to one visible element on RD14.
- The matched anchor element has text `More`, class `button button--secondary`, `rel=next`, and an href containing `next%5Branking%5D`.
