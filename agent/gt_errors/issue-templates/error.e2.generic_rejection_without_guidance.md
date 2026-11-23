# Issue Template

- template_id: `error.e2.generic_rejection_without_guidance`
- template_name: `Generic rejection or invalid message without corrective guidance`
- domain: `error`
- primary_wcag: `3.3.3 Error Suggestion`
- assessment_mapping: `E.2 Error Suggestion`
- pattern_summary: `The system detects an input error, but the feedback remains a generic rejection or invalid message and provides insufficient corrective guidance`

## Recognition Rule
- The page detects an input error.
- The user sees a textual error message.
- The message remains generic, such as `Invalid credentials.` or `This value is not valid.`
- The user is not told what to check, re-enter, or do to recover.

## Boundary Rule
- Include cases that identify a violated rule but still lack a suggestion in `rule_violation_without_actionable_suggestion`.
- Exclude cases that directly degrade into an exception page or broken page after invalid input.
- Exclude cases that provide a concrete next action or accepted format.

## Canonical Examples
- `reddit.ex01.e2.generic_rejection_without_guidance`
- `reddit.rd11.e2.generic_rejection_without_guidance`
