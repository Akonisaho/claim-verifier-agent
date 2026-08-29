#!/usr/bin/env bash
set -e

if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: 'ollama' isn't on PATH." >&2
  echo "If you just installed Ollama, this is expected - the installer" >&2
  echo "updates PATH, but any terminal already open (including this one," >&2
  echo "or an editor's integrated terminal) started before the install" >&2
  echo "won't see the change until it's closed and reopened." >&2
  echo "Close this terminal, open a new one, and re-run ./setup.sh." >&2
  exit 1
fi

echo "Pulling the model (one-time, a couple GB)..."
ollama pull llama3.2:3b
echo "Building Docker images..."
docker compose build
echo "Setup complete. Run: docker compose run baseline    or    docker compose run verifier"
