# Merge Instance

```yaml
instance_id: shopping_admin.admin_reports_report_review_product.links_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA40
  review_status: source_and_live_checked
page:
  site: shopping_admin
  page_name: Product Reviews Report
  start_url: http://localhost:7780/admin/reports/report_review/product/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa40.lf.left_nav_disclosure_anchor_without_widget_role
    target:
      selector: '#nav a[href=''#''][onclick*=''return false'']'
      description: the top-level admin left navigation anchor elements on the Product Reviews Report page
      coverage_policy: representative_group
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched anchor elements have `href='#'` and `onclick='return false;'` without button/disclosure roles or `aria-expanded`
      state. Activation expands a left navigation submenu in place while the current page remains loaded.
  - issue_id: shopping_admin.pa40.lp.product_reviews_show_reviews_without_row_context
    target:
      selector: '#gridProducts_table td.col-actions a'
      description: the `Show Reviews` links in the Product Reviews Report grid Action column
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links have computed AX name `Show Reviews` and no description. Their action cells and associated
      column header only identify `Action`; product names are in sibling cells without row-header, headers/id, or ARIA association.
```

## Source And Live Check

- This L3 source reuses reviewed L2 merge source files for the same page where applicable:
  - `agent/gt_links/source_md_clean/merge-instances/level2/shopping_admin.admin_reports_report_review_product.link_purpose.md` (`link_purpose`, 1 issue)
- This L3 source also includes the L3-owned left-navigation link-function issue group from the source record and live DOM review; this does not expand Merge L2 scope.
- `shopping-admin-link-purpose-record.md` PA40 states that 6.1 Link Function fails on the eight top-level left-navigation disclosure-as-link anchor elements.
- Fresh live L3 probe after refreshing Shopping Admin auth found eight visible `#nav a[href='#'][onclick*='return false']` anchor elements: `SALES`, `CATALOG`, `CUSTOMERS`, `MARKETING`, `CONTENT`, `REPORTS`, `STORES`, and `SYSTEM`.
- The live probe confirmed each matched anchor element has `href='#'`, `onclick='return false;'`, no explicit widget role, and no `aria-expanded` state.
- Coverage-gap observations such as header account dropdowns or candidate-outside command links remain excluded unless explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `shopping_admin + http://localhost:7780/admin/reports/report_review/product/`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 2 issues: 1 link_function and 1 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
