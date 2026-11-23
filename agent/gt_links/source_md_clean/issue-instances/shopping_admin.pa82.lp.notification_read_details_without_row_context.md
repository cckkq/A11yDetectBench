# Issue Instance

```yaml
instance_id: shopping_admin.pa82.lp.notification_read_details_without_row_context
template_id: links.link_purpose.shopping_admin.notification_read_details_without_row_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA82

page:
  site: shopping_admin
  page_name: Notifications (System)
  start_url: http://localhost:7780/admin/admin/notification/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#notificationGrid_table td.col-actions a.action-details'
  description: the `Read Details` link in the System Notifications grid Actions column
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link has computed AX name `Read Details` and no description. Its
    action cell and associated column header only identify `Actions`; the
    notification message is in sibling `td.col-title` without row-header,
    headers/id, or ARIA association.
```

## Selector Check

- `document.querySelectorAll('#notificationGrid_table td.col-actions a.action-details')` resolves to one element on PA82.
- The matched element has visible text `Read Details`, no `aria-label`, no `title`, and URL `https://business.adobe.com/blog/the-latest/three-rules-of-b2b-commerce-using-adobe-commerce`.
- The associated column header is only `Actions`; the notification message cell is ordinary sibling-cell text rather than programmatic link context.
