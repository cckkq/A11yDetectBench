# PASS Instance

```yaml
instance_id: reddit.rd15.lp.comment_author_profile_links_have_specific_purpose_for_parent
template_id: links.link_purpose.pass.reddit.comment_author_profile_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD15
  matched_positive: reddit.rd15.lp.comment_parent_without_comment_context

page:
  site: reddit
  page_name: Comment Thread
  start_url: http://localhost:9999/f/AskReddit/10224/why-bleaching-your-butthole-isn-t-called-changing-your-ring
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.comment header a[href^=''/user/'']:not([href=''/user/%5Bdeleted%5D''])'
  description: the visible non-deleted comment author profile links in comment headers
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched links have specific visible author names and hrefs pointing to
    the corresponding `/user/<name>` profile URLs. The link text identifies the
    target profile, so the Link Purpose issue is not present for this target.
```

## Selector Check

- The selector targets visible author profile links on RD15.
- This target is different from the repeated `Parent` positive target.
