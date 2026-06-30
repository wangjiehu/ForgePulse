# Diagnosis Report: coating_line_conflicting_evidence_005

**Diagnosis status:** `conflicting_evidence`

## Incident Summary
Dryer alarm conflicts with fan frequency evidence. Alarm and sensor evidence conflict; verification is required before repair. Incident window: 2026-09-18T15:00:00+08:00 to 2026-09-18T15:24:00+08:00.

## Primary Root Cause
**Dryer zone 2 temperature control loop instability** (confidence: 0.59)

Ranked from alarm 100%, sensor 0%, SOP 100%, maintenance 50%, and operator note 22% evidence.

## Missing Evidence
- primary sensor anomaly: dryer_zone_2_temp_c

## Conflicting Evidence
- alarms favor Dryer zone 2 temperature control loop instability, while sensor anomalies favor Fan inverter airflow frequency instability

## Data Quality
- Sensor rows: 7
- Alarm events: 2
- SOP sections: 2
- Maintenance records: 1

## Diagnostic Process
- ✅ **Data Loading**: Loaded manifest, 7 sensor rows, 2 alarm rows, SOP and maintenance records.
- ✅ **Data Validation**: Sensor rows: 7, Alarms: 2, SOP sections: 2, Maintenance records: 1.
- ✅ **Signal Anomaly Detection**: Detected 1 anomalies across 1 fields. Correlated findings: 0.
- ✅ **Alarm Correlation**: Parsed 2 alarm events. Alarm codes: DRY-122.
- ✅ **SOP & Maintenance Retrieval**: Retrieved 3 SOP sections and 1 maintenance records.
- ✅ **Root Cause Ranking**: Matched 2 candidates from 5 fault modes. Primary: Dryer zone 2 temperature control loop instability (status: conflicting_evidence).
- ✅ **Evidence Sufficiency Decision**: Decision: conflicting_evidence. Missing: primary sensor anomaly: dryer_zone_2_temp_c. Conflicts: alarms favor Dryer zone 2 temperature control loop instability, while sensor anomalies favor Fan inverter airflow frequency instability.
- ✅ **Action Planning**: Generated 4 recommended actions across roles: equipment_engineer, safety_reviewer.
- ✅ **Report Generation**: Generated timeline (3 events), work order, evidence graph (15 links), and value estimates.

## Event Timeline
- **2026-09-18T15:06:15+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: active)
- **2026-09-18T15:16:00+08:00** [major] fan_frequency_hz threshold violation: fan_frequency_hz fell below threshold at 41.4.
- **2026-09-18T15:21:20+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: recovered)

## Root Cause Candidates
### RC-001: Dryer zone 2 temperature control loop instability
- **Confidence**: 0.59 | **Priority**: high
- **Fault Mode**: FM-001
- **Diagnostic Role**: equipment_cause
- **Score Breakdown**: alarm=1.00, sensor=0.00, sop=1.00, maint=0.50, note=0.22 → total=0.60
- **Evidence**: EV-001, EV-002, EV-005, EV-006, EV-007
- **Rationale**: Matched alarm codes: DRY-122. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 100%, sensor 0%, SOP 100%, maintenance 50%, and operator note 22% evidence.
- **Missing Evidence**: primary sensor anomaly: dryer_zone_2_temp_c

### RC-002: Fan inverter airflow frequency instability
- **Confidence**: 0.44 | **Priority**: medium
- **Fault Mode**: FM-003
- **Diagnostic Role**: equipment_cause
- **Score Breakdown**: alarm=0.00, sensor=1.00, sop=0.50, maint=0.50, note=0.16 → total=0.44
- **Evidence**: EV-003, EV-006, EV-007
- **Rationale**: Anomalous sensor fields: fan_frequency_hz. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 0%, sensor 100%, SOP 50%, maintenance 50%, and operator note 16% evidence.
- **Missing Evidence**: primary alarm: AIR-305

## Evidence
- **EV-001** (alarms.csv at 2026-09-18T15:06:15+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-002** (alarms.csv at 2026-09-18T15:21:20+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-003** (sensor_readings.csv at 2026-09-18T15:16:00+08:00): fan_frequency_hz below threshold at 41.4 [fan_frequency_hz] = 41.4
- **EV-004** (sop_dryer_airflow_verification.md): SOP section 'Overview' is relevant to observed anomalies.
- **EV-005** (sop_dryer_airflow_verification.md): SOP section 'DRY-122 Instrument Verification' is relevant to observed anomalies.
- **EV-006** (sop_dryer_airflow_verification.md): SOP section 'AIR-305 Fan Frequency Verification' is relevant to observed anomalies.
- **EV-007** (maintenance_records.md): Maintenance record M-2026-151: A dryer alarm and fan frequency drop occurred in the same window. The repair decision was deferred until sensor calibration and inverter output were checked independently. = M-2026-151

## Evidence Graph
- RC-001 --[supported_by]--> EV-001
- RC-001 --[supported_by]--> EV-002
- RC-001 --[supported_by]--> EV-005
- RC-001 --[supported_by]--> EV-006
- RC-001 --[supported_by]--> EV-007
- RC-002 --[supported_by]--> EV-003
- RC-002 --[supported_by]--> EV-006
- RC-002 --[supported_by]--> EV-007
- EV-001 --[from_source]--> alarms.csv
- EV-002 --[from_source]--> alarms.csv
- EV-003 --[from_source]--> sensor_readings.csv
- EV-004 --[from_source]--> sop_dryer_airflow_verification.md
- EV-005 --[from_source]--> sop_dryer_airflow_verification.md
- EV-006 --[from_source]--> sop_dryer_airflow_verification.md
- EV-007 --[from_source]--> maintenance_records.md

## Recommended Actions
- **ACT-001** (verify) [equipment_engineer]: Reconcile conflicting evidence before repair
  Verify sensor calibration, alarm timestamps, and equipment state because the evidence channels disagree: alarms favor Dryer zone 2 temperature control loop instability, while sensor anomalies favor Fan inverter airflow frequency instability
  Linked: RC-001, RC-002
- **ACT-002** (inspect) [equipment_engineer]: Follow SOP: DRY-122 Instrument Verification
  Per SOP section 'DRY-122 Instrument Verification': Compare controller temperature with an independent calibrated sensor.; Check alarm timestamp alignment before replacing the heater or controller.; Record controller output and heater current.
  Linked: RC-001
- **ACT-003** (inspect) [equipment_engineer]: Follow SOP: AIR-305 Fan Frequency Verification
  Per SOP section 'AIR-305 Fan Frequency Verification': Compare inverter command frequency with measured fan frequency.; Inspect the inverter cooling path and airflow filter.; Verify power quality before changing inverter parameters.
  Linked: RC-002
- **ACT-004** (safety) [safety_reviewer]: Confirm safety procedures before equipment intervention
  All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.
  Linked: RC-001, RC-002

## Work Order Draft
**Check cell coating line C dryer airflow and temperature control** (priority: high, assignee: equipment engineer)

**Tasks:**
  1. Verify sensor calibration, alarm timestamps, and equipment state because the evidence channels disagree: alarms favor Dryer zone 2 temperature control loop instability, while sensor anomalies favor Fan inverter airflow frequency instability
  1. Per SOP section 'DRY-122 Instrument Verification': Compare controller temperature with an independent calibrated sensor.; Check alarm timestamp alignment before replacing the heater or controller.; Record controller output and heater current.
  1. Per SOP section 'AIR-305 Fan Frequency Verification': Compare inverter command frequency with measured fan frequency.; Inspect the inverter cooling path and airflow filter.; Verify power quality before changing inverter parameters.
**Safety:**
  ⚠ All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.
## Agent Decisions
- **load** -> `continue`: All required case resources were loaded.
- **validate** -> `continue`: Case data passed quality checks without warnings.
- **assess_evidence** -> `conflicting_evidence`: alarms favor Dryer zone 2 temperature control loop instability, while sensor anomalies favor Fan inverter airflow frequency instability


## Postmortem Summary
The incident contains conflicting alarm and sensor evidence. Validate instrumentation and timestamp alignment before selecting a repair path.

## Limitations
- This diagnosis is generated from synthetic demo data.
- Real equipment actions require factory safety procedures and engineer confirmation.
- Configured value estimates are scenario calculations, not validated production results.
- Deterministic analysis only – no LLM reasoning applied.
