# Security and Safety Boundaries

ForgePulse 的可信度取决于边界清楚。它是诊断辅助系统，不是自动控制系统。

## Non-negotiable Boundaries

ForgePulse must not:

- Control production equipment.
- Disable alarms or safety interlocks.
- Replace on-site engineer approval.
- Make autonomous quality release decisions.
- Store real customer secrets in the repository.
- Publish real production data without approval and anonymization.

## Data Security

### Public repository

Allowed:

- Synthetic sample data.
- Public documentation.
- Demo fault modes.
- No real factory identifiers.

Not allowed:

- Real customer names.
- Real equipment serial numbers.
- Credentials, API keys, tokens, passwords.
- Private production logs.
- Personal contact information from operators.

### Factory pilot

Recommended:

- Read-only connector.
- Local deployment inside factory network.
- Role-based access for reports.
- Data retention policy.
- Audit trail for generated reports.

## Safety Model

ForgePulse output should be treated as:

- Advisory diagnosis.
- Evidence organization.
- Work-order draft.
- Postmortem draft.

ForgePulse output should not be treated as:

- Final equipment command.
- Safety clearance.
- Quality release approval.
- Root-cause certainty without human review.

## Required Limitations in Reports

Every generated report should include:

- Diagnosis is based on available data.
- Missing or inconsistent data may affect conclusions.
- Final equipment intervention requires on-site engineer confirmation.
- Safety procedures and interlocks must not be bypassed.
- Quality release decisions require authorized quality review.

## LLM Guardrails

If an LLM provider is added later:

- LLM output must be schema-validated.
- LLM must not invent evidence IDs.
- LLM must not invent sensor readings.
- LLM must not invent SOP clauses.
- LLM must not issue device-control instructions.
- Deterministic evidence remains the source of truth.

## Failure Modes to Handle

ForgePulse should explicitly say “insufficient evidence” when:

- Required sensor fields are missing.
- Alarm timestamps do not overlap the incident window.
- SOP retrieval finds no relevant procedures.
- Maintenance records conflict with sensor evidence.
- A root cause has weak evidence.

## Safe Language

Use:

- “likely”
- “candidate”
- “requires confirmation”
- “recommended check”
- “based on available evidence”

Avoid:

- “confirmed”
- “guaranteed”
- “automatically fix”
- “safe to bypass”
- “replace engineer”
