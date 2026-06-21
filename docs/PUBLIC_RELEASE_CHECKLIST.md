# Public Release Checklist

ForgePulse should be published as a clean, reproducible project without local state, secrets, dependencies, or unverified deployment claims.

## Include

- source code and lockfiles;
- `README.md`, planning, delivery, architecture, safety, pilot, and evaluation documents;
- five public synthetic cases and their per-case golden expectations;
- deterministic evaluation output;
- five generated Markdown reports;
- desktop and mobile workbench screenshots;
- editable pitch deck;
- one-command verification and demo scripts.

## Exclude

- `node_modules/`, `dist/`, caches, and runtime PID/log files;
- `.env` files other than examples;
- AtomCode or local AI tool state;
- API keys, tokens, passwords, cookies, account data, or private production logs;
- claims of verified factory deployment or verified NPU execution.

## Required Verification

From the project root:

```powershell
.\scripts\verify.ps1
```

Expected result:

- `83` backend tests pass;
- evaluation is `71/71` across five cases;
- frontend production build succeeds;
- npm audit reports `0 vulnerabilities`;
- frontend static smoke validation passes.

## Manual Demo Path

```powershell
.\scripts\run_demo.ps1
```

Open `http://localhost:5173` and verify:

1. all five cases can be selected;
2. confirmed, insufficient-evidence, and conflicting-evidence states are distinguishable;
3. evidence IDs navigate to source evidence;
4. causes, factors, effects, actions, work order, and value sections render;
5. Markdown report export opens successfully;
6. desktop and mobile widths remain usable.

Stop the demo:

```powershell
.\scripts\stop_demo.ps1
```

## Repository Verification

Before push:

```powershell
git diff --cached --check
git status --short
git remote -v
```

After push:

- clone the public repository into a clean directory;
- run `.\scripts\verify.ps1`;
- verify README images and PPT download;
- verify the submitted URL points to the intended AtomGit repository.

## Public Summary

> ForgePulse is an evidence-grounded maintenance diagnosis Agent for battery coating lines. It analyzes sensor readings, alarms, SOPs, and maintenance records to produce traceable cause rankings, uncertainty decisions, role-based actions, work orders, and postmortem reports. It runs offline by default and includes five reproducible cases with 71 automated behavioral and integrity checks.

## Claim Boundary

ForgePulse is a submission-ready prototype for read-only historical-data evaluation. It must not be described as production deployed, autonomous equipment control, or verified on Ascend hardware until those claims have direct evidence.
