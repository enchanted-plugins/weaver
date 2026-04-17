#!/usr/bin/env bash
# Weaver installer. The 8 plugins coordinate through the mcp-event-bus;
# the `full` meta-plugin pulls them all in via one dependency-resolution pass.
set -euo pipefail

REPO="https://github.com/enchanted-plugins/weaver"
WEAVER_DIR="${HOME}/.claude/plugins/weaver"

step() { printf "\n\033[1;36m▸ %s\033[0m\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }

step "Weaver installer"

# 1. Clone the monorepo so shared/scripts/*.py are available locally.
#    Plugins themselves are served via the marketplace command below.
if [[ -d "$WEAVER_DIR/.git" ]]; then
  git -C "$WEAVER_DIR" pull --ff-only --quiet
  ok "Updated existing clone at $WEAVER_DIR"
else
  git clone --depth 1 --quiet "$REPO" "$WEAVER_DIR"
  ok "Cloned to $WEAVER_DIR"
fi

# 2. Pre-flight git credential-manager check — Weaver's auth layer depends on it.
if ! command -v git >/dev/null 2>&1; then
  echo "  \033[33m!\033[0m git not found on PATH — Weaver requires git" >&2
  exit 1
fi
ok "git present"

if git credential-manager --version >/dev/null 2>&1; then
  ok "git-credential-manager detected"
elif command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  ok "gh auth detected (fast-path for GitHub)"
else
  echo "  \033[33m!\033[0m No credential helper detected. Install git-credential-manager or run 'gh auth login' before using /weaver push." >&2
fi

cat <<'EOF'

─────────────────────────────────────────────────────────────────────────
  Weaver ships as an 8-plugin ecosystem. Each plugin owns one named
  engine (W1–W5) or one orthogonal concern (capability-memory, ci-reader,
  weaver-gate). The `full` meta-plugin lists all eight as dependencies
  so one install pulls in the whole chain.
─────────────────────────────────────────────────────────────────────────

  Finish in Claude Code with TWO commands:

    /plugin marketplace add enchanted-plugins/weaver
    /plugin install full@weaver

  That installs all 8 plugins via dependency resolution. To cherry-pick
  a single plugin instead, use e.g. `/plugin install commit-intelligence@weaver`.

  Verify with:   /plugin list
  Expected:      full + 8 plugins installed under the weaver marketplace.

  Once installed, Weaver auto-orchestrates on PostToolUse(Edit|Write):
  task boundaries become branches, each boundary becomes a signed
  Conventional Commit, and a draft PR opens when the cluster closes.
  Destructive ops always route through the decision-gate.

EOF
