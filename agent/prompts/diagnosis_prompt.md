# Diagnosis Prompt Template

## Input

- Case metadata
- Sensor anomaly summary
- Alarm summary
- Retrieved SOP sections
- Retrieved maintenance records
- Operator note

## Task

Generate a structured diagnosis for the incident.

## Required JSON Shape

```json
{
  "incident_summary": "",
  "facts": [],
  "timeline": [],
  "root_cause_candidates": [],
  "recommended_actions": [],
  "work_order_draft": {},
  "postmortem_summary": "",
  "limitations": []
}
```

## Constraints

- Every root-cause candidate must cite evidence ids.
- Every action must be connected to at least one candidate or safety requirement.
- Use cautious language when confidence is below 0.75.
