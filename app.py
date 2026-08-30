"""The verifier: atomic claim extraction, then per-claim verify + context audit.

Two plain HTTP calls to a local Ollama model, both structured with Pydantic:

1. Extraction  — break the input document into individual, standalone
   factual claims instead of judging the whole document as one blob.
2. Verification — for each atomic claim, return a verdict (SUPPORTED /
   CONTRADICTED / UNVERIFIABLE) AND a separate, independently-decided
   context_audit_flag that catches claims where the number is correct but
   the surrounding context (test conditions, time period, population) has
   been altered or dropped.

Document-level result is then rolled up from the per-claim verdicts:
  - any claim CONTRADICTED  -> document CONTRADICTED
  - else any claim UNVERIFIABLE -> document UNVERIFIABLE
  - else -> document SUPPORTED
  - context_audit_flag = True if ANY claim's audit flag is True

No RAG framework, vector database, or agent-orchestration library — source
material is provided directly per case.

Usage:
    python app.py --all
    python app.py --case test_cases/case_02.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from pydantic import BaseModel, Field, ValidationError

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
TEST_CASES_DIR = Path(__file__).parent / "test_cases"

VALID_VERDICTS = {"SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"}


class AtomicClaim(BaseModel):
    text: str


class ClaimVerdict(BaseModel):
    claim: str
    verdict: str
    context_audit_flag: bool
    source_quote: str
    reasoning: str


class DocumentResult(BaseModel):
    id: str
    title: str
    claims: list[ClaimVerdict]
    verdict: str = Field(..., description="rolled-up document-level verdict")
    context_audit_flag: bool = Field(..., description="True if any claim was flagged")
    ground_truth_verdict: str
    ground_truth_audit_flag: bool


def load_test_cases(directory: Path = TEST_CASES_DIR) -> list[dict]:
    cases = []
    for path in sorted(directory.glob("case_*.json")):
        with open(path, encoding="utf-8") as f:
            cases.append(json.load(f))
    return cases


def call_ollama(prompt: str, retries: int = 3, timeout: int = 120) -> str:
    """Plain HTTP call to a local Ollama server. Retries on transient failures."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    # temperature 0 (+ fixed seed): verdicts must be
                    # reproducible run-to-run, not just plausible-sounding.
                    # num_predict: bounds how long a single call can run -
                    # without it, a rambling completion has no hard stop.
                    "options": {"temperature": 0, "seed": 42, "num_predict": 250},
                    # keep the model loaded between calls - reloading it
                    # from disk (measured: ~11s) otherwise repeats on every
                    # single request once Ollama's default idle timeout
                    # unloads it.
                    "keep_alive": "30m",
                },
                timeout=timeout,
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except (requests.RequestException, KeyError) as exc:
            last_error = exc
            if attempt < retries:
                continue
    raise RuntimeError(
        f"Ollama call failed after {retries} attempts "
        f"(host={OLLAMA_HOST}, model={OLLAMA_MODEL}): {last_error}"
    ) from last_error


# --- Step 1: atomic extraction ---------------------------------------------

def build_extraction_prompt(claim: str) -> str:
    return f"""Break the following statement into individual, standalone factual
claims. Each atomic claim must be a complete, checkable statement of fact
(a number with what it measures, a full quote with who said it, a
historical fact) — never a single word or sentence fragment, and never a
generic claim about something merely existing (e.g. never output something
like "the document exists" or "the CEO is a real person" — those are not
checkable facts).

If the statement only contains ONE fact, return just that one claim
unchanged. Only split into multiple claims when the statement genuinely
asserts two or more separate, independently-checkable facts (for example, a
sentence that reports two different metrics joined by "and").

Examples:

STATEMENT:
Revenue grew 15% and headcount decreased by 10% this year, showing improved efficiency.
CLAIM: Revenue grew 15% this year.
CLAIM: Headcount decreased by 10% this year.

STATEMENT:
The document quotes the CEO as saying "our top priority remains customer trust."
CLAIM: The CEO is quoted as saying "our top priority remains customer trust."

STATEMENT:
94% of our customers are satisfied with the product.
CLAIM: 94% of our customers are satisfied with the product.

Now do the same for this statement:

STATEMENT:
{claim}

Respond with EXACTLY this format, one claim per line, nothing else:

CLAIM: <atomic claim text>
CLAIM: <atomic claim text>
(as many CLAIM: lines as needed)
"""


MIN_CLAIM_WORDS = 3  # defensive guard: a real atomic claim is a full statement,
                      # never a lone word or stopword fragment.


def parse_claims(text: str, fallback: str) -> list[AtomicClaim]:
    claims = []
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("CLAIM:"):
            content = line.split(":", 1)[1].strip()
            # Guard against small-model fragmentation (e.g. splitting a
            # statement word-by-word) — a real atomic claim is a full
            # statement of fact, not a lone word.
            if content and len(content.split()) >= MIN_CLAIM_WORDS:
                claims.append(AtomicClaim(text=content))
    if not claims:
        claims = [AtomicClaim(text=fallback)]
    return claims


def extract_claims(document_claim: str) -> list[AtomicClaim]:
    raw = call_ollama(build_extraction_prompt(document_claim))
    return parse_claims(raw, fallback=document_claim)


# --- Step 2: verify + context audit ----------------------------------------

def build_verify_prompt(claim: str, source: str) -> str:
    return f"""You are fact-checking ONE atomic claim from a corporate document
against source material. Do two things, independently:

1. Decide a VERDICT: is the claim SUPPORTED, CONTRADICTED, or UNVERIFIABLE
   against the source material?
2. Decide a CONTEXT_AUDIT, separately from the verdict: even if the number
   or fact itself is correct, has the surrounding context been altered or
   dropped in a way that changes the meaning? Examples: a number that's
   real but was measured under different conditions (e.g. a sandbox/test
   environment vs. real production), over a different time period (e.g.
   trailing twelve months vs. a single quarter), or for a different
   population (e.g. only survey respondents vs. all customers) than the
   claim implies. Answer YES to CONTEXT_AUDIT only if the claim's framing
   would mislead a reasonable reader about what the source actually shows.

CLAIM:
{claim}

SOURCE MATERIAL:
{source}

Respond with EXACTLY this format, nothing else:

VERDICT: <SUPPORTED, CONTRADICTED, or UNVERIFIABLE>
CONTEXT_AUDIT: <YES or NO>
SOURCE_QUOTE: <the exact portion of the source material this is based on>
REASONING: <one or two sentences explaining both decisions>
"""


def parse_verdict(text: str, claim: str) -> ClaimVerdict:
    verdict = "UNVERIFIABLE"
    audit_flag = False
    source_quote = ""
    reasoning = text.strip()
    for line in text.splitlines():
        line = line.strip()
        upper = line.upper()
        if upper.startswith("VERDICT:"):
            candidate = line.split(":", 1)[1].strip().upper()
            for v in VALID_VERDICTS:
                if v in candidate:
                    verdict = v
                    break
        elif upper.startswith("CONTEXT_AUDIT:"):
            audit_flag = "YES" in line.split(":", 1)[1].strip().upper()
        elif upper.startswith("SOURCE_QUOTE:"):
            source_quote = line.split(":", 1)[1].strip()
        elif upper.startswith("REASONING:"):
            reasoning = line.split(":", 1)[1].strip()
    return ClaimVerdict(
        claim=claim,
        verdict=verdict,
        context_audit_flag=audit_flag,
        source_quote=source_quote,
        reasoning=reasoning,
    )


def verify_claim(claim: str, source: str) -> ClaimVerdict:
    raw = call_ollama(build_verify_prompt(claim, source))
    try:
        return parse_verdict(raw, claim)
    except ValidationError as exc:
        return ClaimVerdict(
            claim=claim, verdict="UNVERIFIABLE", context_audit_flag=False,
            source_quote="", reasoning=f"parse error: {exc}",
        )


# --- Roll-up + orchestration ------------------------------------------------

def rollup(claims: list[ClaimVerdict]) -> tuple[str, bool]:
    verdicts = {c.verdict for c in claims}
    if "CONTRADICTED" in verdicts:
        verdict = "CONTRADICTED"
    elif "UNVERIFIABLE" in verdicts:
        verdict = "UNVERIFIABLE"
    else:
        verdict = "SUPPORTED"
    audit_flag = any(c.context_audit_flag for c in claims)
    return verdict, audit_flag


def run_case(case: dict) -> DocumentResult:
    atomic_claims = extract_claims(case["claim"])
    claim_verdicts = [verify_claim(c.text, case["source"]) for c in atomic_claims]
    verdict, audit_flag = rollup(claim_verdicts)
    return DocumentResult(
        id=case["id"],
        title=case["title"],
        claims=claim_verdicts,
        verdict=verdict,
        context_audit_flag=audit_flag,
        ground_truth_verdict=case["ground_truth_verdict"],
        ground_truth_audit_flag=case["ground_truth_audit_flag"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="run every test case")
    parser.add_argument("--case", type=str, help="path to a single test case JSON file")
    args = parser.parse_args()

    if args.case:
        with open(args.case, encoding="utf-8") as f:
            cases = [json.load(f)]
    else:
        cases = load_test_cases()
        if not cases:
            print("No test cases found in test_cases/", file=sys.stderr)
            sys.exit(1)

    results = []
    for case in cases:
        print(f"--- {case['id']}: {case['title']} ---")
        result = run_case(case)
        results.append(result)
        for cv in result.claims:
            print(f"  claim:         {cv.claim}")
            print(f"    verdict:       {cv.verdict}  audit_flag={cv.context_audit_flag}")
            print(f"    source_quote:  {cv.source_quote}")
            print(f"    reasoning:     {cv.reasoning}")
        v_match = "MATCH" if result.verdict == result.ground_truth_verdict else "MISMATCH"
        a_match = "MATCH" if result.context_audit_flag == result.ground_truth_audit_flag else "MISMATCH"
        print(f"  DOCUMENT verdict:    {result.verdict}  ({v_match} vs ground truth "
              f"{result.ground_truth_verdict})")
        print(f"  DOCUMENT audit_flag: {result.context_audit_flag}  ({a_match} vs ground truth "
              f"{result.ground_truth_audit_flag})")

    verdict_correct = sum(1 for r in results if r.verdict == r.ground_truth_verdict)
    audit_correct = sum(1 for r in results if r.context_audit_flag == r.ground_truth_audit_flag)
    both_correct = sum(
        1 for r in results
        if r.verdict == r.ground_truth_verdict
        and r.context_audit_flag == r.ground_truth_audit_flag
    )
    print(f"\nVerifier verdict accuracy:    {verdict_correct}/{len(results)}")
    print(f"Verifier audit-flag accuracy: {audit_correct}/{len(results)}")
    print(f"Verifier fully-correct:       {both_correct}/{len(results)}")


if __name__ == "__main__":
    main()
