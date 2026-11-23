# Issue Instance

```yaml
instance_id: shopping_admin.pa02.lp.notification_remove_without_row_context
template_id: links.link_purpose.shopping_admin.notification_remove_without_row_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA02

page:
  site: shopping_admin
  page_name: Notifications
  start_url: http://localhost:7780/admin/admin/notification/index/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#notificationGrid_table td.col-actions a.action-delete'
  description: the `Remove` links in the Notifications grid Actions column
  coverage_policy: representative_group

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched links have computed AX name `Remove` and no description. Their
    action cells and associated column header only identify `Actions`; the
    notification messages are in sibling `td.col-title` cells without row-header,
    headers/id, or ARIA association.
```

## Selector Check

- The selector resolves to two elements on PA02.
- Both matched elements have visible text `Remove`, no `aria-label`, and no `title`.
- The first matched action cell contains `Read Details Remove`; the second contains `Remove`. Their associated column header is only `Actions`, and neither row exposes a row header or `headers` association for the sibling notification message cell.
