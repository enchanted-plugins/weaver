# Weaver — Agent Contract

Audience: Claude. Weaver owns the git-workflow layer of AI-assisted development. Observes Claude Code sessions, segments work into logical tasks, auto-branches, auto-commits per cohesive chunk, and auto-opens draft PRs with session context. Destructive ops always route through a Hornet-style decision-gate.

## Lifecycle

Weaver is hook-driven, not skill-invoked. Auto-orchestration is the product's reason to exist.

| Event | Plugin | Role |
|-------|--------|------|
| `SessionStart` | capability-memory | Load provider registry, probe GitLab self-managed version |
| `PostToolUse(Edit\|Write)` | boundary-segmenter | W2 clusters edit events into task boundaries |
| On boundary | branch-workflow + commit-intelligence | W3 picks branch strategy, W1 drafts Conventional Commits message |
| On cluster close | pr-lifecycle | W4 opens draft PR, routes reviewers, subscribes to CI status |
| `PreToolUse(Bash)` | weaver-gate | Destructive-op decision-gate (force-push, rebase, reset, clean) |
| On CI status change | ci-reader | Reads status from 8 CI systems, gates merge-queue entry |
| `PreCompact` | weaver-learning | W5 checkpoints developer preferences + cluster state |

## Named engines (brand standard)

| ID | Name | Plugin | Algorithm |
|----|------|--------|-----------|
| W1 | Myers-Diff Conventional Classifier | commit-intelligence | Diff summarization + rule-based classifier + LLM re-rank |
| W2 | Jaccard-Cosine Boundary Segmentation | boundary-segmenter | Online agglomerative clustering, multi-modal distance. **Defining engine** |
| W3 | Workflow-Pattern Classifier | branch-workflow | Weighted decision tree over repo feature vector |
| W4 | Path-History Reviewer Routing | pr-lifecycle | Blame-graph weighted scoring + recency decay + availability filter |
| W5 | Gauss Learning (Weaver) | weaver-learning | Weighted moving averages over preference signals, Allay-A4 persistence |

## Tier-1 vs Tier-2 hosts

| Host | Support Level | Notes |
|------|---------------|-------|
| GitHub (Cloud + Enterprise Server) | first-class | Check Runs API, Merge Queue, native CODEOWNERS |
| GitLab (SaaS + self-managed) | first-class | Merge Trains, version-probed at runtime |
| Bitbucket Cloud | first-class | Unsigned webhooks default — mitigated via shared-secret |
| Bitbucket Data Center | first-class | Different REST API from Cloud |
| Azure DevOps | best-effort | VSTS-era REST, scoped org/project/repo |
| Gitea / Forgejo / Codeberg | best-effort | GitHub-compatible subset |
| AWS CodeCommit | read-only | SigV4; no native PR UI |
| SourceHut | read-only | Mailing-list PRs — `git send-email`, no `pulls` abstraction |

## CI/CD boundary

Weaver **reads** CI status across 8 systems (GitHub Actions, GitLab CI, CircleCI, Jenkins, Buildkite, Drone/Woodpecker, Tekton, ArgoCD/FluxCD). Weaver **does not own** CI execution — that's Assembler's domain. Boundary enforced via the enchanted-mcp event bus:

- **Weaver publishes**: `weaver.task.boundary.detected`, `weaver.commit.committed`, `weaver.pr.drafted`, `weaver.pr.ready`, `weaver.destructive.detected`, `weaver.ci.status.observed`
- **Weaver subscribes**: `assembler.pipeline.status.changed`, `hornet.change.classified`, `hornet.session.continuity.node`, `hornet.reviewer.availability.changed`, `reaper.prepush.secret.detected`, `nook.budget.threshold.crossed`

## Destructive-op contract

Every destructive op routes through weaver-gate. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#destructive-op-confirmation-contract) for the full table. Key rules:

- Force-push to protected branches: **never** bypassed.
- `git clean -fdx`: **never** bypassed (irrecoverable).
- Merge-queue `--admin` bypass: **never** without explicit `--admin-bypass` flag.
- All other destructive ops: `--yes-i-know` bypass for one invocation, always audited.

Audit log: `plugins/*/state/audit.jsonl` — append-only, Allay-A4 atomic pattern.

## Behavioral contracts

1. **IMPORTANT — Silent by default, loud when risky.** Auto-orchestration is invisible when it works. Decision-gates are blocking only for destructive ops. Nothing routine asks for permission.
2. **YOU MUST respect the Assembler ownership boundary.** Weaver reads CI status; Weaver never triggers a build. If a workflow requires a build trigger, publish to `weaver.ci.trigger.requested` and let Assembler fulfil it.
3. **YOU MUST NOT write history rewrites without gate confirmation.** Even if the developer asks, route through `weaver-gate`. The developer's explicit confirmation is logged, not assumed.
4. **ESCALATE on SourceHut push operations.** SourceHut uses mailing-list PRs — if the developer's remote points to SourceHut, degrade to patch-email mode and surface the divergence.
5. **ESCALATE when the capability registry is stale.** If `state/capability-registry.json` is older than 30 days and the developer is on a Tier-1 host, nudge toward a nightly-refresh check.
6. **Ask, don't guess.** If `git status` is dirty at session-start or the branch naming doesn't match the detected workflow, ask before continuing. Never fabricate a task-boundary when none is certain.
7. **YOU MUST defer secret scanning to Reaper.** The `reaper.prepush.secret.detected` event is authoritative — Weaver blocks push when it fires, never second-guesses.
8. **YOU MUST NOT inflate clustering confidence.** W2 emits confidence per boundary; when confidence < 0.7, route to the Opus boundary-detector agent for judgment rather than acting autonomously.

## Brand standard compliance

- **Zero external runtime deps.** Hooks: bash + jq. Scripts: Python 3.8+ stdlib. `git-credential-manager` recommended; `gh auth` fast-path for GitHub. Tree-sitter gated behind `--deep-signals` flag.
- **Managed agents.** Opus for boundary judgment + PR description + conflict proposals. Sonnet for commit drafting + CODEOWNERS reasoning. Haiku for format validation + policy checks.
- **Gauss Accumulation (W5).** Per-developer preference persistence in `plugins/weaver-learning/state/learnings.json`, exported to `shared/learnings.json`.
- **Dark-themed PDF audit.** Ships from each plugin on final release.
- **Allay-style marketplace structure.** `plugins/<name>/{agents,commands,hooks,skills,state}` per sub-plugin.

## Anti-patterns

- **Owning CI execution.** Drifting into "Weaver builds the pipeline" violates the Assembler boundary. Triggering belongs on `weaver.ci.trigger.requested` → Assembler.
- **Auto-amending pushed commits.** W1's safe-amend detection must block this. Even if the Conventional Commits message is wrong, the fix is a follow-up commit, not `--amend`.
- **Silent history rewrite on late-boundary correction.** W2's late-boundary correction surfaces as a skill invocation, never a silent `git rebase -i` or `git reset`.
- **Reviewer storms.** W4 caps auto-requested reviewers at 3. Larger pools rotate across subsequent PRs, not stacked on one.
- **GitHub-shaped assumptions in the abstraction layer.** The Provider Capability Schema must be filled for SourceHut (the hardest edge) before any host code ships — that's the test that proves the abstraction isn't GitHub-shaped underneath.

Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Crafted by Flux at `flux/prompts/weaver-architecture/` (σ=0.40, DEPLOY).
