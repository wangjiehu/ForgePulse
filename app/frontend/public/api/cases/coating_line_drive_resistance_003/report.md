# Diagnosis Report: coating_line_drive_resistance_003

**Diagnosis status:** `confirmed`

## Incident Summary
Drive current elevation and web tension instability due to roller contamination. Primary root cause: Drive current resistance from roller surface contamination. Incident window: 2026-08-22T09:00:00+08:00 to 2026-08-22T09:30:00+08:00.

## Primary Root Cause
**Drive current resistance from roller surface contamination** (confidence: 0.94)

Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 42% evidence.

## Data Quality
- Sensor rows: 17
- Alarm events: 5
- SOP sections: 4
- Maintenance records: 2

## Diagnostic Process
- ✅ **Data Loading**: Loaded manifest, 17 sensor rows, 5 alarm rows, SOP and maintenance records.
- ✅ **Data Validation**: Sensor rows: 17, Alarms: 5, SOP sections: 4, Maintenance records: 2.
- ✅ **Signal Anomaly Detection**: Detected 3 anomalies across 3 fields. Correlated findings: 1.
- ✅ **Alarm Correlation**: Parsed 5 alarm events. Alarm codes: DRV-410, QCS-318, TEN-204.
- ✅ **SOP & Maintenance Retrieval**: Retrieved 5 SOP sections and 2 maintenance records.
- ✅ **Root Cause Ranking**: Matched 3 candidates from 5 fault modes. Primary: Drive current resistance from roller surface contamination (status: confirmed).
- ✅ **Evidence Sufficiency Decision**: Decision: confirmed.
- ✅ **Action Planning**: Generated 7 recommended actions across roles: equipment_engineer, production_supervisor, quality_engineer, safety_reviewer.
- ✅ **Report Generation**: Generated timeline (8 events), work order, evidence graph (45 links), and value estimates.

## Event Timeline
- **2026-08-22T09:04:30+08:00** [warning] Alarm DRV-410: Warning: Drive current above normal operating range (status: active)
- **2026-08-22T09:08:20+08:00** [major] Alarm TEN-204: Major: Web tension oscillation exceeds warning band (status: active)
- **2026-08-22T09:12:00+08:00** [major] web_tension_n threshold violation: web_tension_n exceeded threshold at 138.1.
- **2026-08-22T09:12:00+08:00** [major] drive_current_a threshold violation: drive_current_a exceeded threshold at 15.2.
- **2026-08-22T09:18:40+08:00** [warning] Alarm QCS-318: Warning: Coating thickness drift detected by inline inspection (status: active)
- **2026-08-22T09:20:00+08:00** [major] thickness_um threshold violation: thickness_um exceeded threshold at 105.3.
- **2026-08-22T09:24:10+08:00** [warning] Alarm DRV-410: Warning: Drive current above normal operating range (status: recovered)
- **2026-08-22T09:26:30+08:00** [major] Alarm TEN-204: Major: Web tension oscillation exceeds warning band (status: recovered)

## Root Cause Candidates
### RC-001: Drive current resistance from roller surface contamination
- **Confidence**: 0.94 | **Priority**: high
- **Fault Mode**: FM-004
- **Diagnostic Role**: equipment_cause
- **Score Breakdown**: alarm=1.00, sensor=1.00, sop=1.00, maint=1.00, note=0.42 → total=0.94
- **Evidence**: EV-001, EV-002, EV-004, EV-005, EV-006, EV-007, EV-008, EV-010, EV-011, EV-012, EV-013, EV-014, EV-015
- **Rationale**: Matched alarm codes: DRV-410, TEN-204. Anomalous sensor fields: drive_current_a, thickness_um, web_tension_n. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 42% evidence.

### RC-002: Web tension closed-loop response lag
- **Confidence**: 0.82 | **Priority**: high
- **Fault Mode**: FM-002
- **Diagnostic Role**: coupled_secondary_factor
- **Score Breakdown**: alarm=1.00, sensor=1.00, sop=1.00, maint=1.00, note=0.14 → total=0.82
- **Evidence**: EV-002, EV-005, EV-006, EV-010, EV-011, EV-012, EV-013, EV-014, EV-015
- **Rationale**: Matched alarm codes: TEN-204. Anomalous sensor fields: web_tension_n. SOP sections provide relevant check procedures. Historical maintenance records show similar patterns.
- **Why Ranked**: Ranked from alarm 100%, sensor 100%, SOP 100%, maintenance 100%, and operator note 14% evidence.

## Contributing Factors
- **RC-002** Web tension closed-loop response lag (0.82)

## Downstream Effects and Business Risks
- **RC-003** Coating thickness drift and yield risk (0.74)

## Evidence
- **EV-001** (alarms.csv at 2026-08-22T09:04:30+08:00): DRV-410 warning alarm: Drive current above normal operating range = DRV-410
- **EV-002** (alarms.csv at 2026-08-22T09:08:20+08:00): TEN-204 major alarm: Web tension oscillation exceeds warning band = TEN-204
- **EV-003** (alarms.csv at 2026-08-22T09:18:40+08:00): QCS-318 warning alarm: Coating thickness drift detected by inline inspection = QCS-318
- **EV-004** (alarms.csv at 2026-08-22T09:24:10+08:00): DRV-410 warning alarm: Drive current above normal operating range = DRV-410
- **EV-005** (alarms.csv at 2026-08-22T09:26:30+08:00): TEN-204 major alarm: Web tension oscillation exceeds warning band = TEN-204
- **EV-006** (sensor_readings.csv at 2026-08-22T09:12:00+08:00): web_tension_n above threshold at 138.1 [web_tension_n] = 138.1
- **EV-007** (sensor_readings.csv at 2026-08-22T09:12:00+08:00): drive_current_a above threshold at 15.2 [drive_current_a] = 15.2
- **EV-008** (sensor_readings.csv at 2026-08-22T09:20:00+08:00): thickness_um above threshold at 105.3 [thickness_um] = 105.3
- **EV-009** (sop_drive_tension.md): SOP section 'Overview' is relevant to observed anomalies.
- **EV-010** (sop_drive_tension.md): SOP section 'DRV-410 Drive Current Above Normal Range' is relevant to observed anomalies.
- **EV-011** (sop_drive_tension.md): SOP section 'TEN-204 Web Tension Oscillation' is relevant to observed anomalies.
- **EV-012** (sop_drive_tension.md): SOP section 'QCS-318 Thickness Drift' is relevant to observed anomalies.
- **EV-013** (sop_drive_tension.md): SOP section 'Roller Contamination Response' is relevant to observed anomalies.
- **EV-014** (maintenance_records.md): Maintenance record M-2026-103: Line: cell coating line A = M-2026-103
- **EV-015** (maintenance_records.md): Maintenance record M-2026-078: Line: cell coating line C = M-2026-078

## Evidence Graph
- RC-001 --[supported_by]--> EV-001
- RC-001 --[supported_by]--> EV-002
- RC-001 --[supported_by]--> EV-004
- RC-001 --[supported_by]--> EV-005
- RC-001 --[supported_by]--> EV-006
- RC-001 --[supported_by]--> EV-007
- RC-001 --[supported_by]--> EV-008
- RC-001 --[supported_by]--> EV-010
- RC-001 --[supported_by]--> EV-011
- RC-001 --[supported_by]--> EV-012
- RC-001 --[supported_by]--> EV-013
- RC-001 --[supported_by]--> EV-014
- RC-001 --[supported_by]--> EV-015
- RC-002 --[supported_by]--> EV-002
- RC-002 --[supported_by]--> EV-005
- RC-002 --[supported_by]--> EV-006
- RC-002 --[supported_by]--> EV-010
- RC-002 --[supported_by]--> EV-011
- RC-002 --[supported_by]--> EV-012
- RC-002 --[supported_by]--> EV-013
- RC-002 --[supported_by]--> EV-014
- RC-002 --[supported_by]--> EV-015
- RC-003 --[supported_by]--> EV-003
- RC-003 --[supported_by]--> EV-008
- RC-003 --[supported_by]--> EV-010
- RC-003 --[supported_by]--> EV-011
- RC-003 --[supported_by]--> EV-012
- RC-003 --[supported_by]--> EV-013
- RC-003 --[supported_by]--> EV-014
- RC-003 --[supported_by]--> EV-015
- EV-001 --[from_source]--> alarms.csv
- EV-002 --[from_source]--> alarms.csv
- EV-003 --[from_source]--> alarms.csv
- EV-004 --[from_source]--> alarms.csv
- EV-005 --[from_source]--> alarms.csv
- EV-006 --[from_source]--> sensor_readings.csv
- EV-007 --[from_source]--> sensor_readings.csv
- EV-008 --[from_source]--> sensor_readings.csv
- EV-009 --[from_source]--> sop_drive_tension.md
- EV-010 --[from_source]--> sop_drive_tension.md
- EV-011 --[from_source]--> sop_drive_tension.md
- EV-012 --[from_source]--> sop_drive_tension.md
- EV-013 --[from_source]--> sop_drive_tension.md
- EV-014 --[from_source]--> maintenance_records.md
- EV-015 --[from_source]--> maintenance_records.md

## Recommended Actions
- **ACT-001** (inspect) [equipment_engineer]: Follow SOP: DRV-410 Drive Current Above Normal Range
  Per SOP section 'DRV-410 Drive Current Above Normal Range': Check roller surface condition for contamination, wear, or material buildup.; Inspect drive belt tension and alignment.; Check bearing condition and lubrication.
  Linked: RC-001
- **ACT-002** (inspect) [equipment_engineer]: Follow SOP: TEN-204 Web Tension Oscillation
  Per SOP section 'TEN-204 Web Tension Oscillation': Check dancer roller position feedback.; Check tension controller response after recipe switch.; Inspect drive current trend and roller surface contamination.
  Linked: RC-002
- **ACT-003** (inspect) [equipment_engineer]: Follow SOP: QCS-318 Thickness Drift
  Per SOP section 'QCS-318 Thickness Drift': Correlate drift time with temperature, tension and line speed changes.; Isolate affected material roll range.; Request quality engineer review before release.
  Linked: RC-003
- **ACT-004** (inspect) [equipment_engineer]: Follow SOP: Roller Contamination Response
  Per SOP section 'Roller Contamination Response': Prioritize roller surface inspection – contamination can cause both elevated drive current and tension instability.; Check if recent coating material change or process adjustment increased residue buildup.; Schedule roller cleaning during next planned stop if immediate stop is not warranted.
  Linked: RC-001, RC-002
- **ACT-005** (quality) [quality_engineer]: Quality engineer review of affected material
  Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
  Linked: RC-003
- **ACT-006** (escalate) [production_supervisor]: Notify production supervisor
  High-priority root causes detected: Drive current resistance from roller surface contamination, Web tension closed-loop response lag, Coating thickness drift and yield risk. Production supervisor should be notified for resource allocation and scheduling decisions.
  Linked: RC-001, RC-002, RC-003
- **ACT-007** (safety) [safety_reviewer]: Confirm safety procedures before equipment intervention
  All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.
  Linked: RC-001, RC-002, RC-003

## Work Order Draft
**Check cell coating line A drive system and web tension control** (priority: high, assignee: equipment engineer)

**Tasks:**
  1. Per SOP section 'DRV-410 Drive Current Above Normal Range': Check roller surface condition for contamination, wear, or material buildup.; Inspect drive belt tension and alignment.; Check bearing condition and lubrication.
  1. Per SOP section 'TEN-204 Web Tension Oscillation': Check dancer roller position feedback.; Check tension controller response after recipe switch.; Inspect drive current trend and roller surface contamination.
  1. Per SOP section 'QCS-318 Thickness Drift': Correlate drift time with temperature, tension and line speed changes.; Isolate affected material roll range.; Request quality engineer review before release.
  1. Per SOP section 'Roller Contamination Response': Prioritize roller surface inspection – contamination can cause both elevated drive current and tension instability.; Check if recent coating material change or process adjustment increased residue buildup.; Schedule roller cleaning during next planned stop if immediate stop is not warranted.
  1. Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.
  1. High-priority root causes detected: Drive current resistance from roller surface contamination, Web tension closed-loop response lag, Coating thickness drift and yield risk. Production supervisor should be notified for resource allocation and scheduling decisions.
**Safety:**
  ⚠ All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.

## Business Value Estimates
### MTTR reduction target
- **Baseline**: 45 min configured pilot baseline
- **Projected**: 31 min at a 30% reduction target
- **Assumption**: Scenario calculation from case_manifest business_context; not a validated production result.
- **Configured**: yes

### Avoided downtime scenario
- **Baseline**: 90 currency units per downtime minute
- **Projected**: 1215 currency units per incident
- **Assumption**: Illustrative scenario only. Currency and plant cost must be configured and validated during a pilot.
- **Configured**: yes

## Agent Decisions
- **load** -> `continue`: All required case resources were loaded.
- **validate** -> `continue`: Case data passed quality checks without warnings.
- **assess_evidence** -> `confirmed`: Primary candidate has 94% confidence with sufficient evidence.


## Postmortem Summary
The incident likely originated from Drive current resistance from roller surface contamination, with Web tension closed-loop response lag as a coupled secondary factor. Downstream effects should be reviewed by the quality team.

## Limitations
- This diagnosis is generated from synthetic demo data.
- Real equipment actions require factory safety procedures and engineer confirmation.
- Configured value estimates are scenario calculations, not validated production results.
- Deterministic analysis only – no LLM reasoning applied.
