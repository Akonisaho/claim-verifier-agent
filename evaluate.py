"""Runs baseline.py and app.py on every test case and writes a real
comparison table to evidence/results.md.

Every number in this output comes from an actual Ollama call made during
this run — nothing here is hand-written or estimated.

Usage:
    python evaluate.py
"""
from __future__ import annotations

import datetime
import os
import time
from pathlib import Path

import app as verifier
import baseline

EVIDENCE_DIR = Path(__file__).parent / "evidence"


def run_all() -> tuple[list[dict], list[verifier.DocumentResult], float, float]:
    cases = baseline.load_test_cases()

    print("=" * 70)
    print("Running BASELINE (single prompt, no structure, no context audit)")
    print("=" * 70)
    t0 = time.time()
    baseline_results = [baseline.run_case(c) for c in cases]
    baseline_seconds = time.time() - t0

    print()
    print("=" * 70)
    print("Running VERIFIER (atomic extraction + verify + context audit)")
    print("=" * 70)
    t0 = time.time()
    verifier_results = [verifier.run_case(c) for c in cases]
    verifier_seconds = time.time() - t0

    return baseline_results, verifier_results, baseline_seconds, verifier_seconds


def render_report(
    baseline_results: list[dict],
    verifier_results: list[verifier.DocumentResult],
    baseline_seconds: float,
    verifier_seconds: float,
) -> str:
    lines = []
    lines.append("# Evaluation results")
    lines.append("")
    lines.append(
        f"Generated {datetime.datetime.now(datetime.timezone.utc).isoformat()} "
        f"by running `evaluate.py` against model `{os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')}` "
        f"via Ollama at `{os.environ.get('OLLAMA_HOST', 'http://localhost:11434')}`. "
        "Every value below is real output from that run — nothing is hand-written."
    )
    lines.append("")

    lines.append("## Per-case comparison")
    lines.append("")
    lines.append(
        "| Case | Ground truth (verdict / audit) | Baseline verdict | Baseline match | "
        "Verifier verdict / audit | Verifier match (verdict / audit) |"
    )
    lines.append("|---|---|---|---|---|---|")
    for b, v in zip(baseline_results, verifier_results):
        gt_v, gt_a = v.ground_truth_verdict, v.ground_truth_audit_flag
        b_match = "✅" if b["verdict"] == gt_v else "❌"
        v_verdict_match = "✅" if v.verdict == gt_v else "❌"
        v_audit_match = "✅" if v.context_audit_flag == gt_a else "❌"
        lines.append(
            f"| {v.id}: {v.title} | {gt_v} / {gt_a} | {b['verdict']} | {b_match} | "
            f"{v.verdict} / {v.context_audit_flag} | {v_verdict_match} / {v_audit_match} |"
        )
    lines.append("")

    n = len(verifier_results)
    baseline_correct = sum(1 for b in baseline_results if b["verdict"] == b["ground_truth_verdict"])
    verifier_verdict_correct = sum(1 for v in verifier_results if v.verdict == v.ground_truth_verdict)
    verifier_audit_correct = sum(
        1 for v in verifier_results if v.context_audit_flag == v.ground_truth_audit_flag
    )
    verifier_both_correct = sum(
        1 for v in verifier_results
        if v.verdict == v.ground_truth_verdict
        and v.context_audit_flag == v.ground_truth_audit_flag
    )

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Test cases: {n}")
    lines.append(f"- Baseline verdict accuracy: {baseline_correct}/{n} ({baseline_seconds:.1f}s total)")
    lines.append(f"- Verifier verdict accuracy: {verifier_verdict_correct}/{n} ({verifier_seconds:.1f}s total)")
    lines.append(f"- Verifier context-audit-flag accuracy: {verifier_audit_correct}/{n}")
    lines.append(f"- Verifier fully correct (verdict AND audit flag): {verifier_both_correct}/{n}")
    lines.append("")

    # Case 2 is the key differentiator case per test_case_definitions.md
    case2_baseline = next((b for b in baseline_results if b["id"] == "case_02"), None)
    case2_verifier = next((v for v in verifier_results if v.id == "case_02"), None)
    if case2_baseline and case2_verifier:
        lines.append("## Key differentiator case (case_02: deceptive context)")
        lines.append("")
        lines.append(f"- Baseline verdict: {case2_baseline['verdict']} "
                      f"(baseline has no context-audit mechanism at all)")
        lines.append(f"- Verifier verdict: {case2_verifier.verdict}, "
                      f"context_audit_flag: {case2_verifier.context_audit_flag}")
        lines.append("- Ground truth: SUPPORTED, context_audit_flag: True")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    EVIDENCE_DIR.mkdir(exist_ok=True)
    baseline_results, verifier_results, baseline_seconds, verifier_seconds = run_all()
    report = render_report(baseline_results, verifier_results, baseline_seconds, verifier_seconds)

    out_path = EVIDENCE_DIR / "results.md"
    out_path.write_text(report, encoding="utf-8")
    print()
    print(report)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
