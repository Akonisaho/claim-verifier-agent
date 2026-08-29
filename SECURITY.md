# Security posture

This project's CI gate (`.github/workflows/ci.yml`) runs five checks on
every push and PR. None of them are decorative — each one has caught a
real issue during development (see `trajectories/02-phase2-verifier-and-ci.md`
for the actual investigation). This document explains what each gate
checks and why its thresholds are set the way they are.

## 1. Secret scan — gitleaks
Scans the full git history (`fetch-depth: 0`) for committed credentials.
Since this project uses no paid API and needs no API keys anywhere, the
expected result is always zero findings — any hit here would mean
something genuinely doesn't belong in the repo.

## 2. Lint, SAST & dependency audit
- **ruff** — lint. Zero tolerance; the codebase is small enough that
  there's no excuse for a lingering warning.
- **bandit** (`-ll`, excluding `tests/`) — static analysis for common
  Python security anti-patterns (unsafe deserialization, shell injection,
  weak crypto, etc.). Zero tolerance.
- **pip-audit** — checks every pinned dependency in `requirements.txt`
  against known CVE databases. This one has already caught real,
  actionable issues: the originally-pinned `requests==2.32.3` and
  `pytest==8.3.3` both had disclosed CVEs with fixed versions available,
  found and bumped (`requests==2.33.0`, `pytest==9.0.3`) before this was
  ever a passing check.
- **pytest** — the unit test suite (parsing, roll-up logic, retry
  behavior, file-extraction helpers). No network/Ollama calls in tests -
  those are covered by the real `evaluate.py` runs in `evidence/`.

## 3. Dockerfile lint — hadolint
Standard Dockerfile best-practice checks (no unpinned `apt-get install`
without `update` in the same layer, running as non-root, etc.).

## 4. Container scan — Trivy (vulnerability + license)
Builds the actual image and scans it. Two decisions here are worth
explaining, since both were arrived at by testing real output, not by
assumption:

**`ignore-unfixed: true` on the vulnerability scan.** The base
`python:3.12-slim` image carries a handful of Debian OS-level CVEs
(`perl-base`, `gzip`, `libsqlite3-0`, ...) with no upstream fix released
yet - Trivy reports their status as `affected` or `fix_deferred` with no
fixed version listed. These exist in a stock, freshly-pulled
`python:3.12-slim` too; failing CI on a finding nobody can currently act
on provides no signal, so those are ignored while anything with a real
fix (verified: the Dockerfile runs `apt-get upgrade` specifically so
CVEs that *do* have a fix get picked up) still fails the build.

**`vuln-type: library` on the license scan.** Scanning license
compliance across the *base OS* would fail on any Debian-based image:
system packages like `bash`, `coreutils`, and `tar` are GPL/LGPL-licensed,
which Trivy classifies as "restricted" - a real finding on literally any
Debian container, not something this project introduced or can change.
Scoping the license scan to `library` (our own Python dependencies only)
checks what's actually within this project's control. Verified: with that
scope, the real dependencies (`pydantic`, `requests`, `pytest`, `Flask`,
`pdfplumber`, `python-docx`) come back with **zero** restrictive-license
findings.

**Smoke test.** After both scans pass, the built image is actually run
(`import app; print('image runs OK')`) to catch anything a static scan
can't - e.g. the real `.dockerignore` bug found during development, where
a local Python virtualenv was leaking into the build context via
`COPY . .` and bloating/polluting the image.

## 5. Submission completeness check
Confirms the required submission files (`README.md`, `CHANGELOG.md`,
`REPRODUCE.md`, `Dockerfile`, `requirements.txt`) exist before anything
else is evaluated.

## What's out of scope
This is a local, single-user CLI/tool project with no auth, no
multi-tenant storage, and no network-facing service beyond a
`127.0.0.1`-only local Flask page a user runs themselves - there is no
production deployment surface to threat-model beyond what's already
covered above.
