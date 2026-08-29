# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Security: run as non-root user, not root (basic hardening, cheap to add,
# checked by container scanners)
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

# This container calls Ollama running on the HOST machine, not inside this
# image. On Linux hosts, docker-compose.yml adds extra_hosts so
# "host.docker.internal" resolves correctly; on Mac/Windows Docker Desktop
# this works out of the box.

# Default command runs the full evaluation. Override for other entrypoints,
# e.g.: docker run <image> python baseline.py --doc test_cases/case_01.txt
CMD ["python", "evaluate.py"]
