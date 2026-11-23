# Merge Instance

```yaml
instance_id: shopping.product_detail_gingerbread.links_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P10
  review_status: source_and_live_checked
page:
  site: shopping
  page_name: Product Detail
  start_url: http://localhost:7770/pre-baked-gingerbread-house-kit-value-pack-17-oz-pack-of-2-total-34-oz.html
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p10.lf.product_detail_add_to_compare_command_anchor
    target:
      selector: .product-info-main a.action.tocompare
      description: the `Add to Compare` anchor element in the product action links
      coverage_policy: single
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched anchor element has `href='#'` and a `data-post` payload targeting `/catalog/product_compare/add/`.
      Activation adds the current product to the compare list and shows page feedback instead of navigating to link content.
  - issue_id: shopping.p10.lf.product_detail_panel_tab_anchor_without_widget_role
    target:
      selector: .product.data.items a.data.switch
      description: the `Details` and `Reviews` product information tab anchor elements
      coverage_policy: representative_group
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched anchor elements are exposed as links with hrefs to page fragments, but activation switches the visible
      product information panel in place. The interactive tab state is represented on parent title elements, while the focusable
      anchor elements themselves are ordinary links.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `shopping + http://localhost:7770/pre-baked-gingerbread-house-kit-value-pack-17-oz-pack-of-2-total-34-oz.html`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 2 issues: 2 link_function.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
