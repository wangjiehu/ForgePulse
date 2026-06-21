# Next Strategic Work Plan

This document records the remaining high-value work after the verified ForgePulse baseline.

## Verified Baseline

- Backend tests: `83 passed`.
- Evaluation: `71/71`, all five cases pass.
- Cases cover confirmed diagnosis, insufficient evidence, and conflicting evidence.
- Frontend build and static smoke checks pass.
- npm audit reports `0 vulnerabilities`.
- Desktop and mobile screenshots have been visually reviewed.
- Five deterministic Markdown reports and one editable 9-slide pitch deck are included.
- One-command verify, run, and stop scripts are available on Windows.
- Offline deterministic diagnosis is the default; optional model output is narrative-only and evidence guarded.

## Product Position

ForgePulse is a read-only, evidence-grounded maintenance diagnosis Agent for battery coating lines. It is ready for public submission and controlled historical-data evaluation. It is not yet validated as a production factory system.

The product should continue to optimize for:

- diagnostic trust;
- traceability;
- conservative handling of uncertainty;
- fast deployment in a read-only pilot;
- measurable engineering value.

It should not expand into generic chat, equipment control, or broad cross-industry workflows before the coating-line diagnosis has been validated with real users and data.

## Remaining High-value Work

### 1. Publish to the Official AtomGit Repository

External prerequisite:

- official repository URL;
- authenticated AtomGit account;
- final team and submission metadata.

Required actions:

- add the official remote;
- push the reviewed `main` branch;
- verify README rendering, images, and downloadable PPT;
- run the public clone-and-verify path on a clean machine or directory;
- submit the exact repository URL through the competition channel.

This is release work, not a product feature.

### 2. Conduct a Blind Historical-incident Review

External prerequisite:

- de-identified historical incidents;
- at least one equipment engineer and one quality engineer.

Protocol:

- remove known labels from the input;
- have ForgePulse and human reviewers analyze the same incidents independently;
- compare primary cause, evidence completeness, unsafe overclaims, proposed checks, and report usefulness;
- record disagreements instead of tuning the system during scoring.

Minimum useful sample:

- 10 to 20 incidents across confirmed, incomplete, and conflicting evidence;
- at least two failure families not represented in the public demo.

This is the strongest remaining step because it converts internal correctness into credible external evidence.

### 3. Verify the Ascend/NPU Route on Real Hardware

External prerequisite:

- supported Ascend hardware and drivers;
- an approved model/runtime combination;
- permission to install and benchmark the integration.

Measure:

- model load success;
- narrative latency and throughput;
- memory use;
- failure fallback to deterministic offline mode;
- evidence-ID guard behavior under model output.

Do not claim NPU deployment until this test has been completed and recorded.

### 4. Record the Final Demo Video

External prerequisite:

- screen-recording or video encoding tooling;
- final public repository URL and submission wording.

The video should show:

- a confirmed case;
- an insufficient-evidence case;
- a conflicting-evidence case;
- evidence navigation;
- action and work-order output;
- report export;
- explicit read-only and human-review boundaries.

The existing script and workbench are ready; the remaining work is media production.

## Work Not Worth Adding Now

The following items have low marginal value before real pilot evidence:

- login, RBAC, or multi-tenant SaaS administration;
- a vector database for five public cases;
- generic chat as the primary interface;
- automatic equipment control or quality release;
- more synthetic happy-path cases without a new failure mode;
- cross-industry templates;
- decorative animation or a marketing landing page;
- replacing the deterministic diagnosis engine with an LLM.

These additions would increase surface area without proving better diagnosis.

## Exit Criteria

ForgePulse can be described as market-pilot ready only after:

- a clean public repository can be cloned and verified;
- domain experts complete blind historical-incident review;
- the pilot metrics and disagreements are documented;
- any claimed Ascend/NPU path is tested on actual hardware.

Until then, the accurate claim is:

> A submission-ready, evidence-grounded industrial Agent prototype with a reproducible offline benchmark and a documented read-only pilot path.
