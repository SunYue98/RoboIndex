#!/bin/bash
# Pre-commit pipeline. Run after any data change before staging+committing.
#
# Steps:
#   1. Schema validation (must be 0 errors)
#   2. Public API regeneration
#   3. Version stamp bump (dataset_version + snapshot_sha)
#   4. Health report refresh
#   5. Stage standard output paths
#
# Exit non-zero on any failure. The git commit must be done by the caller
# (we don't auto-commit so the caller controls the commit message).

set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> [1/5] Schema validation"
python3 research/_tools/validate_schema.py >/dev/null
echo "    OK"

echo "==> [2/5] Build public API (/api/*.json,csv,md)"
python3 research/_tools/build_api.py | tail -1

echo "==> [3/5] Version stamp"
python3 research/_tools/version_bump.py | tail -5

echo "==> [4/5] Health report refresh"
python3 research/_tools/health_report.py | tail -1

echo "==> [5/5] Stage outputs (excluding raw_images, _health_cache)"
git add public/data/*.json public/api/ research/HEALTH.md 2>/dev/null || true
# Also stage any new synthetic cards if they exist
if [ -d public/images/_synthetic ]; then
  git add public/images/_synthetic/ 2>/dev/null || true
fi

echo
echo "Pre-commit pipeline passed. Run \`git status\` to verify what's staged,"
echo "then \`git commit\` with your message."
