# Project Rules for Claude Code — Claim Verifier

Binding for every session. Follow without being asked again.

## 1. Language, environment & architecture constraints
- Python 3.12 only.
- All dependencies pinned to exact versions in requirements.txt.
- No RAG frameworks, vector databases, or agent-orchestration libraries
  (no LangChain, LangGraph, LlamaIndex, Chroma, Pinecone, etc.). Source
  material is passed in directly per test case. Keep the pipeline
  transparent: two steps (extract, then verify+audit), both structured
  with Pydantic, nothing more.
- The LLM runtime is a local, free, open-weight model served via Ollama
  (llama3.2:3b by default), called over plain HTTP with the `requests`
  library — never a paid API. Claude Code is the coding agent used to
  build this project; that is separate from what the pipeline calls at
  runtime.
- Do NOT build a web UI, admin panel, or multi-tenant storage until
  Phase 4 explicitly calls for a simple single-page frontend. No
  multi-tenancy, ever — out of scope.

## 2. Non-negotiables (hackathon compliance)
- Never commit real credentials — none should be needed anywhere in this
  project, since it uses no paid API.
- Every consequential action stays sandboxed; this system only ever
  produces a report for a human editor — it never publishes or acts.
- Disclose Claude Code as the agent used via README.md's "AI Agent
  Disclosure" section and exported trajectories in trajectories/. This
  satisfies the hackathon's disclosure requirement.
- **Git commit authorship stays solely Akonisaho — never add a
  `Co-Authored-By: Claude` trailer or any other co-author line to commits.**
  Tool disclosure lives in README.md and trajectories/, not in commit
  metadata. Every commit must be authored and committed as Akonisaho only.
- Use only public or synthetic data for test cases.
- Never fabricate results. Every number in CHANGELOG.md, README.md, or
  evidence/ must come from an actual run of evaluate.py. If a real number
  isn't available yet, leave it as [TODO] — never a placeholder that looks
  like a real result.

## 3. Structure to respect
```
app.py              # core pipeline: atomic extraction, then verify+context-audit
baseline.py          # single-prompt baseline, no structure, no audit
evaluate.py          # runs both on all test cases, produces results table
web/                 # Phase 4 only: simple local Flask page over app.py/baseline.py
test_cases/          # synthetic documents + sources + ground-truth verdicts
evidence/            # real output of evaluate.py runs — never hand-edited
trajectories/        # exported Claude Code session logs
tests/               # pytest unit tests
Dockerfile, docker-compose.yml, requirements.txt, setup.sh
README.md, CHANGELOG.md, REPRODUCE.md
```

## 4. Git workflow (follow exactly, this is not optional)
- `main` must always be in a working, CI-passing state.
- Each phase below happens on its own branch, named exactly as listed.
- After finishing a phase: run all CI checks locally if possible (ruff,
  bandit, pytest at minimum), show me the real output, wait for my
  explicit confirmation, THEN open a PR and merge to main.
- Never merge a phase with invented/placeholder results presented as real.
- Never start the next phase's branch before the current one is merged.

### Phases
1. `phase-1-baseline` — write the 10 test cases as real data; build
   baseline.py; run it for real on all cases; record actual output.
2. `phase-2-verifier` — build app.py (atomic extraction + verify+audit via
   Ollama) and evaluate.py (runs both, produces comparison table, writes
   evidence/results.md). Run for real.
3. `phase-3-hardening` — add pytest unit tests, error handling/retries
   around Ollama calls, and perform a genuine clean-environment
   reproduction test of REPRODUCE.md (simulate a fresh clone and follow
   the instructions exactly). Fix anything that breaks.
4. `phase-4-frontend` — a simple local Flask page (paste document + source,
   buttons for baseline vs verifier, side-by-side results). Thin wrapper
   only — no new pipeline logic here.
5. `phase-5-docs` — fill CHANGELOG.md with real numbers, write the
   failure-mode/hot-take section based on what the hard case (Case 9)
   actually revealed, finalize README, export trajectories.
6. `phase-6-final` — final full clean-environment run to confirm main
   still works exactly as documented before submission.

## 5. CI gate awareness
CI (.github/workflows/ci.yml) runs: gitleaks (secrets), ruff (lint),
bandit (SAST), pip-audit (dependency vulns), pytest (tests), hadolint
(Dockerfile lint), Trivy (image vulnerability + license scan), and a
submission completeness check. Check work against these mentally before
declaring any phase done.

## 6. Communication style
- After finishing a chunk of work, summarize what changed, what you
  tested, and what's still unverified.
- Flag uncertainty explicitly — this is judged work, not a demo.
