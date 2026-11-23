# PASS Instance

```yaml
instance_id: shopping_admin.pa20.e4.progress_scene_without_live_semantics
template_id: error.e4.progress_scene_without_live_semantics
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA20
  matched_positive: shopping_admin.pa20.e4.progress_scene_without_live_semantics
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
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same `Please wait...` loading/progress scene so it is programmatically
    exposed through role, aria-live, or equivalent status-message semantics. Ordinary grid
    result or empty-state text such as `0 records found` or `We couldn't find any records.`
    is not the target scene for this task. A reported E.4 issue on the matched loading-mask
    target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa20.e4.progress_scene_without_live_semantics`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
