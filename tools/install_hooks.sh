#!/bin/sh
# installs the no-drift hooks (HANDOFF.md). Run once after cloning.
#
# The pre-commit hook is a WRAPPER, not a copy of check_plan.py. Copying the .py in relies on its
# `#!/usr/bin/env python3` shebang, and on Windows that resolves to the Microsoft Store stub --
# "Python was not found" -- so the hook fails open-ish: git reports the commit refused and the
# check never ran. Found 2026-10-24 by this script overwriting a working wrapper with the raw
# file. The wrapper finds whichever interpreter this machine actually has.
cd "$(dirname "$0")/.." || exit 1

cat > .git/hooks/pre-commit <<'HOOK'
#!/bin/sh
# no-drift check -- see tools/check_plan.py. A wrapper, because a python3 shebang does not
# resolve on Windows (Microsoft Store stub) and the check would silently never run.
root=$(git rev-parse --show-toplevel)
for py in python3 python py; do
	if command -v "$py" >/dev/null 2>&1 && "$py" -c '' >/dev/null 2>&1; then
		exec "$py" "$root/tools/check_plan.py"
	fi
done
echo 'pre-commit: no working python found (tried python3, python, py) -- check_plan.py did NOT run'
exit 1
HOOK

cp tools/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/pre-commit .git/hooks/commit-msg
echo hooks installed
