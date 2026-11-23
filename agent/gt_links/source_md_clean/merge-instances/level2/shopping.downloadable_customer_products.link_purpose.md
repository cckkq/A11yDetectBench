# Merge Instance

```yaml
instance_id: shopping.downloadable_customer_products.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P03
  review_status: source_and_live_checked

page:
  site: shopping
  page_name: Downloadable Products
  start_url: http://localhost:7770/downloadable/customer/products/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping.p03.lp.generic_view_all_without_programmatic_context
      target:
        selector: '.block-reorder a.action.view'
        description: the `View All` anchor element in the Recently Ordered block
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `View All`. The visible `Recently Ordered`
        block title is not exposed through the link name, description, ARIA
        association, same sentence, same paragraph, same list item, or same table
        cell.

```

## Source And Live Check

- `shopping-link-purpose-record.md` P03 states that 6.2 Link Purpose fails only on LP019 `View All` in the Recently Ordered block.
- The same P03 record states mini-cart and Recently Ordered `Add to Cart` / `Remove This Item` links are PASS because the same `li` product-name context identifies the target item.
- Fresh live P03 probe after refreshing Shopping auth found one `.block-reorder a.action.view` anchor element.
- The Recently Ordered block is populated by Magento customer-data after initial page load; after waiting for the block content to leave `no-display`, the target anchor element is visible and named `View All`.
- P03 6.1 Link Function is PASS in the source record, so this merge instance records only the 6.2 link-purpose issue.

## Merge Scope

- L2 owner key: `shopping + http://localhost:7770/downloadable/customer/products/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for P03 link purpose.
- The single `gold.issues[]` entry preserves the only P03 source-record link-purpose failure group.
