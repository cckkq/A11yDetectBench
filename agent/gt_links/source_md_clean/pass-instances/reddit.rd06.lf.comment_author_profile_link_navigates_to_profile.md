# PASS Instance

```yaml
instance_id: reddit.rd06.lf.comment_author_profile_link_navigates_to_profile
template_id: links.link_function.pass.reddit.comment_author_profile_link_navigates_to_profile
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD06
  matched_positive: reddit.rd06.lf.reply_anchor_inserts_form_without_widget_role

page:
  site: reddit
  page_name: Comments Listing
  start_url: http://localhost:9999/comments
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'article.comment header a[href^=''/user/'']:not([href=''/user/%5Bdeleted%5D''])'
  description: the visible non-deleted comment author profile anchor elements in comment headers on the Recent comments page
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have visible author names such as `7SlotGrill` and
    `DavosLostFingers`, and their hrefs point to corresponding `/user/<name>`
    profile URLs. Activation navigates to the user profile instead of
    inserting or revealing an in-place reply form, so the Link Function issue
    is not present for this target.
```

## Selector Check

- With a valid Reddit login state, `document.querySelectorAll('article.comment header a[href^=''/user/'']:not([href=''/user/%5Bdeleted%5D''])')` resolves to 24 visible author profile anchor elements on RD06.
- A Playwright click probe on the first matched anchor element navigated from `/comments` to `/user/7SlotGrill` without increasing the number of forms or textareas.
