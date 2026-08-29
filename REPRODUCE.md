# Reproduction Guide

Written for someone starting from a completely clean environment.
Total cost: $0. No API key, no billing account, no signup required.

## Fastest path (recommended)
```bash
git clone <your-repo-url>
cd research-claim-verifier
./setup.sh
docker compose run verifier python evaluate.py
```
That's the whole thing. `setup.sh` pulls the model and builds the Docker
images in one step.

## Requirements
- Docker + Docker Compose
- [Ollama](https://ollama.com) installed (free, no account needed) —
  this is what actually runs the model, entirely locally

**If you just installed Ollama and `setup.sh` says `ollama: command not
found`:** this is a real, well-known Windows/PATH quirk, not a bug in this
script. The installer updates your PATH, but any terminal already open
(including one an editor is running inside) was handed a copy of PATH at
the moment it started and won't see the update. Close that terminal, open
a new one, and re-run `./setup.sh`.

## What each command does

### Setup
```bash
./setup.sh
```
Pulls `llama3.2:3b` (~2GB, one-time download — time depends on your
internet connection) and builds the Docker images (~1-2 minutes).
A larger/higher-quality model (`llama3.1:8b`) can be swapped in by
changing `OLLAMA_MODEL` in `docker-compose.yml` — no code changes needed.

### Run the baseline
```bash
docker compose run baseline
```
Expected: a plain verdict per test case, no structured extraction, no
context-audit flag. Runtime measured on CPU (no GPU) for all 10 cases:
~4-6.5 minutes. Meaningfully faster with a GPU.

### Run the full verifier
```bash
docker compose run verifier
```
Expected: for each test case, the extracted atomic claims, then a
structured verdict (SUPPORTED / CONTRADICTED / UNVERIFIABLE) with a
context_audit_flag and source quotes. Runtime measured on CPU for all 10
cases: ~19-23 minutes (two model calls per claim - extraction, then
verify+audit - so this takes noticeably longer than the baseline).

### Run the full evaluation (baseline vs. verifier, all 10 cases)
```bash
docker compose run verifier python evaluate.py
```
Expected: a results table comparing both against the ground truth in
`test_cases/test_case_definitions.md`, saved to `evidence/results.md`.
Runs both of the above back to back, so budget their combined time
(~25-30 minutes on CPU).

## No-Docker fallback
If you'd rather not use Docker at all:
```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
ollama pull llama3.2:3b
python evaluate.py
```

## Versions used
- Python 3.12
- Ollama, model: llama3.2:3b (see requirements.txt for exact pinned
  package versions)
- GPU is used automatically if available (NVIDIA CUDA or Apple Silicon
  Metal); otherwise runs on CPU, just slower.
