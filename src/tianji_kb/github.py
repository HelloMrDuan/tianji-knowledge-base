from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


class GitHubError(RuntimeError):
    pass


@dataclass
class GitHubClient:
    token: str | None = None
    api_base: str = "https://api.github.com"

    def __post_init__(self) -> None:
        if self.token is None:
            self.token = os.getenv("GITHUB_TOKEN")

    def _request(self, url: str) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "tianji-knowledge-base/0.2",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GitHubError(f"GitHub API {exc.code}: {body[:500]}") from exc
        except urllib.error.URLError as exc:
            raise GitHubError(f"GitHub network error: {exc}") from exc

    def api(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.api_base}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        return self._request(url)

    def repo(self, full_name: str) -> dict[str, Any]:
        return self.api(f"/repos/{full_name}")

    def latest_commit(self, full_name: str, ref: str) -> dict[str, Any]:
        return self.api(f"/repos/{full_name}/commits/{urllib.parse.quote(ref, safe='')}")

    def license(self, full_name: str) -> dict[str, Any] | None:
        try:
            return self.api(f"/repos/{full_name}/license")
        except GitHubError as exc:
            if "404" in str(exc):
                return None
            raise

    def fetch_text_file(self, full_name: str, path: str, ref: str | None = None) -> str:
        params = {"ref": ref} if ref else None
        payload = self.api(
            f"/repos/{full_name}/contents/{urllib.parse.quote(path, safe='/')}",
            params,
        )
        if payload.get("type") != "file":
            raise GitHubError(f"Not a file: {full_name}/{path}")
        encoding = payload.get("encoding")
        content = payload.get("content") or ""
        if encoding == "base64":
            return base64.b64decode(content).decode("utf-8")
        if encoding in (None, "utf-8"):
            return str(content)
        raise GitHubError(f"Unsupported encoding {encoding!r}: {full_name}/{path}")

    def search_repositories(self, query: str, per_page: int = 20, page: int = 1) -> list[dict[str, Any]]:
        payload = self.api("/search/repositories", {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": min(per_page, 100),
            "page": page,
        })
        return payload.get("items", [])
