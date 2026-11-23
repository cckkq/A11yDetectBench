# Merge Instance

```yaml
instance_id: shopping.category_oral_pain_relief.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P21
  review_status: source_and_live_checked

page:
  site: shopping
  page_name: Oral Pain Relief Category
  start_url: http://localhost:7770/beauty-personal-care/oral-care/oral-pain-relief.html
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping.p21.lp.generic_view_all_without_programmatic_context
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

- `shopping-link-purpose-record.md` P21 states that the true 6.2 Link Purpose failure is LP053 `View All` in the Recently Ordered block.
- The same P21 record states product-image links and `Remove This Item` are PASS because same `li.product-item` context identifies the specific product.
- Fresh live P21 probe after refreshing Shopping auth found one `.block-reorder a.action.view` anchor element.
- The Recently Ordered block is populated by Magento customer-data after initial page load; after waiting for the block content to leave `no-display`, the target anchor element is visible and named `View All`.
- P21 6.1 Link Function is PASS in the source record, so this merge instance records only the 6.2 link-purpose issue.

## Merge Scope

- L2 owner key: `shopping + http://localhost:7770/beauty-personal-care/oral-care/oral-pain-relief.html + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for P21 link purpose.
- The single `gold.issues[]` entry preserves the only P21 source-record link-purpose failure group.
