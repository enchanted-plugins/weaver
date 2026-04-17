"""
Stub CI adapters for the 7 non-GitHub systems.

Each raises NotImplementedCIOp for every op. ci-reader degrades gracefully:
when a stub fires, the caller logs a `weaver.ci.manual_handoff.required`
event and skips gating (the PR can still merge if the developer forces it).
"""

from __future__ import annotations

from typing import Any

from . import Check, CIAdapter, NotImplementedCIOp


class _StubBase(CIAdapter):
    system_id = "stub"

    def is_available(self) -> bool:
        return False

    def latest_status(self, repo: str, ref: str) -> list[Check]:
        # Return empty rather than raising — is_available() is False so the
        # caller already knows not to expect anything useful.
        return []

    def stream_logs(self, check_id: str):
        raise NotImplementedCIOp(self.system_id, "stream_logs")

    def rerun(self, check_id: str) -> bool:
        raise NotImplementedCIOp(self.system_id, "rerun")


class GitLabCIAdapter(_StubBase):
    system_id = "gitlab-ci"


class CircleCIAdapter(_StubBase):
    system_id = "circleci"


class JenkinsAdapter(_StubBase):
    """Jenkins stub — when implemented, must handle the `result == SUCCESS`
    vs `result == UNSTABLE` distinction that tripped semantic-release in 2021.
    Anything other than `SUCCESS` + `result == SUCCESS` on the final stage
    counts as non-green."""
    system_id = "jenkins"


class BuildkiteAdapter(_StubBase):
    system_id = "buildkite"


class DroneAdapter(_StubBase):
    system_id = "drone"


class WoodpeckerAdapter(_StubBase):
    system_id = "woodpecker"


class TektonAdapter(_StubBase):
    """Tekton stub — requires kubectl access to watch PipelineRun CRDs.
    Full implementation needs Kubernetes client library or shelling out
    to kubectl, both of which are heavier deps than GitHub's `gh` CLI."""
    system_id = "tekton"


class ArgoCDAdapter(_StubBase):
    """ArgoCD stub. GitOps paradigm — Weaver reads sync-status and surfaces
    drift. Never gates (ArgoCD doesn't run PR checks)."""
    system_id = "argocd"


class FluxCDAdapter(_StubBase):
    """FluxCD stub. Same paradigm notes as ArgoCD."""
    system_id = "fluxcd"
