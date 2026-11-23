# Merge Instance

```yaml
instance_id: shopping.home.links_assessment
task_level: level3
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
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p29.lf.home_product_card_add_to_compare_command_anchor
    target:
      selector: .products-grid a.action.tocompare
      description: the `Add to Compare` anchor elements in home page product cards
      coverage_policy: representative_group
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched anchor elements have `href='#'` and `data-post` values targeting `/catalog/product_compare/add/`. Activation
      adds the product to the compare list and shows page feedback instead of navigating to link content.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `shopping + http://localhost:7770/`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 1 issue: 1 link_function.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
