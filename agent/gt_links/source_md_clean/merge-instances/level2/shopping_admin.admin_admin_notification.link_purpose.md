# Merge Instance

```yaml
instance_id: shopping_admin.admin_admin_notification.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA82
  review_status: source_and_live_checked

page:
  site: shopping_admin
  page_name: Notifications (System)
  start_url: http://localhost:7780/admin/admin/notification/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa82.lp.notification_read_details_without_row_context
      target:
        selector: '#notificationGrid_table td.col-actions a.action-details'
        description: the `Read Details` link in the System Notifications grid Actions column
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link has computed AX name `Read Details` and no description. Its
        action cell and associated column header only identify `Actions`; the
        notification message is in sibling `td.col-title` without row-header,
        headers/id, or ARIA association.

    - issue_id: shopping_admin.pa82.lp.notification_remove_without_row_context
      target:
        selector: '#notificationGrid_table td.col-actions a.action-delete'
        description: the `Remove` links in the System Notifications grid Actions column
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links have computed AX name `Remove` and no description. Their
        action cells and associated column header only identify `Actions`; the
        notification messages are in sibling `td.col-title` cells without row-header,
        headers/id, or ARIA association.

```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA82 states that the stable 6.2 link-purpose failures are LP015 `Read Details` and LP016/LP017 `Remove` in the System Notifications grid action column.
- The same PA82 record states raw `admin` and footer `Magento` were reclassified PASS because they expose AX description or title context.
- The record states the notification title is only in sibling `td.col-title`, not in the action cell, row header, `headers/id`, or ARIA association.
- Fresh live PA82 probe found 20 visible links. The only notification-grid action links matching this L2 link-purpose scope are one `Read Details` link and two `Remove` links.
- The same live probe found `admin`, `Notifications`, and footer `Magento` expose `title` context; left navigation `href="#" onclick="return false"` anchor elements belong to link-function, not this L2 link-purpose merge.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/admin/notification/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for PA82 link purpose, not one L2 task per issue.
- `Read Details` and `Remove` remain separate issues in `gold.issues[]` because they are different action labels and selectors.
