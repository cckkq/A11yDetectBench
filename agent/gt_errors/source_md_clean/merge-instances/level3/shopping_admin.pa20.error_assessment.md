# Merge Instance

```yaml
instance_id: shopping_admin.pa20.error_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA20
  review_status: clean_source_inventory_checked
page:
  site: shopping_admin
  page_name: Newsletter Subscribers
  start_url: http://localhost:7780/admin/newsletter/subscriber/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa20.e4.progress_scene_without_live_semantics
    target:
      selector: '#subscriberGrid button[title="Search"][data-action="grid-filter-apply"]'
      description: the Search action in the Magento Admin Newsletter Subscribers grid
      coverage_policy: single
    criterion:
      issue_family: status_messages
      wcag_target: WCAG 4.1.3 Status Messages
    evidence_rule: >-
      Using the target Newsletter Subscribers grid Search action produces an active same-page
      progress/status message at `.loading-mask` during grid refresh, but that message node
      and its relevant ancestors do not expose role, aria-live, or equivalent status-message
      semantics. No-selection workflow guards on the same page are not this target. Ordinary
      grid result or empty-state text such as `0 records found` or `We couldn't find any
      records.` is not the target scene for this issue.
```

## Source And Live Check
- This L3 merge source contains the complete ERROR E.1-E.4 inventory represented by the current clean ERROR source instances for this page owner key.
- Current clean-source families on this page: status_messages.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: shopping_admin + http://localhost:7780/admin/newsletter/subscriber/ + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for Newsletter Subscribers.
- gold.issues[] contains 1 reviewed clean-source issue entries.
- This generated merge source does not add L3-only issues beyond the current clean source inventory.
