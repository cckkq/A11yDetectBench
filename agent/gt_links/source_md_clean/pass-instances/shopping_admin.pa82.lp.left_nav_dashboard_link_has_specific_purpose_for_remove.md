# PASS Instance

```yaml
instance_id: shopping_admin.pa82.lp.left_nav_dashboard_link_has_specific_purpose_for_remove
template_id: links.link_purpose.pass.shopping_admin.left_nav_dashboard_link_has_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA82
  matched_positive: shopping_admin.pa82.lp.notification_remove_without_row_context

page:
  site: shopping_admin
  page_name: Notifications (System)
  start_url: http://localhost:7780/admin/admin/notification/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#nav a[href*=''/admin/admin/dashboard/'']'
  description: the Dashboard link in the admin left navigation
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched link has visible text `Dashboard` and an href pointing to the
    admin dashboard. The link text identifies the destination, so the Link
    Purpose issue is not present for this target.
```

## Selector Check

- The selector targets one visible Dashboard navigation link on PA82.
- This target is different from the `Remove` grid positive target.
