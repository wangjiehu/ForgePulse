# Security and Safety Boundaries

ForgePulse 的可信度取决于边界清楚。它是诊断辅助系统，不是自动控制系统。

## Runtime Security (Implemented)

The API enforces authentication, rate limiting, and audit logging
(`app/backend/forgepulse_api/security.py`):

- **API key auth**: clients send `X-API-Key: <key>`. Keys are configured via
  `FORGEPULSE_API_KEYS` as comma-separated `<key>:<role>` entries where role is
  `viewer|engineer|admin`. Unknown or missing key → `401`.
- **RBAC**: `require_role(...)` dependency gates write-class endpoints by role.
  All current endpoints are read-only (`viewer` sufficient); the hook exists for
  future POST endpoints.
- **Rate limiting**: in-memory sliding-window token bucket, `FORGEPULSE_RATE_LIMIT`
  requests per key per minute (default 60). Exceeded → `429`. Open mode
  (no keys configured) rate-limits by client IP instead.
- **Audit log**: every request is appended as a JSON line to
  `FORGEPULSE_AUDIT_LOG` (default `logs/audit.jsonl`) with timestamp, masked
  key id, role, method, path, status, latency, and client IP.

**Open mode**: when `FORGEPULSE_API_KEYS` is unset, the API runs without auth for
local development and logs a prominent warning. **Open mode must NOT be used in
production.** Set at least one API key before any external exposure.

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
