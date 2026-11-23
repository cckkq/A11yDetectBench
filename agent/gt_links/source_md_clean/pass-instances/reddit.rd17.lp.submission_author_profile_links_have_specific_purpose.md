# PASS Instance

```yaml
instance_id: reddit.rd17.lp.submission_author_profile_links_have_specific_purpose
template_id: links.link_purpose.pass.reddit.submission_author_profile_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD17
  matched_positive: reddit.rd17.lp.generic_more_link_without_list_context

page:
  site: reddit
  page_name: Relationship Advice Forum
  start_url: http://localhost:9999/f/relationship_advice
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.submission header a[href^=''/user/'']:not([href=''/user/%5Bdeleted%5D''])'
  description: the visible non-deleted submission author profile anchor elements in the relationship_advice forum listing
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have specific visible author names such as
    `RAThrow_clairbear22` and `Practiccount`, and their hrefs point to the
    corresponding `/user/<name>` profile URL. The link text identifies the
    target profile, so the Link Purpose issue is not present for this target.
```

## Selector Check

- With a valid Reddit login state, `document.querySelectorAll('article.submission header a[href^=''/user/'']:not([href=''/user/%5Bdeleted%5D''])')` resolves to 20 visible author profile anchor elements on RD17.
