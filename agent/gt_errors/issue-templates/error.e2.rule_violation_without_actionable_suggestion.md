# Issue Template

- template_id: `error.e2.rule_violation_without_actionable_suggestion`
- template_name: `Rule violation identified without an actionable correction suggestion`
- domain: `error`
- primary_wcag: `3.3.3 Error Suggestion`
- assessment_mapping: `E.2 Error Suggestion`
- pattern_summary: `The system detects a format, value, or uniqueness violation and describes the problem, but does not provide an actionable correction suggestion`

## Recognition Rule
- The page automatically detects an input error.
- The error text identifies the problem type, such as `blank`, `invalid`, `already taken`, or `not a valid URL`.
- The text gives no actionable correction direction, such as an accepted format, example value, acceptable alternative, or recovery action.
- A better same-page error path cannot be used to cover this path with insufficient guidance.

## Boundary Rule
- Exclude generic invalid or rejection messages that barely identify the problem type.
- Exclude cases that directly degrade into an exception page or broken page after invalid input.
- Exclude cases that clearly provide an accepted format, allowed characters, example value, or other concrete corrective direction.

## Canonical Examples
- `gitlab.gl11.e2.rule_violation_without_actionable_suggestion`
- `gitlab.gl16.e2.rule_violation_without_actionable_suggestion`
