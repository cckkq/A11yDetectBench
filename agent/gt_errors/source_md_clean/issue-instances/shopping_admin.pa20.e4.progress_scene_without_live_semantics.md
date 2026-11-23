# Issue Instance

```yaml
instance_id: shopping_admin.pa20.e4.progress_scene_without_live_semantics
template_id: error.e4.progress_scene_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA20

page:
  site: shopping_admin
  page_name: Newsletter Subscribers
  start_url: http://localhost:7780/admin/newsletter/subscriber/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#subscriberGrid button[title="Search"][data-action="grid-filter-apply"]'
  description: the Search action in the Magento Admin Newsletter Subscribers grid
  coverage_policy: single

probe: Change a Newsletter Subscribers grid filter such as the Email filter, then use the target Search action to refresh the grid and observe only the `Please wait...` loading mask. Do not treat ordinary grid result or empty-state text as the target scene for this task.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Using the target Newsletter Subscribers grid Search action produces an
    active same-page progress/status message at `.loading-mask` during grid
    refresh, but that message node and its relevant ancestors do not expose
    role, aria-live, or equivalent status-message semantics. No-selection
    workflow guards on the same page are not this target. Ordinary grid result
    or empty-state text such as `0 records found` or `We couldn't find any
    records.` is not the target scene for this issue.
```

## Selector Check

- A fresh Playwright probe with refreshed Magento Admin auth opened PA20 and observed the visible Newsletter Subscribers grid and search/filter controls.
- `document.querySelectorAll('#subscriberGrid button[title="Search"][data-action="grid-filter-apply"]')` resolves to the stable grid Search action on PA20.
- The source record reports that a grid query or refresh produces a visible `.loading-mask` progress/status scene for this page.
- The visible loading mask is evidence for this issue, but it is not the target selector. The source record explicitly distinguishes this path from the no-selection mass-action prompt.
- Ordinary grid result-count or empty-state content after refresh is out of scope for this instance; this issue is scoped to the transient `Please wait...` progress scene.
