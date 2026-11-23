# Merge Instance

```yaml
instance_id: shopping.home.link_function
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P29
  review_status: source_and_live_checked

page:
  site: shopping
  page_name: Home
  start_url: http://localhost:7770/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping.p29.lf.home_product_card_add_to_compare_command_anchor
      target:
        selector: '.products-grid a.action.tocompare'
        description: the `Add to Compare` anchor elements in home page product cards
        coverage_policy: representative_group
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched anchor elements have `href='#'` and `data-post` values targeting
        `/catalog/product_compare/add/`. Activation adds the product to the
        compare list and shows page feedback instead of navigating to link
        content.

```

## Source And Live Check

- `shopping-link-purpose-record.md` P29 states that 6.1 Link Function fails on the 12 `Add to Compare` product-card anchor elements.
- The same P29 record states store logo and 12 `Add to Wish List` anchor elements are PASS, and that P29 6.2 Link Purpose is PASS.
- Fresh live P29 probe after refreshing Shopping auth found twelve visible `.products-grid a.action.tocompare` anchor elements.
- The matched anchor elements have text `Add to Compare`, `href='#'`, and `data-post` payloads for different product ids targeting `/catalog/product_compare/add/`.

## Merge Scope

- L2 owner key: `shopping + http://localhost:7770/ + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for P29 link function.
- The single `gold.issues[]` entry preserves the P29 source-record link-function failure group already anchored by a clean atomic issue instance.
