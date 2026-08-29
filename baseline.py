"""Baseline: a single direct prompt, no structural decomposition, no context audit.

"Fact-check this document against this source material" — the whole claim
and the whole source go into one prompt, and the model returns one verdict.
This is what a naive AI fact-checker looks like. It exists so
`evaluate.py` has something to compare `app.py` against.

Usage:
    python baseline.py --all
    python baseline.py --case test_cases/case_02.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from pydantic import BaseModel, ValidationError

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
TEST_CASES_DIR = Path(__file__).parent / "test_cases"

VALID_VERDICTS = {"SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"}


class BaselineVerdict(BaseModel):
    verdict: str
    reasoning: str


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
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
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


def build_prompt(claim: str, source: str) -> str:
    return f"""You are fact-checking a claim from a corporate document against source material.

CLAIM:
{claim}

SOURCE MATERIAL:
{source}

Fact-check the claim against the source material. Respond with EXACTLY this format,
nothing else:

VERDICT: <SUPPORTED, CONTRADICTED, or UNVERIFIABLE>
REASONING: <one or two sentences explaining your verdict>
"""


def parse_response(text: str) -> BaselineVerdict:
    verdict = "UNVERIFIABLE"
    reasoning = text.strip()
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("VERDICT:"):
            candidate = line.split(":", 1)[1].strip().upper()
            for v in VALID_VERDICTS:
                if v in candidate:
                    verdict = v
                    break
        elif line.upper().startswith("REASONING:"):
            reasoning = line.split(":", 1)[1].strip()
    return BaselineVerdict(verdict=verdict, reasoning=reasoning)


def run_case(case: dict) -> dict:
    prompt = build_prompt(case["claim"], case["source"])
    raw = call_ollama(prompt)
    try:
        parsed = parse_response(raw)
    except ValidationError as exc:
        parsed = BaselineVerdict(verdict="UNVERIFIABLE", reasoning=f"parse error: {exc}")
    return {
        "id": case["id"],
        "title": case["title"],
        "verdict": parsed.verdict,
        "reasoning": parsed.reasoning,
        "ground_truth_verdict": case["ground_truth_verdict"],
    }


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
        match = "MATCH" if result["verdict"] == result["ground_truth_verdict"] else "MISMATCH"
        print(f"  verdict:       {result['verdict']}  ({match} vs ground truth "
              f"{result['ground_truth_verdict']})")
        print(f"  reasoning:     {result['reasoning']}")

    correct = sum(1 for r in results if r["verdict"] == r["ground_truth_verdict"])
    print(f"\nBaseline accuracy: {correct}/{len(results)} verdicts matched ground truth")


if __name__ == "__main__":
    main()
