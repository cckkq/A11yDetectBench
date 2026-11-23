# Issue Instance

```yaml
instance_id: reddit.rd20.lp.opaque_inline_external_link_text
template_id: links.link_purpose.reddit.opaque_inline_external_link_text
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD20

page:
  site: reddit
  page_name: News Comments
  start_url: http://localhost:9999/f/news/comments
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'a[href*=''texastribune.org'']'
  description: the inline external link whose visible text is `as American as apple pie.`
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link text is `as American as apple pie.`. The text and same
    paragraph context do not identify the destination article or resource.
```

## Selector Check

- With a valid Reddit login state, the `target.selector` value resolves to one visible element on RD20.
- The matched anchor element text is `as American as apple pie.` and its href points to `https://www.texastribune.org/2022/11/10/indian-child-adoption-scotus/`.
