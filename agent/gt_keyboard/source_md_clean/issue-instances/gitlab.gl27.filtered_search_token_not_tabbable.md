# Issue Instance

```yaml
instance_id: gitlab.gl27.filtered_search_token_not_tabbable
template_id: keyboard.keyboard_nonreachable.filtered_search_token_not_tabbable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL27
page:
  site: gitlab
  page_name: Assigned Merge Requests
  start_url: http://localhost:8023/dashboard/merge_requests?assignee_username=byteblaze
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .filtered-search-token.search-token-assignee
  description: the Assignee equals Byte Blaze filtered-search token on the merge requests
    dashboard
  coverage_policy: single
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the Assignee equals Byte Blaze filtered-search token on the merge
    requests dashboard) is visible and pointer-operable or part of an active widget, but expected
    keyboard navigation cannot reach or complete operation of that same target. Reporting
    a different keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: Playwright resolved .filtered-search-token.search-token-assignee to one visible token with tabindex -1.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
