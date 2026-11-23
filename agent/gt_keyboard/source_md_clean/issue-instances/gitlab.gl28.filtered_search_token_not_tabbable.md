# Issue Instance

```yaml
instance_id: gitlab.gl28.filtered_search_token_not_tabbable
template_id: keyboard.keyboard_nonreachable.filtered_search_token_not_tabbable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL28
page:
  site: gitlab
  page_name: Merged Assigned Merge Requests
  start_url: http://localhost:8023/dashboard/merge_requests?scope=all&state=merged&assignee_username=byteblaze
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .filtered-search-token.search-token-assignee
  description: the Assignee equals Byte Blaze filtered-search token on the merged merge requests
    dashboard
  coverage_policy: single
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the Assignee equals Byte Blaze filtered-search token on the merged
    merge requests dashboard) is visible and pointer-operable or part of an active widget,
    but expected keyboard navigation cannot reach or complete operation of that same target.
    Reporting a different keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: Playwright resolved .filtered-search-token.search-token-assignee to one visible assignee token.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
