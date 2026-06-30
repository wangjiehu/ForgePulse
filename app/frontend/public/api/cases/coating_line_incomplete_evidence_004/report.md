# Diagnosis Report: coating_line_incomplete_evidence_004

**Diagnosis status:** `insufficient_evidence`

## Incident Summary
Dryer alarm with missing zone temperature evidence. Evidence is insufficient to confirm a root cause. Incident window: 2026-09-05T11:00:00+08:00 to 2026-09-05T11:20:00+08:00.

## Primary Root Cause
**Dryer zone 2 temperature control loop instability** (confidence: 0.42)

Ranked from alarm 100%, sensor 0%, SOP 50%, maintenance 0%, and operator note 17% evidence.

## Missing Evidence
- critical sensor field: dryer_zone_2_temp_c
- primary sensor anomaly: dryer_zone_2_temp_c

## Data Quality
- Sensor rows: 6
- Alarm events: 3
- SOP sections: 2
- Maintenance records: 1
- ⚠ Missing fields: dryer_zone_2_temp_c
- ⚠ Missing sensor fields: dryer_zone_2_temp_c

## Diagnostic Process
- ✅ **Data Loading**: Loaded manifest, 6 sensor rows, 3 alarm rows, SOP and maintenance records.
- ✅ **Data Validation**: Sensor rows: 6, Alarms: 3, SOP sections: 2, Maintenance records: 1. Warnings: Missing sensor fields: dryer_zone_2_temp_c
- ✅ **Signal Anomaly Detection**: Detected 2 anomalies across 1 fields. Correlated findings: 0.
- ✅ **Alarm Correlation**: Parsed 3 alarm events. Alarm codes: DRY-122, QCS-318.
- ✅ **SOP & Maintenance Retrieval**: Retrieved 1 SOP sections and 0 maintenance records.
- ✅ **Root Cause Ranking**: Matched 2 candidates from 5 fault modes. Primary: Dryer zone 2 temperature control loop instability (status: insufficient_evidence).
- ✅ **Evidence Sufficiency Decision**: Decision: insufficient_evidence. Missing: critical sensor field: dryer_zone_2_temp_c; primary sensor anomaly: dryer_zone_2_temp_c.
- ✅ **Action Planning**: Generated 5 recommended actions across roles: equipment_engineer, quality_engineer, safety_reviewer.
- ✅ **Report Generation**: Generated timeline (5 events), work order, evidence graph (12 links), and value estimates.

## Event Timeline
- **2026-09-05T11:05:20+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: active)
- **2026-09-05T11:15:40+08:00** [warning] Alarm QCS-318: Warning: Coating thickness approaching upper specification limit (status: active)
- **2026-09-05T11:16:00+08:00** [major] thickness_um threshold violation: thickness_um exceeded threshold at 104.6.
- **2026-09-05T11:16:00+08:00** [major] thickness_um reached peak: thickness_um drifted upward to 104.6 (Δ+3.6).
- **2026-09-05T11:19:10+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: recovered)

## Root Cause Candidates
### RC-001: Dryer zone 2 temperature control loop instability
- **Confidence**: 0.42 | **Priority**: medium
- **Fault Mode**: FM-001
- **Diagnostic Role**: equipment_cause
- **Score Breakdown**: alarm=1.00, sensor=0.00, sop=0.50, maint=0.00, note=0.17 → total=0.42
- **Evidence**: EV-001, EV-003, EV-006
- **Rationale**: Matched alarm codes: DRY-122. SOP sections provide relevant check procedures.
- **Why Ranked**: Ranked from alarm 100%, sensor 0%, SOP 50%, maintenance 0%, and operator note 17% evidence.
- **Missing Evidence**: primary sensor anomaly: dryer_zone_2_temp_c

## Downstream Effects and Business Risks
- **RC-002** Coating thickness drift and yield risk (0.49)

## Evidence
- **EV-001** (alarms.csv at 2026-09-05T11:05:20+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-002** (alarms.csv at 2026-09-05T11:15:40+08:00): QCS-318 warning alarm: Coating thickness approaching upper specification limit = QCS-318
- **EV-003** (alarms.csv at 2026-09-05T11:19:10+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-004** (sensor_readings.csv at 2026-09-05T11:16:00+08:00): thickness_um above threshold at 104.6 [thickness_um] = 104.6
- **EV-005** (sensor_readings.csv at 2026-09-05T11:16:00+08:00): thickness_um sustained upward drift, peak 104.6 (Δ+3.6) [thickness_um] = 104.6
- **EV-006** (sop_partial_dryer.md): SOP section 'DRY-122 Initial Safety Check' is relevant to observed anomalies.

## Evidence Graph
- RC-001 --[supported_by]--> EV-001
- RC-001 --[supported_by]--> EV-003
- RC-001 --[supported_by]--> EV-006
- RC-002 --[supported_by]--> EV-002
- RC-002 --[supported_by]--> EV-004
- RC-002 --[supported_by]--> EV-005
- EV-001 --[from_source]--> alarms.csv
- EV-002 --[from_source]--> alarms.csv
- EV-003 --[from_source]--> alarms.csv
- EV-004 --[from_source]--> sensor_readings.csv
- EV-005 --[from_source]--> sensor_readings.csv
- EV-006 --[from_source]--> sop_partial_dryer.md

## Recommended Actions
- **ACT-001** (collect_data) [equipment_engineer]: Collect missing diagnostic evidence
  Collect and validate the following evidence before confirming a root cause: critical sensor field: dryer_zone_2_temp_c; primary sensor anomaly: dryer_zone_2_temp_c
- **ACT-002** (inspect) [equipment_engineer]: Perform bounded manual inspection
  Inspect the affected station using the applicable SOP without replacing interlocks or making automatic control changes.
  Linked: RC-001
- **ACT-003** (inspect) [equipment_engineer]: Follow SOP: DRY-122 Initial Safety Check
  Per SOP section 'DRY-122 Initial Safety Check': Confirm the alarm timestamp and affected recipe.; Verify that the temperature historian channel is available and calibrated.; Do not replace components until temperature evidence is restored.
  Linked: RC-001
- **ACT-004** (quality) [quality_engineer]: Quality engineer review of affected material
  Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
  Linked: RC-002
- **ACT-005** (safety) [safety_reviewer]: Confirm safety procedures before equipment intervention
  All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.
  Linked: RC-001, RC-002

## Work Order Draft
**Check cell coating line C dryer section** (priority: high, assignee: equipment engineer)

**Tasks:**
  1. Collect and validate the following evidence before confirming a root cause: critical sensor field: dryer_zone_2_temp_c; primary sensor anomaly: dryer_zone_2_temp_c
  1. Inspect the affected station using the applicable SOP without replacing interlocks or making automatic control changes.
  1. Per SOP section 'DRY-122 Initial Safety Check': Confirm the alarm timestamp and affected recipe.; Verify that the temperature historian channel is available and calibrated.; Do not replace components until temperature evidence is restored.
  1. Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
**Safety:**
  ⚠ All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.
## Agent Decisions
- **load** -> `continue`: All required case resources were loaded.
- **validate** -> `continue_with_caution`: Missing sensor fields: dryer_zone_2_temp_c
- **assess_evidence** -> `insufficient_evidence`: critical sensor field: dryer_zone_2_temp_c; primary sensor anomaly: dryer_zone_2_temp_c


## Postmortem Summary
The available evidence does not support a reliable root-cause conclusion. Collect the listed missing evidence and repeat the bounded diagnosis before approving repair work.

## Limitations
- This diagnosis is generated from synthetic demo data.
- Real equipment actions require factory safety procedures and engineer confirmation.
- Configured value estimates are scenario calculations, not validated production results.
- Deterministic analysis only – no LLM reasoning applied.
