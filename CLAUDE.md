# Sylph — Agent Contract

Audience: Claude. Sylph owns the git-workflow layer of AI-assisted development. Observes Claude Code sessions, segments work into logical tasks, auto-branches, auto-commits per cohesive chunk, and auto-opens draft PRs with session context. Destructive ops always route through a decision-gate.

## Shared behavioral modules

These apply to every skill in every plugin. Load once; do not re-derive.

- @shared/conduct/discipline.md — coding conduct: think-first, simplicity, surgical edits, goal-driven loops
- @shared/conduct/context.md — attention-budget hygiene, U-curve placement, checkpoint protocol
- @shared/conduct/verification.md — independent checks, baseline snapshots, dry-run for destructive ops
- @shared/conduct/delegation.md — subagent contracts, tool whitelisting, parallel vs. serial rules
- @shared/conduct/failure-modes.md — 14-code taxonomy for accumulated-learning logs
- @shared/conduct/tool-use.md — tool-choice hygiene, error payload contract, parallel-dispatch rules
- @shared/conduct/formatting.md — per-target format (XML/Markdown/minimal/few-shot), prefill + stop sequences
- @shared/conduct/skill-authoring.md — SKILL.md frontmatter discipline, discovery test
- @shared/conduct/hooks.md — advisory-only hooks, injection over denial, fail-open
- @shared/conduct/precedent.md — log self-observed failures to `state/precedent-log.md`; consult before risky steps
- @shared/conduct/tier-sizing.md — agent-tier budget allocation per task class
- @shared/conduct/web-fetch.md — external-URL-handling hygiene

When a module conflicts with a plugin-local instruction, the plugin wins — but log the override.

## Lifecycle

Sylph is hook-driven, not skill-invoked. Auto-orchestration is the product's reason to exist.

| Event / Skill | Plugin | Role |
|---|---|---|
| `SessionStart` | capability-memory | Load provider registry, probe git host + CI; cache capabilities |
| `SessionStart` | weaver-learning | Load W5 per-developer priors |
| `SessionStart` | ci-reader | Load CI registry |
| `PostToolUse(Edit\|Write\|MultiEdit)` | boundary-segmenter | W2 clusters edit events into task boundaries; checkpoints clusters at PreCompact |
| On boundary | branch-workflow | W3 picks branch strategy; scaffolds the branch |
| On boundary | commit-intelligence | W1 drafts Conventional Commits message; Haiku + Python validate |
| `PostToolUse(Bash)` | pr-lifecycle | On committed boundary, W4 opens draft PR, routes reviewers, subscribes to CI status |
| `PreToolUse(Bash)` | weaver-gate | Destructive-op decision-gate (force-push, rebase, reset, clean) |
| `PreCompact` | weaver-learning | W5 checkpoints developer preferences + cluster state |

Matchers in `./plugins/<name>/hooks/hooks.json`. Agents in `./plugins/<name>/agents/`.

## Algorithms

W1 Myers-Diff Conventional Classifier · W2 Jaccard-Cosine Boundary Segmentation · W3 Workflow-Pattern Classifier · W4 Blame-Weighted Reviewer Ranker · W5 Gauss Learning (Sylph). Derivations in `docs/science/README.md`. **Defining engine:** W2.

| ID | Name | Plugin | Algorithm | Reference |
|----|------|--------|-----------|-----------|
| W1 | Myers-Diff Conventional Classifier | commit-intelligence | Myers diff → rule-based classifier → Sonnet LLM re-rank + Haiku rules validation. Subjects ≤72 chars, body ≤72 chars/line, Conventional Commits 1.0 types enforced. | Myers E.W. (1986), "An O(ND) Difference Algorithm and Its Variations", Algorithmica 1(1-4):251-266; Conventional Commits 1.0.0 spec (conventionalcommits.org) |
| W2 | Jaccard-Cosine Boundary Segmentation | boundary-segmenter | Online agglomerative clustering; `d = α·(1−jaccard(files)) + β·(1−cosine(tokens)) + γ·tanh(idle/τ)`. α=β=0.4, γ=0.2, τ=300 s, θ=0.55. Crow V1 embedding if available; stdlib bag-of-tokens otherwise. | Jaccard P. (1901); Salton, Wong, Yang (1975); Hearst M.A. (1997), "TextTiling", Computational Linguistics 23(1):33-64 |
| W3 | Workflow-Pattern Classifier | branch-workflow | Weighted decision tree over branch-age distribution, protection rules, config-file markers, tag cadence. Classifies: stacked-diffs / gitflow / release-flow / trunk-based / github-flow / unknown. Per-subtree overrides via `.sylph/workflow-map.yaml`. | Driessen V. (2010), "A successful Git branching model"; Quinlan J.R. (1986), "Induction of Decision Trees", Machine Learning 1(1):81-106 |
| W4 | Blame-Weighted Reviewer Ranker | pr-lifecycle | Weighted sum: `blame_score × recency_decay × path_depth × codeowners_boost × availability`. 90-day half-life on last-commit timestamp, CODEOWNERS union boost (1.5×), top-3 cap. | Thongtanunam et al. (2015), "Who should review my code?", IEEE/ACM SANER 2015:141-150 (file-history-based reviewer recommendation) |
| W5 | Gauss Learning (Sylph) | weaver-learning | EMA update `new = α·signal + (1−α)·old`, α=0.3. Tracks commit style, branch-naming, PR turnaround, reviewer overrides, W2 threshold corrections per-developer. Bootstrap floor at 10 samples; below floor, priors are ignored. | Gauss C.F. (1809), "Theoria motus corporum coelestium" (least-squares); ecosystem precedent: Wixie F6, Emu A7, Crow H6, Djinn C5, Gorgon G5, Naga N5 |

## Behavioral contracts

1. **IMPORTANT — Silent by default, loud when risky.** Auto-orchestration is invisible when it works. Decision-gates are blocking only for destructive ops. Nothing routine asks for permission.
2. **YOU MUST NOT write history rewrites without gate confirmation.** Even if the developer asks, route through `weaver-gate`. The developer's explicit confirmation is logged, not assumed.
3. **ESCALATE on SourceHut push operations.** SourceHut uses mailing-list PRs — if the developer's remote points to SourceHut, degrade to patch-email mode and surface the divergence.
4. **ESCALATE when the capability registry is stale.** If `state/capability-registry.json` is older than 30 days and the developer is on a Tier-1 host, nudge toward a nightly-refresh check.
5. **Ask, don't guess.** If `git status` is dirty at session-start or the branch naming doesn't match the detected workflow, ask before continuing. Never fabricate a task-boundary when none is certain.
6. **YOU MUST defer secret scanning to Hydra.** The `hydra.prepush.secret.detected` event is authoritative — Sylph blocks push when it fires, never second-guesses.
7. **YOU MUST NOT inflate clustering confidence.** W2 emits confidence per boundary; when confidence < 0.7, route to the Opus boundary-detector agent for judgment rather than acting autonomously.

## State paths

| State file | Owner | Purpose |
|---|---|---|
| `plugins/capability-memory/state/capability-registry.json` | capability-memory | 10-host capability data (24 fields/host), nightly-refreshed |
| `plugins/capability-memory/state/session-cache/` | capability-memory | Per-session resolved-host slice |
| `plugins/boundary-segmenter/state/boundary-clusters.json` | boundary-segmenter | W2 rolling cluster state, survives compaction |
| `plugins/boundary-segmenter/state/boundary-events.jsonl` | boundary-segmenter | Every fired task boundary, append-only |
| `plugins/boundary-segmenter/state/escalations.jsonl` | boundary-segmenter | W2 uncertainty escalations to boundary-detector agent |
| `plugins/boundary-segmenter/state/escalation-verdicts.jsonl` | boundary-segmenter | boundary-detector verdicts, append-only |
| `plugins/commit-intelligence/state/metrics.jsonl` | commit-intelligence | Per-commit W1 classification metrics |
| `plugins/pr-lifecycle/state/last-reviewer-suggestion.json` | pr-lifecycle | W4's last blame-graph reviewer ranking |
| `plugins/pr-lifecycle/state/pending-prs.jsonl` | pr-lifecycle | Open PRs being monitored for CI status |
| `plugins/weaver-gate/state/audit.jsonl` | weaver-gate | Every gated/blocked destructive op — append-only, Emu-A4 atomic write |
| `plugins/weaver-learning/state/learnings.json` | weaver-learning | W5 EMA priors, cross-session |
| `plugins/weaver-learning/state/priors.json` | weaver-learning | Session-cached slice downstream engines read |
| `plugins/ci-reader/state/ci-registry.json` | ci-reader | 10-CI-system registry; gates merge-queue entry; ArgoCD/WixieCD read-only |

## Agent tiers

| Tier | Model | Agent | Plugin | Used for |
|------|-------|-------|--------|----------|
| Orchestrator | Opus | boundary-detector | boundary-segmenter | Tipping-judgment on W2 uncertainty band (θ ± 0.10) — decides open/extend |
| Orchestrator | Opus | conflict-resolver | pr-lifecycle | Three-way merge resolution proposals; never auto-applies |
| Orchestrator | Opus | pr-description-crafter | pr-lifecycle | Compose structured PR body from W2 cluster + git log + Crow V4 session nodes |
| Executor | Sonnet | commit-drafter | commit-intelligence | W1 Stage 1 — Myers-diff Conventional Commits drafting |
| Validator | Haiku | message-validator | commit-intelligence | W1 Stage 2 — format + policy rules check; escalates ambiguous cases only |

Respect the tiering. Routing a Haiku validation task to Opus burns budget and breaks the cost contract.

## Anti-patterns

- **Owning CI execution.** Sylph is a reader, not a runner — do not add build-trigger code paths. CI execution belongs to your existing CI pipelines.
- **Auto-amending pushed commits.** W1's safe-amend detection must block this. Even if the Conventional Commits message is wrong, the fix is a follow-up commit, not `--amend`.
- **Silent history rewrite on late-boundary correction.** When W2 confidence is low (< 0.7), the boundary escalates to `/sylph:review-boundary` — an Opus agent judgment invoked via skill, never a silent `git rebase -i` or `git reset`. Low-confidence boundaries are surfaced for human review + learning, not silently rewritten.
- **Reviewer storms.** W4 caps auto-requested reviewers at 3. Larger pools rotate across subsequent PRs, not stacked on one.
- **GitHub-shaped assumptions in the abstraction layer.** The Provider Capability Schema must be filled for SourceHut (the hardest edge) before any host code ships — that's the test that proves the abstraction isn't GitHub-shaped underneath.
- **Fabricating CI status.** When credentials/tooling are absent, adapters return empty — never fabricate a normalized `Check` result.
- **Triggering builds.** Sylph reads CI status via `ci-reader`; it never fires a fresh build. `/sylph:retry-ci` reruns existing runs only.

---

Events this plugin publishes: `sylph.task.boundary.detected`, `sylph.commit.committed`, `sylph.pr.drafted`, `sylph.pr.ready`, `sylph.destructive.detected`, `sylph.ci.status.observed`
Events this plugin subscribes to (Phase 1 only): `crow.session.continuity.node` (PR description context), `crow.reviewer.availability.changed` (W4 availability filter)
