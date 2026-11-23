# Issue Instance

```yaml
instance_id: reddit.rd17.lp.generic_more_link_without_list_context
template_id: links.link_purpose.reddit.generic_more_link_without_list_context
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
  selector: 'a.button[rel=''next'']'
  description: the More pagination anchor element at the bottom of the relationship_advice listing
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link name is only More. It does not programmatically identify
    that it continues or loads more items from the relationship_advice listing.
```

## Selector Check

- With a valid Reddit login state, the `target.selector` value resolves to one visible element on RD17.
- The matched anchor element has text `More`, class `button button--secondary`, `rel=next`, and an href containing `next%5Branking%5D`.
