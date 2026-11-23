# PASS Instance

```yaml
instance_id: shopping_admin.pa19.e4.progress_scene_without_live_semantics
template_id: error.e4.progress_scene_without_live_semantics
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA19
  matched_positive: shopping_admin.pa19.e4.progress_scene_without_live_semantics
page:
  site: shopping_admin
  page_name: Newsletter Queue
  start_url: http://localhost:7780/admin/newsletter/queue/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: '#queueGrid button[title="Search"][data-action="grid-filter-apply"]'
  description: the Search action in the Magento Admin Newsletter Queue grid
  coverage_policy: single
probe: >-
  Change a Newsletter Queue grid filter such as the Subject filter, then use the target Search
  action to refresh the grid and observe the loading mask.
criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same target interaction so the triggered same-page status, error, or
    progress message is programmatically exposed through role, aria-live, or equivalent status-message
    semantics. A reported E.4 issue on this matched target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa19.e4.progress_scene_without_live_semantics`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
