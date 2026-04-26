#!/usr/bin/env bash
# One-shot Entire bootstrap.  No API key required.
#
# Run from the repo root:   bash scripts/setup_entire.sh
#
# This installs the CLI (idempotent), enables Entire on this repo, and
# captures the first dispatch summary.  Re-run after every major commit
# (or wire it into your post-commit hook) so reasoning traces stay current.

set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v entire >/dev/null 2>&1; then
  echo "→ Installing Entire CLI…"
  curl -fsSL https://entire.io/install.sh | bash
  export PATH="$HOME/.entire/bin:$PATH"
fi

echo "→ entire enable in $(pwd)"
entire enable || {
  echo "If this errored with 'already enabled', that's fine — proceeding."
}

DISPATCH_DIR="docs/entire-dispatches"
mkdir -p "$DISPATCH_DIR"
DATE_STAMP="$(date +%Y-%m-%d)"
DISPATCH_FILE="$DISPATCH_DIR/$DATE_STAMP.md"

echo "→ entire dispatch --local --since 24h  (capturing into $DISPATCH_FILE)"
# --local uses the locally-installed agent CLI (Claude Code / Cursor /
# Codex) instead of the Entire server — works without an Entire login.
# --since 24h scopes the window.  Output is committed under
# docs/entire-dispatches/ so judges can `git clone` and read the
# build journal directly (see README's '## Build journal' section).
if entire dispatch --local --since 24h > "$DISPATCH_FILE.tmp" 2>&1; then
  mv "$DISPATCH_FILE.tmp" "$DISPATCH_FILE"
  echo "  → wrote $DISPATCH_FILE"
  echo
  echo "  Commit it next:"
  echo "      git add $DISPATCH_FILE && git commit -m 'entire: dispatch $DATE_STAMP'"
else
  rm -f "$DISPATCH_FILE.tmp"
  echo "  Note: 'entire dispatch --local' may need a fresh commit since the"
  echo "  last dispatch.  Try after your next commit."
fi

echo
echo "Done.  Build journal lives at $DISPATCH_DIR/ — see README '## Build journal'."
