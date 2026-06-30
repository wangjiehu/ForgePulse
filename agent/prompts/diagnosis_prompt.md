# Diagnosis Review Prompt Template

This prompt is consumed by `OpenAICompatibleModelProvider.reason()` in
`app/backend/forgepulse_api/services/model_provider.py`. The deterministic
engine produces the structured `Diagnosis` first; the LLM only reviews it.

## Input (sent in the user message)

- `diagnosis_status`: finalized status (do not change).
- `incident_summary`: deterministic summary.
- `primary_root_cause`: the engine's primary candidate (id, title, confidence, rationale).
- `root_cause_candidates`: all candidates with id, title, confidence, rationale, why_ranked.
- `missing_evidence` / `conflicting_evidence`: gaps the engine already identified.
- `recommended_actions`: engine actions (do not change).
- `allowed_evidence_ids`: the only evidence ids you may reference.

## Task

Produce an **advisory review**. Refine wording of rationale/why_ranked per
candidate, flag uncertainties, and reaffirm safety. Do NOT alter status,
candidates, confidence, scores, or actions.

## Required JSON Shape

```json
{
  "review_summary": "",
  "candidate_notes": [
    { "candidate_id": "", "rationale_refined": "", "why_ranked_refined": "" }
  ],
  "uncertainties": [],
  "safety_reaffirmation": "",
  "referenced_evidence_ids": []
}
```

## Constraints

- `candidate_notes` may only reference `candidate_id` values present in `root_cause_candidates`.
- `referenced_evidence_ids` may only contain ids from `allowed_evidence_ids`.
- `safety_reaffirmation` must state that real equipment actions require engineer confirmation and factory safety procedures.
- If you cannot form a confident review, leave fields empty and explain in `uncertainties` — do not fabricate.
