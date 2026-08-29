#!/usr/bin/env bash
set -e
echo "Pulling the model (one-time, a couple GB)..."
ollama pull llama3.2:3b
echo "Building Docker images..."
docker compose build
echo "Setup complete. Run: docker compose run baseline    or    docker compose run verifier"
