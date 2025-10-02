#!/usr/bin/env bash
set -euo pipefail
BASE_REF="${GITHUB_BASE_REF:-origin/main}"
CHANGED=$(git diff --name-only "$BASE_REF"...HEAD || true)
fail=0
if echo "$CHANGED" | grep -E '^(api|backend|server|web|frontend|src|app|services|package.json|pyproject.toml|requirements.txt|Dockerfile|docker-compose.yml|Makefile|Taskfile.yml)' >/dev/null; then
  echo "::notice::Code changed — ensure _meta/TASKS.md updated."
  if ! echo "$CHANGED" | grep -q '^_meta/TASKS.md'; then
    echo "::error file=_meta/TASKS.md::Update _meta/TASKS.md to reflect changes."
    fail=1
  fi
fi
if echo "$CHANGED" | grep -E '^(Dockerfile|docker-compose.yml|Makefile|Taskfile.yml|\.github/workflows/|scripts/|pyproject.toml|package.json|requirements.txt)' >/dev/null; then
  if ! echo "$CHANGED" | grep -q '^_meta/DECISIONS.md'; then
    echo "::error file=_meta/DECISIONS.md::Record ADR for config/build/CI changes."
    fail=1
  fi
fi
exit $fail
