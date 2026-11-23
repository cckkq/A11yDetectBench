# Merge Instance

```yaml
instance_id: shopping_admin.admin_inventory_source_index.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA62
  review_status: source_and_live_checked

page:
  site: shopping_admin
  page_name: Sources
  start_url: http://localhost:7780/admin/inventory/source/index/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa62.lp.source_grid_edit_without_row_context
      target:
        selector: '[data-role=''grid''] a.action-menu-item'
        description: the `Edit` link in the inventory Sources grid Action column
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link has accessible name `Edit` and no programmatically
        associated source context. Its action cell text is only `Edit`, the
        Action column is not bound with `headers`, `scope`, or ARIA, and the
        source code and source name are ordinary sibling-cell text.
```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA62 states that the stable 6.2 Link Purpose failure is one source grid `Edit` link.
- The same source-record entry flips `admin`, footer `Magento`, and `Account Activity` to PASS; those are not included here.
- Fresh live PA62 probe after refreshing Shopping Admin auth found one visible `[data-role='grid'] a.action-menu-item` link after the UI grid rendered.
- The matched anchor element has text `Edit`, class `action-menu-item`, no `aria-label`, no `aria-labelledby`, no `aria-describedby`, no `title`, no `role`, and an href ending in `/source_code/default/`.
- PA62 also has 6.1 link-function failures on left navigation disclosures, but this merge instance records only the 6.2 link-purpose evidence.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/inventory/source/index/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for PA62 link purpose.
- The single `gold.issues[]` entry preserves the source-record stable Sources grid `Edit` failure confirmed on the live page.
