# Issue Instance

```yaml
instance_id: gitlab.gl70.e4.status_text_change_without_live_semantics
template_id: error.e4.status_text_change_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL70

page:
  site: gitlab
  page_name: CI/CD Editor
  start_url: http://localhost:8023/byteblaze/dotfiles/-/ci/editor?branch_name=main
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.monaco-editor textarea.inputarea[role="textbox"]'
  description: the YAML editor textbox in the GitLab CI/CD pipeline editor
  coverage_policy: single

probe: Choose Configure pipeline to open the editor, change the YAML in the target editor from valid to invalid, and observe the pipeline validation message.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Changing the target YAML editor causes the pipeline validation text at
    `span[data-testid="validationMsg"]` to become an active same-page success
    or error status message, but that message node and its relevant ancestors do
    not expose role, aria-live, or equivalent status-message semantics. Empty
    nearby live-region nodes that do not carry this validation text do not rescue
    this message path.

```

## Selector Check

- `document.querySelectorAll('.monaco-editor textarea.inputarea[role="textbox"]')` resolves to one YAML editor textbox after GL70 is opened into the pipeline editor state.
- A fresh Playwright probe with refreshed GitLab auth clicked `Configure pipeline` and observed the editor plus the pipeline validation message.
- `document.querySelectorAll('span[data-testid="validationMsg"]')` resolves to the validation message node; the source record reports that this text changes when the YAML changes from valid to invalid.
- The validation message is evidence for this issue, but it is not the target selector. The matched `span[data-testid="validationMsg"]` node and its observed ancestors have no `role` and no `aria-live` attribute.