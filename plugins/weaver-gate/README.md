# weaver-gate

**Destructive-op decision-gate. Hornet's pattern, Weaver's domain.**

Inspects every `git` invocation via `PreToolUse(Bash)`. If the command matches a destructive-op pattern (force-push, `filter-branch`, `reset --hard` past pushed tip, `branch -D`, `tag -d`, `clean -fdx`, remote-branch deletion, merge-queue `--admin` bypass), routes through a confirmation surface before allowing it.

No engine — rules-only. Haiku classifies destructive vs safe per the pattern table. Protected-branch force-push: **never** bypassed. `git clean -fdx`: **never** bypassed (irrecoverable — reflog doesn't cover ignored files).

## Install

Part of the [Weaver](../..) bundle. **Installing Weaver without weaver-gate is not supported** — it's the safety floor.

```
/plugin marketplace add enchanted-plugins/weaver
/plugin install full@weaver
```

## Components

| Type | Name | Role |
|------|------|------|
| Hook | PreToolUse(Bash) | Primary inspection point |
| Skill | destructive-gate-confirmation | Decision surface |
| State | audit.jsonl | Append-only, Allay-A4 atomic pattern |

## Cross-plugin

- **Consumes** `reaper.action.dangerous` (blocks Weaver ops when Reaper flags the session).
- **Publishes** `weaver.destructive.detected`, `weaver.destructive.confirmed`, `weaver.destructive.cancelled`.

Full architecture: [../../docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md#destructive-op-confirmation-contract).
