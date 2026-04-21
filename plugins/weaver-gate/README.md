# weaver-gate

**Destructive-op decision-gate. Hornet's pattern, Weaver's domain.**

Inspects every `git` invocation via `PreToolUse(Bash)`. If the command matches a destructive-op pattern (force-push, `filter-branch`, `reset --hard` past pushed tip, `branch -D`, `tag -d`, `clean -fdx`, remote-branch deletion, `commit --amend` of a pushed HEAD, merge-queue `--admin` bypass), routes through a confirmation surface before allowing it.

No engine — rules-only. Haiku classifies destructive vs safe per the pattern table. Protected-branch force-push: **never** bypassed. `git clean -fdx`: **never** bypassed (irrecoverable — reflog doesn't cover ignored files).

## Destructive-pattern table

| Pattern ID | Matches | Severity | Bypass | Notes |
|------------|---------|----------|--------|-------|
| `force_push` | `git push --force` / `-f` | destructive | `--yes-i-know` (one-shot) | Never bypassed on protected branches |
| `force_with_lease` | `git push --force-with-lease` | destructive | `--yes-i-know` | Never bypassed on protected branches |
| `filter_branch` | `git filter-branch` / `filter-repo` | destructive | `--yes-i-know` | History rewrite |
| `reset_hard` | `git reset --hard` | destructive | `--yes-i-know` | Reflog covers 90d |
| `rebase_interactive` | `git rebase -i` / `--interactive` | destructive | `--yes-i-know` | History rewrite when pushed |
| `branch_delete` | `git branch -D` | destructive | `--yes-i-know` | Reflog covers 90d |
| `remote_branch_delete` | `git push --delete <branch>` | destructive | `--yes-i-know` | Host retention varies |
| `tag_delete` | `git tag -d` | destructive | `--yes-i-know` | Remote delete is permanent |
| `clean_fdx` | `git clean -fdx` / `-fdX` | protected-destructive | **never** | Reflog does not cover ignored files |
| `amend_of_pushed_head` | `git commit --amend` when HEAD is reachable from a remote-tracking ref | destructive | `--yes-i-know` | Closes anti-pattern #2 (CLAUDE.md). Context-checked via `amend_safety.is_head_pushed` — amend on an unpushed branch is safe |

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
