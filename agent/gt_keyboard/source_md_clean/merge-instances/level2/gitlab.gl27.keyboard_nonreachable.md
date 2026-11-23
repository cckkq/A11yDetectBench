# Merge Instance

```yaml
instance_id: gitlab.gl27.keyboard_nonreachable
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL27
  review_status: current_clean_inventory
page:
  site: gitlab
  page_name: Assigned Merge Requests
  start_url: http://localhost:8023/dashboard/merge_requests?assignee_username=byteblaze
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
  assessment_requirement: 1.1 Keyboard navigation
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl27.filtered_search_token_not_tabbable
    target:
      selector: .filtered-search-token.search-token-assignee
      description: the Assignee equals Byte Blaze filtered-search token on the merge requests
        dashboard
      coverage_policy: single
    criterion:
      issue_family: keyboard_nonreachable
      wcag_target: WCAG 2.1.1 Keyboard
    evidence_rule: >-
      The target (the Assignee equals Byte Blaze filtered-search token on the merge requests
      dashboard) is visible and pointer-operable or part of an active widget, but expected
      keyboard navigation cannot reach or complete operation of that same target. Reporting
      a different keyboard issue on the page does not satisfy this rule.
```

## Source And Live Check

- This L2 merge source is restricted to a BASE-induced page/family owner key.
- Completeness is scoped to reviewed Keyboard inventory inside that owner key, not a new full-site audit.
- No BASE-external page or page/family owner is introduced here.

## Merge Scope

- Owner key: gitlab + GL27 + keyboard_nonreachable + WCAG 2.1.1 Keyboard.
- gold.issues[] contains 1 reviewed issue entries.
