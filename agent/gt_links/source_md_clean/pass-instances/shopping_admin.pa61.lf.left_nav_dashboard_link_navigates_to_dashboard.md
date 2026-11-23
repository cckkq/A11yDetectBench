# PASS Instance

```yaml
instance_id: shopping_admin.pa61.lf.left_nav_dashboard_link_navigates_to_dashboard
template_id: links.link_function.pass.shopping_admin.left_nav_dashboard_link_navigates_to_dashboard
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA61
  matched_positive: shopping_admin.pa61.lf.order_status_unassign_data_post_anchor

page:
  site: shopping_admin
  page_name: Order Status
  start_url: http://localhost:7780/admin/sales/order_status/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#nav a[href*=''/admin/admin/dashboard/'']'
  description: the Dashboard link in the admin left navigation
  coverage_policy: single

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched link has visible text `Dashboard`, a real href pointing to the
    admin dashboard, and no data-post command payload. Activation navigates
    to another admin page rather than running an in-place command, so the Link
    Function issue is not present for this target.
```

## Selector Check

- The selector targets one visible Dashboard navigation link on PA61.
- This target is different from the `Unassign` data-post command positive target.
