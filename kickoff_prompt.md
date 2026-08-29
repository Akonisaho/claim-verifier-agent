# Claude Code kickoff prompt — Claim Verifier

Read README.md, CLAUDE.md, and test_cases/test_case_definitions.md fully
before writing any code. Follow every rule in CLAUDE.md — especially:
no RAG/vector DB/orchestration frameworks, local Ollama only (no paid
API, I have no budget for one), never fabricate a result number, and
follow the exact phased git branch workflow in CLAUDE.md section 4.

I have Ollama installed and will run `ollama pull llama3.2:3b` myself.

Before writing any code, confirm my git config is set to author = Akonisaho
only, and do not add a Co-Authored-By or any other co-author trailer to
any commit message, ever — tool disclosure belongs in README.md and
trajectories/, not in commit metadata.

Work through the phases in CLAUDE.md one at a time, in order:

- Phase 1: baseline, on branch phase-1-baseline
- Phase 2: verifier + evaluation, on branch phase-2-verifier
- Phase 3: hardening + real reproducibility test, on branch phase-3-hardening
- Phase 4: simple frontend, on branch phase-4-frontend
- Phase 5: docs/changelog/trajectories, on branch phase-5-docs
- Phase 6: final audit, on branch phase-6-final

After each phase, STOP and show me the real output (actual command
results, not a description of what should happen). Wait for my explicit
"looks good, merge it" before opening a PR and merging to main. Do not
start the next phase's branch until the current one is merged.

Begin with Phase 1 now.
