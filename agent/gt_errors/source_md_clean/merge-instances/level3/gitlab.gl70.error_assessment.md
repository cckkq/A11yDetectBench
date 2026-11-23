# Merge Instance

```yaml
instance_id: gitlab.gl70.error_assessment
task_level: level3
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
  assessment_scope: ERROR E.1-E.4
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: gitlab.gl70.e1.commit_message_required_error_not_identified
    target:
      selector: textarea#commit-message
      description: the commit message textarea in the GitLab CI/CD pipeline editor
      coverage_policy: single
    criterion:
      issue_family: error_identification
      wcag_target: WCAG 3.3.1 Error Identification
    evidence_rule: >-
      After Configure pipeline opens the editor, clearing the target commit message textarea
      makes that required field invalid and disables Commit changes, but the page does not
      surface inline error text, aria-invalid, aria-describedby, or a non-empty alert/status/live
      region that identifies the required-field problem. A native validity API message that is
      not rendered or associated in the page DOM does not rescue this path.
  - issue_id: gitlab.gl70.e2.commit_message_required_error_without_suggestion
    target:
      selector: textarea#commit-message
      description: the commit message textarea in the GitLab CI/CD pipeline editor
      coverage_policy: single
    criterion:
      issue_family: error_suggestion
      wcag_target: WCAG 3.3.3 Error Suggestion
    evidence_rule: >-
      After Configure pipeline opens the editor, clearing the target commit message textarea
      makes that required field invalid and disables Commit changes, but the page provides no
      surfaced correction suggestion telling the user to fill the commit message or explaining
      how to recover from the blocked commit path. A native validity API message that is not
      rendered or associated in the page DOM does not rescue this path.
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
- This L3 merge source contains the reviewed ERROR E.1-E.4 inventory for this BASE-induced page owner key.
- Reviewed L3 families on this page: error_identification, error_suggestion, status_messages.
- The E1 and E2 entries are L3-only inventory items traced to the GL70 commit-message required-field path in the source record and review-run evidence.
- Completeness is scoped to the reviewed L3 inventory, not a new full-site re-audit of legacy records.
- Scene-trigger details remain in the source issue-instance prose and are not copied into the generated MERGE prompt.

## Merge Scope
- L3 owner key: gitlab + http://localhost:8023/byteblaze/dotfiles/-/ci/editor?branch_name=main + ERROR E.1-E.4.
- This merge instance should generate one ERROR L3 task for CI/CD Editor.
- gold.issues[] contains 3 reviewed issue entries.
- This generated merge source includes 2 L3-only issues beyond the current clean L1 source inventory.
