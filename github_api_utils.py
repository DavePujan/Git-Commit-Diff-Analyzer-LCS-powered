# github_api_utils.py

import requests
import base64
from typing import List, Optional

class GitHubAPIError(Exception):
    pass

class GitHubRepo:
    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        self.owner = owner
        self.repo = repo
        self.base_api = "https://api.github.com"
        self.session = requests.Session()
        self.token = token
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
        self.session.headers.update({"Accept": "application/vnd.github.v3+json"})

    def _repo_path(self, path: str) -> str:
        return f"/repos/{self.owner}/{self.repo}{path}"

    def get_file_at_ref(self, path: str, ref: str) -> str:
        api_path = self._repo_path(f"/contents/{path}")
        params = {"ref": ref}
        resp = self.session.get(self.base_api + api_path, params=params)
        if resp.status_code == 404:
            raise FileNotFoundError(f"File {path} not found at ref {ref}")
        if not resp.ok:
            raise GitHubAPIError(f"GitHub API error {resp.status_code}: {resp.text}")
        j = resp.json()
        if isinstance(j, list):
            raise GitHubAPIError(f"Expected file but got directory listing at {path}@{ref}")
        content = j.get("content")
        encoding = j.get("encoding")
        if content is None or encoding is None:
            raise GitHubAPIError(f"File content or encoding missing for {path}@{ref}")
        if encoding == "base64":
            b = base64.b64decode(content.encode("utf-8"))
            return b.decode("utf-8", errors="replace")
        else:
            return content

    def get_changed_files_between(self, base: str, head: str) -> List[str]:
        api_path = self._repo_path(f"/compare/{base}...{head}")
        resp = self.session.get(self.base_api + api_path)
        if not resp.ok:
            raise GitHubAPIError(f"GitHub compare API error {resp.status_code}: {resp.text}")
        j = resp.json()
        files = j.get("files", [])
        paths = []
        for f in files:
            paths.append(f.get("filename"))
        return paths

    def get_all_files_at_ref(self, ref: str) -> List[str]:
        commit_api = self._repo_path(f"/commits/{ref}")
        resp = self.session.get(self.base_api + commit_api)
        if not resp.ok:
            raise GitHubAPIError(f"GitHub commit API error {resp.status_code}: {resp.text}")
        j = resp.json()
        tree_sha = j["commit"]["tree"]["sha"]
        tree_api = self._repo_path(f"/git/trees/{tree_sha}")
        resp2 = self.session.get(self.base_api + tree_api, params={"recursive": "1"})
        if not resp2.ok:
            raise GitHubAPIError(f"GitHub tree API error {resp2.status_code}: {resp2.text}")
        tree_j = resp2.json()
        tree_list = tree_j.get("tree", [])
        paths = []
        for item in tree_list:
            if item.get("type") == "blob":
                paths.append(item.get("path"))
        return paths
