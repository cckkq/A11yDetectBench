# Merge Instance

```yaml
instance_id: gitlab.gl11.error_suggestion
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11
  review_status: clean_source_inventory_checked
page:
  site: gitlab
  page_name: Profile settings
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion
  assessment_requirement: E.2 Error Suggestion
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl11.e2.rule_violation_without_actionable_suggestion
    target:
      selector: input#user_website_url[name="user[website_url]"]
      description: the Website URL input in the GitLab profile form
      coverage_policy: single
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      The page detects the Website URL value as invalid but does not provide an accepted URL
      format, an example URL, or another actionable correction direction. Other better validation
      paths on the same page do not rescue this Website URL path.
```

## Source And Live Check
- This L2 merge source contains the complete error-suggestion inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: gitlab + http://localhost:8023/-/profile + error_suggestion + WCAG 3.3.3 Error Suggestion.
- This merge instance should generate one ERROR L2 task for Profile settings / error_suggestion.
- gold.issues[] contains 1 reviewed clean-source issue entries.
