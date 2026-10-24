#!/bin/sh
# installs the no-drift hooks (HANDOFF.md). Run once after cloning.
cd "$(dirname "$0")/.." && cp tools/check_plan.py .git/hooks/pre-commit && cp tools/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/pre-commit .git/hooks/commit-msg && echo hooks installed
