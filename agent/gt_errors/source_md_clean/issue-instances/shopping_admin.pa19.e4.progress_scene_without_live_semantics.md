# Issue Instance

```yaml
instance_id: shopping_admin.pa19.e4.progress_scene_without_live_semantics
template_id: error.e4.progress_scene_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA19

page:
  site: shopping_admin
  page_name: Newsletter Queue
  start_url: http://localhost:7780/admin/newsletter/queue/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#queueGrid button[title="Search"][data-action="grid-filter-apply"]'
  description: the Search action in the Magento Admin Newsletter Queue grid
  coverage_policy: single

probe: Change a Newsletter Queue grid filter such as the Subject filter, then use the target Search action to refresh the grid and observe the loading mask.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Using the target Newsletter Queue grid Search action produces an active
    same-page progress/status message at `.loading-mask` during grid refresh,
    but that message node and its relevant ancestors do not expose role,
    aria-live, or equivalent status-message semantics.
```

## Selector Check

- A fresh Playwright probe with refreshed Magento Admin auth opened PA19 and observed the visible Newsletter Queue grid and search/filter controls.
- `document.querySelectorAll('#queueGrid button[title="Search"][data-action="grid-filter-apply"]')` resolves to the stable grid Search action on PA19.
- The source record reports that a grid search or filter refresh produces a visible `.loading-mask` message for this page.
- The visible loading mask is evidence for this issue, but it is not the target selector. The source record reports that the loading-mask node has no role, aria-live, or equivalent status-message semantics.
