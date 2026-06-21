# ForgePulse Evaluation Rubric

## Score Bands

### 0 - Not usable

- No clear industry scenario.
- Output is generic advice.
- No evidence.

### 1 - Basic

- Identifies the incident window.
- Produces at least one relevant root-cause candidate.
- Has limited evidence.

### 2 - Good

- Uses sensor, alarm and document evidence.
- Produces reasonable actions.
- Generates a usable work order.

### 3 - Excellent

- Explains coupled failure logic.
- Ranks causes with evidence.
- Separates immediate checks, stop-required checks and quality actions.
- Produces a report suitable for review.

## Golden Case Expectations

For `coating_line_dryer_tension_001`, a strong diagnosis should:

- Mention dryer zone 2 temperature control loop instability.
- Mention web tension response lag.
- Mention thickness drift risk.
- Reference DRY-122, TEN-204 and QCS-318.
- Reference maintenance record M-2026-041.
- Warn that final equipment action requires engineer confirmation.
