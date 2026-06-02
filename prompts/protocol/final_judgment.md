# Final Judgment (project-local template)

Produce the final judgment as a **JSON** message.

## How to decide
- Apply the **0–5 rubric** to both sides: clarity, responsiveness, evidence quality,
  position consistency, respectful tone, persuasive force.
- Explain **why the winner won**, referencing the rubric dimensions.
- You must name **exactly one winner** — **no tie** is allowed.
- If the totals were fully tied and the decision required the **configured technical
  tie-break**, disclose this clearly in the `limitations` field and state that it is a
  deterministic protocol mechanism, **not** a claim of substantive superiority.

## Output format (strict)
- Return **exactly one JSON object** and nothing else.
- **No markdown, no code fence, no prose outside the JSON, no empty response.**
- Start the reply with `{` and end with `}`. Include at least `winner_role`,
  `loser_role`, and `reasoning`.
