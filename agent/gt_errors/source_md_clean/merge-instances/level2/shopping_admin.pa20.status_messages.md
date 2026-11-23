# Merge Instance

```yaml
instance_id: shopping_admin.pa20.status_messages
task_level: level2
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
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
  assessment_requirement: E.4 Status Messages
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
- This L2 merge source contains the complete status-messages inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: shopping_admin + http://localhost:7780/admin/newsletter/subscriber/ + status_messages + WCAG 4.1.3 Status Messages.
- This merge instance should generate one ERROR L2 task for Newsletter Subscribers / status_messages.
- gold.issues[] contains 1 reviewed clean-source issue entries.
