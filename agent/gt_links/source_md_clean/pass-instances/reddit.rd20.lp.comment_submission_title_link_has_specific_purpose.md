# PASS Instance

```yaml
instance_id: reddit.rd20.lp.comment_submission_title_link_has_specific_purpose
template_id: links.link_purpose.pass.reddit.comment_submission_title_link_has_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD20
  matched_positive: reddit.rd20.lp.opaque_inline_external_link_text

page:
  site: reddit
  page_name: News Comments
  start_url: http://localhost:9999/f/news/comments
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article#comment_2561379 a[href=''/f/news/129492'']'
  description: the submission title link inside the same comment block as the opaque inline external link
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element text is the full submission title `US Marine's adoption
    of Afghan war orphan voided`, and its href points to `/f/news/129492`.
    The link text identifies the target discussion, so the Link Purpose issue
    is not present for this target.
```

## Selector Check

- The selector targets the visible submission title link in `article#comment_2561379` on RD20.
- This target is in the same comment block as the matched positive but is a different DOM anchor element.
