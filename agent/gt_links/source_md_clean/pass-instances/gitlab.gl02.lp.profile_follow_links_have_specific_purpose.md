# PASS Instance

```yaml
instance_id: gitlab.gl02.lp.profile_follow_links_have_specific_purpose
template_id: links.link_purpose.pass.gitlab.profile_follow_links_have_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL02
  matched_positive: gitlab.gl02.lp.profile_rss_subscribe_anchor_without_target_context

page:
  site: gitlab
  page_name: User Profile
  start_url: http://localhost:8023/byteblaze
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body .profile-header a[href=''/users/byteblaze/followers''], main#content-body .profile-header a[href=''/users/byteblaze/following'']'
  description: the visible follower and following count anchor elements in the profile header
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have visible names `2 followers` and `3 following` and
    hrefs pointing to `/users/byteblaze/followers` and `/users/byteblaze/following`.
    The link text identifies the target list, so the Link Purpose issue is not
    present for this target.
```

## Selector Check

- A construction-time selector check confirmed two visible matching profile-header anchor elements on GL02.
