# PASS Instance

```yaml
instance_id: reddit.rd18.lp.comment_author_profile_links_have_specific_purpose_for_permalink
template_id: links.link_purpose.pass.reddit.comment_author_profile_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD18
  matched_positive: reddit.rd18.lp.comment_permalink_without_comment_context

page:
  site: reddit
  page_name: Comment Thread
  start_url: http://localhost:9999/f/relationship_advice/25599/update-my-f23-boyfriend-m33-just-left-me-in-europe-told-me
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.comment header a[href^=''/user/'']:not([href=''/user/%5Bdeleted%5D''])'
  description: the visible non-deleted comment author profile anchor elements in comment headers
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have specific visible author names such as
    `JustLetItAllBurn` and `RAThrow_clairbear22`, and their hrefs point to the
    corresponding `/user/<name>` profile URL. The link text identifies the
    target profile, so the Link Purpose issue is not present for this target.
```

## Selector Check

- With a valid Reddit login state, `document.querySelectorAll('article.comment header a[href^=''/user/'']:not([href=''/user/%5Bdeleted%5D''])')` resolves to eight visible author profile anchor elements on RD18.
