# Merge Instance

```yaml
instance_id: shopping_admin.admin_admin_integration.links_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA75
  review_status: source_and_live_checked
page:
  site: shopping_admin
  page_name: Integrations
  start_url: http://localhost:7780/admin/admin/integration/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa75.lf.left_nav_disclosure_anchor_without_widget_role
    target:
      selector: '#nav a[href=''#''][onclick*=''return false'']'
      description: the top-level admin left navigation anchor elements on the Integrations page
      coverage_policy: representative_group
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched anchor elements have `href='#'` and `onclick='return false;'` without button/disclosure roles or `aria-expanded`
      state. Activation expands a left navigation submenu in place while the current page remains loaded.
  - issue_id: shopping_admin.pa75.lp.integration_reauthorize_without_row_context
    target:
      selector: '#integrationGrid_table td.col-activate a'
      description: the `Reauthorize` link in the Integrations grid Activate column
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link has accessible name `Reauthorize` and no programmatic integration-row context. Its `title`
      repeats the same action text, the Activate cell does not identify the integration, and the `Magento Analytics user`
      text is ordinary sibling-cell text without `headers`, row-header, or ARIA association.
```

## Source And Live Check

- This L3 source reuses reviewed L2 merge source files for the same page where applicable:
  - `agent/gt_links/source_md_clean/merge-instances/level2/shopping_admin.admin_admin_integration.link_purpose.md` (`link_purpose`, 1 issue)
- This L3 source also includes the L3-owned left-navigation link-function issue group from the source record and live DOM review; this does not expand Merge L2 scope.
- `shopping-admin-link-purpose-record.md` PA75 states that 6.1 Link Function fails on the eight top-level left-navigation disclosure-as-link anchor elements.
- Fresh live L3 probe after refreshing Shopping Admin auth found eight visible `#nav a[href='#'][onclick*='return false']` anchor elements: `SALES`, `CATALOG`, `CUSTOMERS`, `MARKETING`, `CONTENT`, `REPORTS`, `STORES`, and `SYSTEM`.
- The live probe confirmed each matched anchor element has `href='#'`, `onclick='return false;'`, no explicit widget role, and no `aria-expanded` state.
- Coverage-gap observations such as header account dropdowns or candidate-outside command links remain excluded unless explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `shopping_admin + http://localhost:7780/admin/admin/integration/`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 2 issues: 1 link_function and 1 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
