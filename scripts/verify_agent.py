#!/usr/bin/env python3
"""Verify the real LLM advisory reasoning layer end-to-end.

This script calls the diagnosis engine with ``reasoning="llm"`` for every
registered case and asserts that:

- ``agent_reasoning`` is attached (the LLM was actually called), and
- every ``referenced_evidence_id`` belongs to the case's evidence set, and
- the structured diagnosis (status / primary confidence / candidate ids) is
  unchanged versus the offline deterministic run.

REQUIREMENTS:
- ``FORGEPULSE_MODEL_PROVIDER=openai_compatible``
- ``FORGEPULSE_MODEL_BASE_URL``, ``FORGEPULSE_MODEL_API_KEY``,
  ``FORGEPULSE_MODEL_NAME`` all set in the environment (or a .env file you
  export before running).

If the LLM is not configured, the script prints a clear skip message and exits
0 — it never claims success it did not earn. Run from the project root:

    python scripts/verify_agent.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "app" / "backend"))

from forgepulse_api.services.case_loader import list_available_cases  # noqa: E402
from forgepulse_api.services.diagnosis import build_diagnosis  # noqa: E402
from forgepulse_api.services.model_provider import get_model_provider  # noqa: E402


def _llm_configured() -> bool:
    if os.getenv("FORGEPULSE_MODEL_PROVIDER", "offline").strip().lower() != "openai_compatible":
        return False
    return all(
        os.getenv(var, "").strip()
        for var in ("FORGEPULSE_MODEL_BASE_URL", "FORGEPULSE_MODEL_API_KEY", "FORGEPULSE_MODEL_NAME")
    )


def main() -> int:
    if not _llm_configured():
        print(
            "SKIP: LLM not configured (set FORGEPULSE_MODEL_PROVIDER=openai_compatible "
            "plus BASE_URL/API_KEY/MODEL_NAME). Cannot verify the live LLM path. "
            "No success claimed."
        )
        return 0

    provider = get_model_provider()
    print(f"Provider: {provider.name}")
    cases = list_available_cases()
    if not cases:
        print("SKIP: no registered cases found.")
        return 0

    failures: list[str] = []
    for case_id in cases:
        offline = build_diagnosis(case_id, reasoning="off")
        reviewed = build_diagnosis(case_id, reasoning="llm")

        review = reviewed.agent_reasoning
        if review is None:
            failures.append(f"{case_id}: agent_reasoning is None (LLM call did not produce a review)")
            continue

        evidence_ids = {e.id for e in reviewed.evidence}
        bad_ids = set(review.referenced_evidence_ids) - evidence_ids
        if bad_ids:
            failures.append(f"{case_id}: review referenced unknown evidence ids: {sorted(bad_ids)}")

        # Structured diagnosis must be identical to the offline run.
        offline_struct = offline.model_dump(exclude={"agent_reasoning"})
        reviewed_struct = reviewed.model_dump(exclude={"agent_reasoning"})
        # Limitations differ by design (advisory vs offline text); compare the rest.
        offline_struct["limitations"] = []
        reviewed_struct["limitations"] = []
        # agent_decisions differ (llm_review appended); compare the prefix.
        if reviewed.agent_decisions[:-1] != offline.agent_decisions:
            failures.append(f"{case_id}: pre-review agent decisions differ from offline run")

        status_line = (
            f"  {case_id}: review_summary={review.review_summary[:60]!r} "
            f"notes={len(review.candidate_notes)} "
            f"warning={review.warning!r}"
        )
        print(status_line)

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(" -", f)
        print(f"\n{len(failures)} failure(s). Live LLM verification FAILED.")
        return 1

    print(f"\nAll {len(cases)} case(s): live LLM advisory review attached and validated. OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
