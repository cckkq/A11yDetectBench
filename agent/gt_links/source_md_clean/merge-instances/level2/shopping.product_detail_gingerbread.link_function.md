# Merge Instance

```yaml
instance_id: shopping.product_detail_gingerbread.link_function
task_level: level2
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
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping.p10.lf.product_detail_add_to_compare_command_anchor
      target:
        selector: '.product-info-main a.action.tocompare'
        description: the `Add to Compare` anchor element in the product action links
        coverage_policy: single
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched anchor element has `href='#'` and a `data-post` payload targeting
        `/catalog/product_compare/add/`. Activation adds the current product to
        the compare list and shows page feedback instead of navigating to link
        content.

    - issue_id: shopping.p10.lf.product_detail_panel_tab_anchor_without_widget_role
      target:
        selector: '.product.data.items a.data.switch'
        description: the `Details` and `Reviews` product information tab anchor elements
        coverage_policy: representative_group
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched anchor elements are exposed as links with hrefs to page fragments,
        but activation switches the visible product information panel in place.
        The interactive tab state is represented on parent title elements, while
        the focusable anchor elements themselves are ordinary links.

```

## Source And Live Check

- `shopping-link-purpose-record.md` P10 states that 6.1 Link Function fails on L03 `Add to Compare` and L04/L05 `Details` / `Reviews` tab anchor elements.
- The same P10 record states store logo and `Add to Wish List` are PASS and that P10 6.2 Link Purpose is PASS.
- Fresh live P10 probe after refreshing Shopping auth found one visible `.product-info-main a.action.tocompare` anchor element and two visible `.product.data.items a.data.switch` anchor elements.
- The `Add to Compare` anchor element has `href='#'` and `data-post` for `/catalog/product_compare/add/`; the tab anchor elements have `data-toggle='trigger'` and fragment hrefs `#description` and `#reviews`.
- The atomic clean set already contains the P10 tab-anchor instance; the `Add to Compare` issue is included here because the same P10 source page exists and the source record explicitly lists it as a stable same-page 6.1 failure.

## Merge Scope

- L2 owner key: `shopping + http://localhost:7770/pre-baked-gingerbread-house-kit-value-pack-17-oz-pack-of-2-total-34-oz.html + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for P10 link function, not one L2 task per action/tab pattern.
- The two entries in `gold.issues[]` preserve all P10 source-record link-function failure groups.
