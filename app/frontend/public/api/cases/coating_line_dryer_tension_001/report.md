# Diagnosis Report: coating_line_dryer_tension_001

**Diagnosis status:** `confirmed`

## Incident Summary
Coating line dryer temperature deviation with web tension oscillation. Primary root cause: Dryer zone 2 temperature control loop instability. Incident window: 2026-06-10T10:10:00+08:00 to 2026-06-10T10:30:00+08:00.

## Primary Root Cause
**Dryer zone 2 temperature control loop instability** (confidence: 0.91)

Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 13% evidence.

## Data Quality
- Sensor rows: 12
- Alarm events: 5
- SOP sections: 3
- Maintenance records: 2

## Diagnostic Process
- ✅ **Data Loading**: Loaded manifest, 12 sensor rows, 5 alarm rows, SOP and maintenance records.
- ✅ **Data Validation**: Sensor rows: 12, Alarms: 5, SOP sections: 3, Maintenance records: 2.
- ✅ **Signal Anomaly Detection**: Detected 3 anomalies across 3 fields. Correlated findings: 3.
- ✅ **Alarm Correlation**: Parsed 5 alarm events. Alarm codes: DRY-122, QCS-318, TEN-204.
- ✅ **SOP & Maintenance Retrieval**: Retrieved 4 SOP sections and 2 maintenance records.
- ✅ **Root Cause Ranking**: Matched 3 candidates from 5 fault modes. Primary: Dryer zone 2 temperature control loop instability (status: confirmed).
- ✅ **Evidence Sufficiency Decision**: Decision: confirmed.
- ✅ **Action Planning**: Generated 6 recommended actions across roles: equipment_engineer, production_supervisor, quality_engineer, safety_reviewer.
- ✅ **Report Generation**: Generated timeline (8 events), work order, evidence graph (34 links), and value estimates.

## Event Timeline
- **2026-06-10T10:12:30+08:00** [warning] Alarm TEN-204: Warning: Web tension oscillation exceeds warning band (status: active)
- **2026-06-10T10:18:00+08:00** [major] web_tension_n threshold violation: web_tension_n exceeded threshold at 139.2.
- **2026-06-10T10:18:10+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: active)
- **2026-06-10T10:20:00+08:00** [major] dryer_zone_2_temp_c threshold violation: dryer_zone_2_temp_c exceeded threshold at 97.1.
- **2026-06-10T10:22:00+08:00** [major] thickness_um threshold violation: thickness_um exceeded threshold at 106.3.
- **2026-06-10T10:22:40+08:00** [warning] Alarm QCS-318: Warning: Coating thickness drift detected by inline inspection (status: active)
- **2026-06-10T10:28:20+08:00** [warning] Alarm TEN-204: Warning: Web tension oscillation exceeds warning band (status: recovered)
- **2026-06-10T10:30:15+08:00** [major] Alarm DRY-122: Major: Dryer zone 2 temperature deviation above control band (status: recovered)

## Root Cause Candidates
### RC-001: Dryer zone 2 temperature control loop instability
- **Confidence**: 0.91 | **Priority**: high
- **Fault Mode**: FM-001
- **Diagnostic Role**: equipment_cause
- **Score Breakdown**: alarm=1.00, sensor=1.00, sop=1.00, maint=1.00, note=0.13 → total=0.91
- **Evidence**: EV-002, EV-005, EV-006, EV-010, EV-012, EV-013, EV-014
- **Rationale**: Matched alarm codes: DRY-122. Anomalous sensor fields: dryer_zone_2_temp_c. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 13% evidence.

### RC-002: Web tension closed-loop response lag
- **Confidence**: 0.82 | **Priority**: high
- **Fault Mode**: FM-002
- **Diagnostic Role**: coupled_secondary_factor
- **Score Breakdown**: alarm=1.00, sensor=1.00, sop=1.00, maint=0.50, note=0.21 → total=0.82
- **Evidence**: EV-001, EV-004, EV-007, EV-011, EV-012, EV-013
- **Rationale**: Matched alarm codes: TEN-204. Anomalous sensor fields: web_tension_n. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 50%, and operator note 21% evidence.

## Contributing Factors
- **RC-002** Web tension closed-loop response lag (0.82)

## Downstream Effects and Business Risks
- **RC-003** Coating thickness drift and yield risk (0.74)

## Evidence
- **EV-001** (alarms.csv at 2026-06-10T10:12:30+08:00): TEN-204 warning alarm: Web tension oscillation exceeds warning band = TEN-204
- **EV-002** (alarms.csv at 2026-06-10T10:18:10+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-003** (alarms.csv at 2026-06-10T10:22:40+08:00): QCS-318 warning alarm: Coating thickness drift detected by inline inspection = QCS-318
- **EV-004** (alarms.csv at 2026-06-10T10:28:20+08:00): TEN-204 warning alarm: Web tension oscillation exceeds warning band = TEN-204
- **EV-005** (alarms.csv at 2026-06-10T10:30:15+08:00): DRY-122 major alarm: Dryer zone 2 temperature deviation above control band = DRY-122
- **EV-006** (sensor_readings.csv at 2026-06-10T10:20:00+08:00): dryer_zone_2_temp_c above threshold at 97.1 [dryer_zone_2_temp_c] = 97.1
- **EV-007** (sensor_readings.csv at 2026-06-10T10:18:00+08:00): web_tension_n above threshold at 139.2 [web_tension_n] = 139.2
- **EV-008** (sensor_readings.csv at 2026-06-10T10:22:00+08:00): thickness_um above threshold at 106.3 [thickness_um] = 106.3
- **EV-009** (sop_dryer_tension.md): SOP section 'Overview' is relevant to observed anomalies.
- **EV-010** (sop_dryer_tension.md): SOP section 'DRY-122 Dryer Zone Temperature Deviation' is relevant to observed anomalies.
- **EV-011** (sop_dryer_tension.md): SOP section 'TEN-204 Web Tension Oscillation' is relevant to observed anomalies.
- **EV-012** (sop_dryer_tension.md): SOP section 'QCS-318 Thickness Drift' is relevant to observed anomalies.
- **EV-013** (maintenance_records.md): Maintenance record M-2026-041: Line: cell coating line A = M-2026-041
- **EV-014** (maintenance_records.md): Maintenance record M-2026-057: Line: cell coating line B = M-2026-057

## Evidence Graph
- RC-001 --[supported_by]--> EV-002
- RC-001 --[supported_by]--> EV-005
- RC-001 --[supported_by]--> EV-006
- RC-001 --[supported_by]--> EV-010
- RC-001 --[supported_by]--> EV-012
- RC-001 --[supported_by]--> EV-013
- RC-001 --[supported_by]--> EV-014
- RC-002 --[supported_by]--> EV-001
- RC-002 --[supported_by]--> EV-004
- RC-002 --[supported_by]--> EV-007
- RC-002 --[supported_by]--> EV-011
- RC-002 --[supported_by]--> EV-012
- RC-002 --[supported_by]--> EV-013
- RC-003 --[supported_by]--> EV-003
- RC-003 --[supported_by]--> EV-008
- RC-003 --[supported_by]--> EV-010
- RC-003 --[supported_by]--> EV-011
- RC-003 --[supported_by]--> EV-012
- RC-003 --[supported_by]--> EV-013
- RC-003 --[supported_by]--> EV-014
- EV-001 --[from_source]--> alarms.csv
- EV-002 --[from_source]--> alarms.csv
- EV-003 --[from_source]--> alarms.csv
- EV-004 --[from_source]--> alarms.csv
- EV-005 --[from_source]--> alarms.csv
- EV-006 --[from_source]--> sensor_readings.csv
- EV-007 --[from_source]--> sensor_readings.csv
- EV-008 --[from_source]--> sensor_readings.csv
- EV-009 --[from_source]--> sop_dryer_tension.md
- EV-010 --[from_source]--> sop_dryer_tension.md
- EV-011 --[from_source]--> sop_dryer_tension.md
- EV-012 --[from_source]--> sop_dryer_tension.md
- EV-013 --[from_source]--> maintenance_records.md
- EV-014 --[from_source]--> maintenance_records.md

## Recommended Actions
- **ACT-001** (inspect) [equipment_engineer]: Follow SOP: DRY-122 Dryer Zone Temperature Deviation
  Per SOP section 'DRY-122 Dryer Zone Temperature Deviation': Confirm the recipe target temperature and upper/lower control limits.; Check temperature sensor wiring and calibration status.; Inspect heater relay response and controller output.
  Linked: RC-001
- **ACT-002** (inspect) [equipment_engineer]: Follow SOP: TEN-204 Web Tension Oscillation
  Per SOP section 'TEN-204 Web Tension Oscillation': Check dancer roller position feedback.; Check tension controller response after recipe switch.; Inspect drive current trend and roller surface contamination.
  Linked: RC-001, RC-002
- **ACT-003** (inspect) [equipment_engineer]: Follow SOP: QCS-318 Thickness Drift
  Per SOP section 'QCS-318 Thickness Drift': Correlate drift time with temperature, tension and line speed changes.; Isolate affected material roll range.; Request quality engineer review before release.
  Linked: RC-003
- **ACT-004** (quality) [quality_engineer]: Quality engineer review of affected material
  Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
  Linked: RC-003
- **ACT-005** (escalate) [production_supervisor]: Notify production supervisor
  High-priority root causes detected: Dryer zone 2 temperature control loop instability, Web tension closed-loop response lag, Coating thickness drift and yield risk. Production supervisor should be notified for resource allocation and scheduling decisions.
  Linked: RC-001, RC-002, RC-003
- **ACT-006** (safety) [safety_reviewer]: Confirm safety procedures before equipment intervention
  All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.
  Linked: RC-001, RC-002, RC-003

## Work Order Draft
**Check cell coating line A dryer section and web tension control** (priority: high, assignee: equipment engineer)

**Tasks:**
  1. Per SOP section 'DRY-122 Dryer Zone Temperature Deviation': Confirm the recipe target temperature and upper/lower control limits.; Check temperature sensor wiring and calibration status.; Inspect heater relay response and controller output.
  1. Per SOP section 'TEN-204 Web Tension Oscillation': Check dancer roller position feedback.; Check tension controller response after recipe switch.; Inspect drive current trend and roller surface contamination.
  1. Per SOP section 'QCS-318 Thickness Drift': Correlate drift time with temperature, tension and line speed changes.; Isolate affected material roll range.; Request quality engineer review before release.
  1. Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
  1. High-priority root causes detected: Dryer zone 2 temperature control loop instability, Web tension closed-loop response lag, Coating thickness drift and yield risk. Production supervisor should be notified for resource allocation and scheduling decisions.
**Safety:**
  ⚠ All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.

## Business Value Estimates
### MTTR reduction target
- **Baseline**: 50 min configured pilot baseline
- **Projected**: 30 min at a 40% reduction target
- **Assumption**: Scenario calculation from case_manifest business_context; not a validated production result.
- **Configured**: yes

### Avoided downtime scenario
- **Baseline**: 100 currency units per downtime minute
- **Projected**: 2000 currency units per incident
- **Assumption**: Illustrative scenario only. Currency and plant cost must be configured and validated during a pilot.
- **Configured**: yes

## Agent Decisions
- **load** -> `continue`: All required case resources were loaded.
- **validate** -> `continue`: Case data passed quality checks without warnings.
- **assess_evidence** -> `confirmed`: Primary candidate has 91% confidence with sufficient evidence.


## Postmortem Summary
The incident likely originated from Dryer zone 2 temperature control loop instability, with Web tension closed-loop response lag as a coupled secondary factor. Downstream effects should be reviewed by the quality team.

## Limitations
- This diagnosis is generated from synthetic demo data.
- Real equipment actions require factory safety procedures and engineer confirmation.
- Configured value estimates are scenario calculations, not validated production results.
- Deterministic analysis only – no LLM reasoning applied.
