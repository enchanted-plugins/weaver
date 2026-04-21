"""Hook-local thin adapter: stdin JSON -> atomic_state.{append_jsonl,write_state}.

Hook scripts can't cleanly do `python - <<EOF` + stdin-pipe on the same
invocation (the heredoc steals stdin). They also can't rely on the bash
``atomic_append`` path because Cygwin/Git-Bash's ``flock`` trips on the
fd-form inherited into the subshell. So each hook invokes this helper:

    printf '%s' "$record" | python _hook_state.py append <path>
    printf '%s' "$json"   | python _hook_state.py write  <path>

Stdlib only. Re-uses the canonical primitives from ``atomic_state``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Resolve the sibling atomic_state without caring about cwd.
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))

from atomic_state import append_jsonl, write_state  # noqa: E402


def _main() -> int:
    if len(sys.argv) < 3:
        print(
            json.dumps({"error": "usage: _hook_state.py (append|write) <path>"}),
            file=sys.stderr,
        )
        return 2

    action = sys.argv[1]
    target = sys.argv[2]
    raw = sys.stdin.read().strip()

    if not raw:
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"invalid JSON on stdin: {exc}"}), file=sys.stderr)
        return 3

    if action == "append":
        append_jsonl(target, payload)
        return 0
    if action == "write":
        write_state(target, payload)
        return 0

    print(json.dumps({"error": f"unknown action: {action}"}), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(_main())
