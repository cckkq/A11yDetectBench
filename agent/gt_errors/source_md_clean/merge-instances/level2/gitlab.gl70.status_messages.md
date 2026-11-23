# Merge Instance

```yaml
instance_id: gitlab.gl70.status_messages
task_level: level2
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL70
  review_status: clean_source_inventory_checked
page:
  site: gitlab
  page_name: CI/CD Editor
  start_url: http://localhost:8023/byteblaze/dotfiles/-/ci/editor?branch_name=main
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
  assessment_requirement: E.4 Status Messages
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl70.e4.status_text_change_without_live_semantics
    target:
      selector: .monaco-editor textarea.inputarea[role="textbox"]
      description: the YAML editor textbox in the GitLab CI/CD pipeline editor
      coverage_policy: single
    criterion:
      issue_family: status_messages
      wcag_target: WCAG 4.1.3 Status Messages
    evidence_rule: >-
      Changing the target YAML editor causes the pipeline validation text at `span[data-testid="validationMsg"]`
      to become an active same-page success or error status message, but that message node
      and its relevant ancestors do not expose role, aria-live, or equivalent status-message
      semantics. Empty nearby live-region nodes that do not carry this validation text do
      not rescue this message path.
```

## Source And Live Check
- This L2 merge source contains the complete status-messages inventory represented by the current clean ERROR source instances for this page/family owner key.
- Completeness is scoped to the reviewed clean source inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L2 owner key: gitlab + http://localhost:8023/byteblaze/dotfiles/-/ci/editor?branch_name=main + status_messages + WCAG 4.1.3 Status Messages.
- This merge instance should generate one ERROR L2 task for CI/CD Editor / status_messages.
- gold.issues[] contains 1 reviewed clean-source issue entries.
