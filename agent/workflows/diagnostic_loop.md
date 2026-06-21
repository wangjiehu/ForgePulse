# Diagnostic Loop

```text
load_case
  -> validate_inputs
  -> analyze_sensors
  -> parse_alarms
  -> build_timeline
  -> retrieve_sop
  -> retrieve_maintenance_history
  -> rank_root_causes
  -> generate_actions
  -> generate_work_order
  -> generate_report
  -> validate_evidence
```

## Validation Loop

Before returning a final diagnosis:

1. Check every evidence id exists.
2. Check every high-confidence root cause has at least two evidence items.
3. Check safety actions are not phrased as autonomous machine control.
4. Check limitations are present.
