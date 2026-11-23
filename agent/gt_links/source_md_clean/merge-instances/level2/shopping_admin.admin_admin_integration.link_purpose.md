# Merge Instance

```yaml
instance_id: shopping_admin.admin_admin_integration.link_purpose
task_level: level2
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
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa75.lp.integration_reauthorize_without_row_context
      target:
        selector: '#integrationGrid_table td.col-activate a'
        description: the `Reauthorize` link in the Integrations grid Activate column
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link has accessible name `Reauthorize` and no programmatic
        integration-row context. Its `title` repeats the same action text, the
        Activate cell does not identify the integration, and the `Magento
        Analytics user` text is ordinary sibling-cell text without `headers`,
        row-header, or ARIA association.
```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA75 states that the stable 6.2 Link Purpose failure is main-area LP015 `Reauthorize`.
- The same source-record entry flips `admin` and footer `Magento` to PASS; those are not included here.
- Fresh live PA75 probe after refreshing Shopping Admin auth found one visible `#integrationGrid_table td.col-activate a` link.
- The matched anchor element has text `Reauthorize`, `href=javascript:void(0);`, title `Reauthorize`, no `aria-label`, no `aria-labelledby`, no `aria-describedby`, no `role`, and opens the integration authorization popup.
- PA75 also has 6.1 link-function failures on left navigation disclosures, and the `Reauthorize` popup behavior is separately noted as a 6.1 coverage gap; this merge instance records only the 6.2 link-purpose evidence.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/admin/integration/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for PA75 link purpose.
- The single `gold.issues[]` entry preserves the source-record stable Integrations grid `Reauthorize` failure confirmed on the live page.
