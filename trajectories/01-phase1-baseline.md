# Trajectory: Phase 1 — baseline, environment setup, real first run

## Instruction given
The user pointed Claude Code at an empty-looking project folder
(`research-claim-verifier`) that already contained planning docs
(`README.md`, `CLAUDE.md`, `kickoff_prompt.md`, `test_case_definitions.md`,
`Dockerfile`, `docker-compose.yml`, CI config) but zero actual code, and
asked what had been done so far.

## Action taken
Read every planning doc in full before writing anything, per
`kickoff_prompt.md`'s own explicit instruction ("Read README.md, CLAUDE.md,
and test_cases/test_case_definitions.md fully before writing any code").
Confirmed via `git config` that the user's author identity was already set
correctly (`Takalani Akonisaho <...@users.noreply.github.com>`), matching
CLAUDE.md's non-negotiable rule that commits are never co-authored by
Claude.

## Tool response
`ls`/`find` showed only docs and config - no `app.py`, `baseline.py`,
`evaluate.py`, `test_cases/*.json`, `tests/`, `evidence/`, or `trajectories/`
existed yet, and there was no git repo at all (`git init` had never been
run).

## What it revealed / changed next
Reported this plainly rather than assuming progress existed: "you have a
very well-specified plan and zero working code." Also checked the runtime
environment directly rather than assuming it was ready:
- `ollama` - not installed
- Python - only 3.14 present locally (project pins 3.12)
- Docker - installed but daemon not running

This produced a genuine decision point, put to the user rather than
silently worked around:

> "Ollama isn't installed on this machine and Python is 3.14 (project
> pins 3.12). How do you want to proceed to get real, run-for-real
> numbers before the deadline?"

The user chose to install Ollama themselves and to follow CLAUDE.md's
phased branch workflow starting at Phase 1, rather than skip the ceremony.

## Human checkpoint: existing repo + authorship
Mid-way through initializing git, the user interrupted with a correction:

> "here is the repo already so lways give me a pushi will push unles youcan
> push and voiad the authr as claude butme"

i.e.: a GitHub repo already existed at a specific URL, and commits must
never be authored as Claude. Action taken: added the existing remote,
verified the first push's commit author was `Takalani Akonisaho` (not
Claude) before treating this as resolved, and confirmed going forward that
Claude would push directly using the already-cached credentials rather than
asking the user to push manually every time.

## Real run
Wrote the 10 test cases as real JSON files (not just the markdown
description), built `baseline.py` (single-prompt, no decomposition, no
context audit), and ran it for real against `llama3.2:3b` once Ollama and
the model were installed:

```
--- case_01: Flipped statistic ---
  verdict:       CONTRADICTED  (MATCH vs ground truth CONTRADICTED)
--- case_02: Deceptive context (the key case) ---
  verdict:       CONTRADICTED  (MISMATCH vs ground truth SUPPORTED)
...
Baseline accuracy: 6/10 verdicts matched ground truth
```

The mismatches were exactly the deceptive-context cases (2, 6, 7) plus the
fabricated-citation edge case (3) - i.e. the baseline failed precisely on
the failure mode this project exists to catch. This became the first real
data point in `CHANGELOG.md`, reported to the user without rounding up or
cherry-picking ("6/10 ... exactly the failure mode this project targets").
