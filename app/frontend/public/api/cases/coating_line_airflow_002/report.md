# Diagnosis Report: coating_line_airflow_002

**Diagnosis status:** `confirmed`

## Incident Summary
Fan frequency drop causes dryer temperature drift and coating non-uniformity. Primary root cause: Fan inverter airflow frequency instability. Incident window: 2026-07-15T14:00:00+08:00 to 2026-07-15T14:30:00+08:00.

## Primary Root Cause
**Fan inverter airflow frequency instability** (confidence: 0.92)

Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 20% evidence.

## Data Quality
- Sensor rows: 17
- Alarm events: 6
- SOP sections: 4
- Maintenance records: 2

## Diagnostic Process
- ✅ **Data Loading**: Loaded manifest, 17 sensor rows, 6 alarm rows, SOP and maintenance records.
- ✅ **Data Validation**: Sensor rows: 17, Alarms: 6, SOP sections: 4, Maintenance records: 2.
- ✅ **Signal Anomaly Detection**: Detected 3 anomalies across 3 fields. Correlated findings: 2.
- ✅ **Alarm Correlation**: Parsed 6 alarm events. Alarm codes: AIR-305, DRY-110, DRY-122, QCS-318.
- ✅ **SOP & Maintenance Retrieval**: Retrieved 5 SOP sections and 2 maintenance records.
- ✅ **Root Cause Ranking**: Matched 3 candidates from 5 fault modes. Primary: Fan inverter airflow frequency instability (status: confirmed).
- ✅ **Evidence Sufficiency Decision**: Decision: confirmed.
- ✅ **Action Planning**: Generated 7 recommended actions across roles: equipment_engineer, production_supervisor, quality_engineer, safety_reviewer.
- ✅ **Report Generation**: Generated timeline (9 events), work order, evidence graph (43 links), and value estimates.

## Event Timeline
- **2026-07-15T14:04:20+08:00** [warning] Alarm AIR-305: Warning: Fan frequency below normal operating range (status: active)
- **2026-07-15T14:10:00+08:00** [major] fan_frequency_hz threshold violation: fan_frequency_hz fell below threshold at 41.5.
- **2026-07-15T14:10:30+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: active)
- **2026-07-15T14:10:45+08:00** [warning] Alarm DRY-110: Warning: Dryer zone 1 temperature approaching upper control limit (status: active)
- **2026-07-15T14:12:00+08:00** [major] dryer_zone_2_temp_c threshold violation: dryer_zone_2_temp_c exceeded threshold at 96.0.
- **2026-07-15T14:12:00+08:00** [major] thickness_um threshold violation: thickness_um exceeded threshold at 104.2.
- **2026-07-15T14:20:10+08:00** [warning] Alarm QCS-318: Warning: Coating thickness drift detected by inline inspection (status: active)
- **2026-07-15T14:26:30+08:00** [warning] Alarm AIR-305: Warning: Fan frequency below normal operating range (status: recovered)
- **2026-07-15T14:28:15+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: recovered)

## Root Cause Candidates
### RC-001: Fan inverter airflow frequency instability
- **Confidence**: 0.92 | **Priority**: high
- **Fault Mode**: FM-003
- **Diagnostic Role**: equipment_cause
- **Score Breakdown**: alarm=1.00, sensor=1.00, sop=1.00, maint=1.00, note=0.20 → total=0.92
- **Evidence**: EV-001, EV-005, EV-007, EV-008, EV-011, EV-012, EV-013, EV-014, EV-015, EV-016
- **Rationale**: Matched alarm codes: AIR-305. Anomalous sensor fields: dryer_zone_2_temp_c, fan_frequency_hz. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 20% evidence.

### RC-002: Dryer zone 2 temperature control loop instability
- **Confidence**: 0.92 | **Priority**: high
- **Fault Mode**: FM-001
- **Diagnostic Role**: equipment_cause
- **Score Breakdown**: alarm=1.00, sensor=1.00, sop=1.00, maint=1.00, note=0.17 → total=0.92
- **Evidence**: EV-002, EV-003, EV-006, EV-007, EV-011, EV-012, EV-013, EV-014, EV-015, EV-016
- **Rationale**: Matched alarm codes: DRY-110, DRY-122. Anomalous sensor fields: dryer_zone_2_temp_c. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 17% evidence.

## Downstream Effects and Business Risks
- **RC-003** Coating thickness drift and yield risk (0.74)

## Evidence
- **EV-001** (alarms.csv at 2026-07-15T14:04:20+08:00): AIR-305 warning alarm: Fan frequency below normal operating range = AIR-305
- **EV-002** (alarms.csv at 2026-07-15T14:10:30+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-003** (alarms.csv at 2026-07-15T14:10:45+08:00): DRY-110 warning alarm: Dryer zone 1 temperature approaching upper control limit = DRY-110
- **EV-004** (alarms.csv at 2026-07-15T14:20:10+08:00): QCS-318 warning alarm: Coating thickness drift detected by inline inspection = QCS-318
- **EV-005** (alarms.csv at 2026-07-15T14:26:30+08:00): AIR-305 warning alarm: Fan frequency below normal operating range = AIR-305
- **EV-006** (alarms.csv at 2026-07-15T14:28:15+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-007** (sensor_readings.csv at 2026-07-15T14:12:00+08:00): dryer_zone_2_temp_c above threshold at 96.0 [dryer_zone_2_temp_c] = 96.0
- **EV-008** (sensor_readings.csv at 2026-07-15T14:10:00+08:00): fan_frequency_hz below threshold at 41.5 [fan_frequency_hz] = 41.5
- **EV-009** (sensor_readings.csv at 2026-07-15T14:12:00+08:00): thickness_um above threshold at 104.2 [thickness_um] = 104.2
- **EV-010** (sop_airflow_temperature.md): SOP section 'Overview' is relevant to observed anomalies.
- **EV-011** (sop_airflow_temperature.md): SOP section 'AIR-305 Fan Frequency Below Normal' is relevant to observed anomalies.
- **EV-012** (sop_airflow_temperature.md): SOP section 'DRY-122 Dryer Zone Temperature Deviation' is relevant to observed anomalies.
- **EV-013** (sop_airflow_temperature.md): SOP section 'DRY-110 Dryer Zone 1 Temperature Approaching Limit' is relevant to observed anomalies.
- **EV-014** (sop_airflow_temperature.md): SOP section 'QCS-318 Thickness Drift' is relevant to observed anomalies.
- **EV-015** (maintenance_records.md): Maintenance record M-2026-057: Line: cell coating line B = M-2026-057
- **EV-016** (maintenance_records.md): Maintenance record M-2026-089: Line: cell coating line A = M-2026-089

## Evidence Graph
- RC-001 --[supported_by]--> EV-001
- RC-001 --[supported_by]--> EV-005
- RC-001 --[supported_by]--> EV-007
- RC-001 --[supported_by]--> EV-008
- RC-001 --[supported_by]--> EV-011
- RC-001 --[supported_by]--> EV-012
- RC-001 --[supported_by]--> EV-013
- RC-001 --[supported_by]--> EV-014
- RC-001 --[supported_by]--> EV-015
- RC-001 --[supported_by]--> EV-016
- RC-002 --[supported_by]--> EV-002
- RC-002 --[supported_by]--> EV-003
- RC-002 --[supported_by]--> EV-006
- RC-002 --[supported_by]--> EV-007
- RC-002 --[supported_by]--> EV-011
- RC-002 --[supported_by]--> EV-012
- RC-002 --[supported_by]--> EV-013
- RC-002 --[supported_by]--> EV-014
- RC-002 --[supported_by]--> EV-015
- RC-002 --[supported_by]--> EV-016
- RC-003 --[supported_by]--> EV-004
- RC-003 --[supported_by]--> EV-009
- RC-003 --[supported_by]--> EV-012
- RC-003 --[supported_by]--> EV-013
- RC-003 --[supported_by]--> EV-014
- RC-003 --[supported_by]--> EV-015
- RC-003 --[supported_by]--> EV-016
- EV-001 --[from_source]--> alarms.csv
- EV-002 --[from_source]--> alarms.csv
- EV-003 --[from_source]--> alarms.csv
- EV-004 --[from_source]--> alarms.csv
- EV-005 --[from_source]--> alarms.csv
- EV-006 --[from_source]--> alarms.csv
- EV-007 --[from_source]--> sensor_readings.csv
- EV-008 --[from_source]--> sensor_readings.csv
- EV-009 --[from_source]--> sensor_readings.csv
- EV-010 --[from_source]--> sop_airflow_temperature.md
- EV-011 --[from_source]--> sop_airflow_temperature.md
- EV-012 --[from_source]--> sop_airflow_temperature.md
- EV-013 --[from_source]--> sop_airflow_temperature.md
- EV-014 --[from_source]--> sop_airflow_temperature.md
- EV-015 --[from_source]--> maintenance_records.md
- EV-016 --[from_source]--> maintenance_records.md

## Recommended Actions
- **ACT-001** (inspect) [equipment_engineer]: Follow SOP: AIR-305 Fan Frequency Below Normal
  Per SOP section 'AIR-305 Fan Frequency Below Normal': Check fan inverter cooling module and heat sink condition.; Inspect airflow filter for blockage or contamination.; Verify fan inverter parameter settings and power supply stability.
  Linked: RC-001
- **ACT-002** (inspect) [equipment_engineer]: Follow SOP: DRY-122 Dryer Zone Temperature Deviation
  Per SOP section 'DRY-122 Dryer Zone Temperature Deviation': Confirm the recipe target temperature and upper/lower control limits.; Check temperature sensor wiring and calibration status.; Inspect heater relay response and controller output.
  Linked: RC-002
- **ACT-003** (inspect) [equipment_engineer]: Follow SOP: DRY-110 Dryer Zone 1 Temperature Approaching Limit
  Per SOP section 'DRY-110 Dryer Zone 1 Temperature Approaching Limit': Monitor zone 1 temperature trend and compare with zone 2.; Check if fan frequency drop is affecting airflow uniformity.; Verify zone 1 heater controller is responding correctly.
  Linked: RC-002
- **ACT-004** (inspect) [equipment_engineer]: Follow SOP: QCS-318 Thickness Drift
  Per SOP section 'QCS-318 Thickness Drift': Correlate drift time with temperature, tension and line speed changes.; Isolate affected material roll range.; Request quality engineer review before release.
  Linked: RC-003
- **ACT-005** (quality) [quality_engineer]: Quality engineer review of affected material
  Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
  Linked: RC-003
- **ACT-006** (escalate) [production_supervisor]: Notify production supervisor
  High-priority root causes detected: Fan inverter airflow frequency instability, Dryer zone 2 temperature control loop instability, Coating thickness drift and yield risk. Production supervisor should be notified for resource allocation and scheduling decisions.
  Linked: RC-001, RC-002, RC-003
- **ACT-007** (safety) [safety_reviewer]: Confirm safety procedures before equipment intervention
  All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.
  Linked: RC-001, RC-002, RC-003

## Work Order Draft
**Check cell coating line B dryer section airflow and temperature control** (priority: high, assignee: equipment engineer)

**Tasks:**
  1. Per SOP section 'AIR-305 Fan Frequency Below Normal': Check fan inverter cooling module and heat sink condition.; Inspect airflow filter for blockage or contamination.; Verify fan inverter parameter settings and power supply stability.
  1. Per SOP section 'DRY-122 Dryer Zone Temperature Deviation': Confirm the recipe target temperature and upper/lower control limits.; Check temperature sensor wiring and calibration status.; Inspect heater relay response and controller output.
  1. Per SOP section 'DRY-110 Dryer Zone 1 Temperature Approaching Limit': Monitor zone 1 temperature trend and compare with zone 2.; Check if fan frequency drop is affecting airflow uniformity.; Verify zone 1 heater controller is responding correctly.
  1. Per SOP section 'QCS-318 Thickness Drift': Correlate drift time with temperature, tension and line speed changes.; Isolate affected material roll range.; Request quality engineer review before release.
  1. Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
  1. High-priority root causes detected: Fan inverter airflow frequency instability, Dryer zone 2 temperature control loop instability, Coating thickness drift and yield risk. Production supervisor should be notified for resource allocation and scheduling decisions.
**Safety:**
  ⚠ All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.

## Business Value Estimates
### MTTR reduction target
- **Baseline**: 60 min configured pilot baseline
- **Projected**: 39 min at a 35% reduction target
- **Assumption**: Scenario calculation from case_manifest business_context; not a validated production result.
- **Configured**: yes

### Avoided downtime scenario
- **Baseline**: 120 currency units per downtime minute
- **Projected**: 2520 currency units per incident
- **Assumption**: Illustrative scenario only. Currency and plant cost must be configured and validated during a pilot.
- **Configured**: yes

## Agent Decisions
- **load** -> `continue`: All required case resources were loaded.
- **validate** -> `continue`: Case data passed quality checks without warnings.
- **assess_evidence** -> `confirmed`: Primary candidate has 92% confidence with sufficient evidence.


## Postmortem Summary
The incident likely originated from Fan inverter airflow frequency instability. No coupled secondary factor was confirmed; downstream effects should be reviewed by the quality team.

## Limitations
- This diagnosis is generated from synthetic demo data.
- Real equipment actions require factory safety procedures and engineer confirmation.
- Configured value estimates are scenario calculations, not validated production results.
- Deterministic analysis only – no LLM reasoning applied.
