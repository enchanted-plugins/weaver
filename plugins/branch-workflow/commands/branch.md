---
name: weaver:branch
description: Create or switch to a new branch for the current task boundary, named per the detected workflow (GitHub Flow uses type/slug, Trunk-Based uses user/slug, etc.). Reads active W2 cluster to slug the branch if no name is supplied.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/../../shared/scripts/workflow_detect.py *), Bash(python ${CLAUDE_PLUGIN_ROOT}/../../shared/scripts/workflow_detect.py *), Bash(git branch *), Bash(git checkout *), Bash(git status *), Read(plugins/boundary-segmenter/state/boundary-clusters.json)
---

# /weaver:branch

Create and check out a branch named per the repo's detected workflow.

## Usage

```
/weaver:branch                                # infer slug from active W2 cluster
/weaver:branch "add oauth pkce support"       # explicit slug
/weaver:branch --type fix "null session token"  # override Conventional Commits type
/weaver:branch --from-boundary <boundary-id>  # name based on a closed cluster
/weaver:branch --dry-run ...                  # show the chosen name, do not create
```

## Flow

```
1. Detect workflow via `shared/scripts/workflow_detect.py detect`.
2. Pick the slug:
   ├─ explicit arg wins
   ├─ else read active cluster from `plugins/boundary-segmenter/state/boundary-clusters.json`
   │  and extract a slug from the dominant file path + top token
   └─ else abort with hint to pass an explicit slug
3. Pick the type:
   ├─ --type flag wins
   ├─ else default per workflow ('feat' for github-flow / trunk-based,
   │  'feature' for gitflow, etc.)
   └─ stacked-diffs ignores type (short topic names only)
4. Call `shared/scripts/workflow_detect.py suggest-branch <workflow> <type> <slug>`.
5. Check out a new branch with that name (unless --dry-run):
   `git checkout -b <name>`
6. Publish `weaver.branch.created` to state/metrics.jsonl.
```

## Guardrails

- If the working tree is dirty when invoked on `main`/`master`/`trunk`,
  refuse and suggest the user either commit with `/weaver:commit` or
  stash first. Creating a branch carries uncommitted work along, and
  that confuses the per-boundary cluster ownership story.
- Never force-delete an existing branch. If the suggested name collides,
  append `-2`, `-3`, etc., and report the collision.
- For stacked-diff tools (Graphite / Sapling / git-branchless), prefer
  the tool's own branch command when it's installed (`gt create`,
  `sl commit`, `git-branchless submit`). W3 detects these; W4's PR
  lifecycle handles stacking.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Branch created and checked out |
| 1 | Dirty tree on trunk (aborted with hint) |
| 2 | No slug provided and active cluster empty |
| 3 | Git error (e.g., name collision after retries) |
