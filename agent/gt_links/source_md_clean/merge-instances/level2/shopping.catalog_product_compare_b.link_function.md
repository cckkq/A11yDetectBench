# Merge Instance

```yaml
instance_id: shopping.catalog_product_compare_b.link_function
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P20
  review_status: source_and_live_checked

page:
  site: shopping
  page_name: Compare Products
  start_url: http://localhost:7770/catalog/product_compare/index/uenc/aHR0cDovL2xvY2FsaG9zdDo3NzcwL2N1c3RvbWVyL3NlY3Rpb24vbG9hZC8_c2VjdGlvbnM9Y29tcGFyZS1wcm9kdWN0cyUyQ21lc3NhZ2VzJmZvcmNlX25ld19zZWN0aW9uX3RpbWVzdGFtcD1mYWxzZSZfPTE3NzMwNjQwODY2MDA~/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping.p20.lf.compare_page_print_command_anchor
      target:
        selector: 'a.action.print'
        description: the `Print This Page` anchor element above the compare products table
        coverage_policy: single
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched anchor element has `href='#'` and visible text `Print This Page`.
        Activation invokes print behavior for the current compare page instead
        of navigating to link content.

    - issue_id: shopping.p20.lf.compare_page_remove_product_command_anchor
      target:
        selector: '.table-comparison a.action.delete'
        description: the visible `Remove Product` anchor elements in the compare products table
        coverage_policy: representative_group
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched anchor elements have `href='#'`, title `Remove Product`, and
        `data-post` payloads targeting `/catalog/product_compare/remove/` with
        confirmation. Activation starts a remove-product command for a compare
        table item instead of navigating to link content.

```

## Source And Live Check

- `shopping-link-purpose-record.md` P20 states that 6.1 Link Function fails on L02 `Print This Page` and L03 `Remove Product` in the compare products page.
- The same P20 record states store logo and `Add to Wish List` are PASS and that P20 6.2 Link Purpose is PASS because `Print This Page` and `Remove Product` have clear names.
- Fresh live P20 probe after refreshing Shopping auth initially showed an empty compare list; after adding four homepage products to the compare list in the same fresh session, the compare table rendered.
- With products present in the compare list, the live probe found one visible `a.action.print` anchor element and four visible `.table-comparison a.action.delete` anchor elements.
- The delete selector is scoped to `.table-comparison` so hidden mini-cart remove templates are not included.

## Merge Scope

- L2 owner key: `shopping + http://localhost:7770/catalog/product_compare/index/uenc/aHR0cDovL2xvY2FsaG9zdDo3NzcwL2N1c3RvbWVyL3NlY3Rpb24vbG9hZC8_c2VjdGlvbnM9Y29tcGFyZS1wcm9kdWN0cyUyQ21lc3NhZ2VzJmZvcmNlX25ld19zZWN0aW9uX3RpbWVzdGFtcD1mYWxzZSZfPTE3NzMwNjQwODY2MDA~/ + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for P20 link function, not one L2 task per compare-page action pattern.
- The two entries in `gold.issues[]` preserve all P20 source-record link-function failure groups for the compare-list-present state.
