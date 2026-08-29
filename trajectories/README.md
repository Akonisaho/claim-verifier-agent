# Agent trajectories

This directory documents representative excerpts from the actual Claude
Code sessions used to build this project, as required by the hackathon's
coding-agent disclosure rules. Every quoted instruction, action, and tool
result below is real - copied from the session transcript, not
reconstructed or paraphrased from memory afterward.

## Why curated excerpts, not a raw log dump

The full session transcripts are long (spanning environment setup,
multiple real Ollama runs, CI debugging, and back-and-forth with the
human). Rather than hand over an unfiltered wall of text, each file here
walks through one phase of the work in the same shape every time:

**Instruction given → Action taken → Tool response → What it revealed /
changed next.**

That structure is what actually matters for review: what the agent was
asked to do, what it did, what the tools told it, and - critically - the
retries, dead ends, and human checkpoints along the way. A judge should be
able to follow the reasoning without replaying the whole session.

## Files

| File | Covers |
|---|---|
| [01-phase1-baseline.md](01-phase1-baseline.md) | Repo discovery, git/GitHub setup, Ollama install, real baseline run |
| [02-phase2-verifier-and-ci.md](02-phase2-verifier-and-ci.md) | Building app.py, finding and fixing the extraction bug and the non-determinism bug, then the Docker/Trivy CI investigation |
| [03-phase3-hardening.md](03-phase3-hardening.md) | Retry test coverage, the `.venv312` Docker leak, real docker-compose reproduction |

## How this maps to the rest of the submission

- Every real number these sessions produced is in `CHANGELOG.md` and
  `evidence/results*.md` - nothing here introduces a new claim, it just
  shows the work that produced those files.
- Human checkpoints (approvals, corrections, redirection) are called out
  explicitly wherever they happened, not smoothed over.
