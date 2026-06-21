# AI Build Log

ForgePulse was designed, implemented, reviewed, and tested through AI-assisted engineering workflows. This document records reproducible engineering evidence without exposing private prompts, tokens, accounts, or hidden reasoning.

## Build Principles

- Deterministic diagnosis is the source of truth.
- Every conclusion must reference input evidence.
- Model access is optional and narrative-only.
- The Agent may abstain or request verification.
- Public data is synthetic and contains no customer information.
- No equipment control, safety interlock bypass, or automatic quality release is implemented.

## AI-assisted Workstreams

| Workstream | AI contribution | Human-verifiable evidence |
|---|---|---|
| Product framing | Narrowed scope to battery coating-line diagnosis | `docs/DECISION_REVIEW.md` |
| Architecture | Defined bounded Agent states and evidence contracts | `docs/SYSTEM_ARCHITECTURE.md` |
| Implementation | Generated backend, frontend, tests, and scripts | `app/`, `scripts/` |
| Diagnosis hardening | Found and fixed ranking and retrieval-score defects | Tests and evaluation |
| Safety | Added abstention, conflict handling, and read-only boundaries | Cases 004/005 |
| UX | Built an engineer workbench with evidence navigation | `app/frontend/src/` |
| Verification | Added unit, behavioral, counterfactual, determinism, build, audit, and smoke gates | `scripts/verify.ps1` |

## AtomCode Workflow

AtomCode can be used to:

1. Read project contracts and plans.
2. Implement changes under the bounded diagnosis architecture.
3. Run `scripts/verify.ps1`.
4. Review failures and update tests before accepting changes.
5. Use optional models only for explanation wording.

This repository does not claim that a model replaced engineering review.

## Reproduction

```powershell
.\scripts\verify.ps1
```

Expected gates:

- Backend tests pass.
- Five-case evaluation passes.
- Frontend production build passes.
- Dependency audit reports no high-severity vulnerabilities.
- Frontend smoke passes.

## Evidence Boundary

Do not commit API keys, real factory logs, private customer prompts, account identifiers, browser sessions, or unverified NPU performance claims.
