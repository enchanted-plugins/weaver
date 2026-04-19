"""CircleCI adapter — reads pipeline/workflow status via API v2."""

from __future__ import annotations

from typing import Any

from . import Check, CIAdapter, NotImplementedCIOp
from ._http import resolve_token, get_json, CIHttpError


class CircleCIAdapter(CIAdapter):
    system_id = "circleci"

    def __init__(self, token: str | None = None, api_base: str = "https://circleci.com/api/v2"):
        self.api_base = api_base.rstrip("/")
        self._token_explicit = token
        self._token_cached: str | None = None
        self._token_probed = False

    def _token(self) -> str | None:
        if self._token_explicit:
            return self._token_explicit
        if not self._token_probed:
            self._token_cached = resolve_token(
                ["CIRCLECI_TOKEN", "CIRCLE_TOKEN"], "circleci.com"
            )
            self._token_probed = True
        return self._token_cached

    def is_available(self) -> bool:
        return bool(self._token())

    def latest_status(self, repo: str, ref: str) -> list[Check]:
        """CircleCI addresses projects by slug: `{vcs}/{org}/{repo}`.
        We default to github/{repo} since Weaver's main host is GitHub."""
        tok = self._token()
        if not tok:
            return []

        slug = f"gh/{repo}" if "/" in repo and not repo.startswith("gh/") else repo
        url = f"{self.api_base}/project/{slug}/pipeline?branch={ref}"
        try:
            data = get_json(url, token=tok, auth_scheme=None,
                            extra_headers={"Circle-Token": tok})
        except CIHttpError:
            return []

        items = data.get("items") if isinstance(data, dict) else None
        if not items:
            return []

        latest = items[0]
        pipeline_id = latest.get("id")
        # Fetch workflows for this pipeline.
        wf_url = f"{self.api_base}/pipeline/{pipeline_id}/workflow"
        try:
            wf = get_json(wf_url, token=tok, auth_scheme=None,
                          extra_headers={"Circle-Token": tok})
        except CIHttpError:
            return []
        workflows = wf.get("items") if isinstance(wf, dict) else []
        out: list[Check] = []
        for w in workflows or []:
            status = str(w.get("status") or "")
            out.append(Check(
                system=self.system_id,
                name=str(w.get("name") or "workflow"),
                status=self._map_status(status),
                conclusion=self._map_conclusion(status),
                url=f"https://app.circleci.com/pipelines/{slug}/{pipeline_id}",
                started_at=w.get("created_at"),
                completed_at=w.get("stopped_at"),
                raw=w,
            ))
        return out

    @staticmethod
    def _map_status(s: str) -> str:
        if s in ("running", "on_hold"):
            return "in_progress"
        if s in ("queued", "created"):
            return "queued"
        return "completed"

    @staticmethod
    def _map_conclusion(s: str) -> str | None:
        if s == "success":
            return "success"
        if s in ("failed", "failing"):
            return "failure"
        if s == "canceled":
            return "cancelled"
        return None

    def stream_logs(self, check_id: str):
        raise NotImplementedCIOp(self.system_id, "stream_logs: not yet")

    def rerun(self, check_id: str) -> bool:
        return False
