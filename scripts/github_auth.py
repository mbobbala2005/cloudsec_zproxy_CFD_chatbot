#!/usr/bin/env python3
"""
GitHub App authentication helpers for git/gh subprocesses.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence
from urllib import error, request
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_GITHUB_BASE_URL = "https://github.com"


def extract_owner_repo_from_remote_url(remote_url: str) -> str:
    candidate = (remote_url or "").strip()
    if not candidate:
        return ""

    if "://" in candidate:
        path = urlparse(candidate).path.lstrip("/")
    elif ":" in candidate and "@" in candidate:
        path = candidate.split(":", 1)[1]
    else:
        path = candidate

    return path.removesuffix(".git").strip("/")


def resolve_private_key_path(private_key_path: str) -> Path:
    path = Path(private_key_path).expanduser()
    if not path.is_absolute():
        path = Path(__file__).parent.parent / path
    return path


def default_github_api_url(github_base_url: str) -> str:
    base_url = github_base_url.rstrip("/")
    if base_url == DEFAULT_GITHUB_BASE_URL:
        return "https://api.github.com"
    return f"{base_url}/api/v3"


def github_host_from_base_url(github_base_url: str) -> str:
    parsed = urlparse(github_base_url)
    return parsed.netloc or "github.com"


def get_remote_origin_url(repo_path: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()
        return remote_url or None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _git_command_needs_remote_auth(command: Sequence[str]) -> bool:
    return len(command) > 1 and command[1] in {"clone", "fetch", "pull", "ls-remote"}


def _is_ssh_remote_url(remote_url: str) -> bool:
    candidate = (remote_url or "").strip()
    if not candidate:
        return False
    if candidate.startswith("ssh://"):
        return True
    return "://" not in candidate and "@" in candidate and ":" in candidate


def _remote_prefix(remote_url: str, owner_repo: str) -> Optional[str]:
    for suffix in (f"{owner_repo}.git", owner_repo):
        index = remote_url.find(suffix)
        if index != -1:
            return remote_url[:index]
    return None


def _repo_owner(owner_repo: str) -> str:
    return owner_repo.split("/", 1)[0].strip()


@dataclass
class InstallationToken:
    token: str
    expires_at_epoch: float


class GitHubAppAuth:
    def __init__(
        self,
        app_id: str,
        private_key_path: str,
        github_base_url: Optional[str] = None,
        github_api_url: Optional[str] = None,
        installation_id: Optional[str] = None,
    ) -> None:
        self.app_id = str(app_id).strip()
        self.private_key_path = resolve_private_key_path(private_key_path)
        if not self.private_key_path.exists():
            raise FileNotFoundError(f"GitHub App private key not found: {self.private_key_path}")

        self.github_base_url = (github_base_url or DEFAULT_GITHUB_BASE_URL).rstrip("/")
        self.github_api_url = (github_api_url or default_github_api_url(self.github_base_url)).rstrip("/")
        self.github_host = github_host_from_base_url(self.github_base_url)
        self.default_installation_id = int(installation_id) if installation_id else None
        self.installation_ids_by_repo: Dict[str, int] = {}
        self.installation_ids_by_owner: Dict[str, int] = {}
        self.tokens_by_installation: Dict[int, InstallationToken] = {}

    def _build_app_jwt(self) -> str:
        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT"}
        payload = {"iat": now - 60, "exp": now + 540, "iss": self.app_id}
        unsigned = (
            f"{_b64url(json.dumps(header, separators=(',', ':')).encode('utf-8'))}."
            f"{_b64url(json.dumps(payload, separators=(',', ':')).encode('utf-8'))}"
        )

        try:
            result = subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", str(self.private_key_path), "-binary"],
                input=unsigned.encode("utf-8"),
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
            raise RuntimeError(f"Failed to sign GitHub App JWT with openssl: {stderr}") from exc
        except FileNotFoundError as exc:
            raise RuntimeError("openssl is required to sign GitHub App JWTs") from exc

        signature = _b64url(result.stdout)
        return f"{unsigned}.{signature}"

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
    ) -> Any:
        req = request.Request(url, data=body, method=method)
        for key, value in (headers or {}).items():
            req.add_header(key, value)

        try:
            with request.urlopen(req, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API request failed ({exc.code}) for {url}: {body_text}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"GitHub API request failed for {url}: {exc}") from exc

        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"GitHub API returned invalid JSON for {url}: {payload}") from exc

    def _app_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._build_app_jwt()}",
            "Accept": "application/vnd.github+json",
        }

    def _list_installations(self) -> list[Dict[str, Any]]:
        payload = self._request_json(
            "GET",
            f"{self.github_api_url}/app/installations",
            headers=self._app_headers(),
        )
        if not isinstance(payload, list):
            raise RuntimeError(
                f"GitHub API returned unexpected payload for /app/installations: {payload}"
            )
        return payload

    def get_installation_id(self, owner_repo: str) -> int:
        if self.default_installation_id is not None:
            return self.default_installation_id

        installation_id = self.installation_ids_by_repo.get(owner_repo)
        if installation_id is not None:
            return installation_id

        owner = _repo_owner(owner_repo)
        installation_id = self.installation_ids_by_owner.get(owner)
        if installation_id is not None:
            self.installation_ids_by_repo[owner_repo] = installation_id
            return installation_id

        installations = self._list_installations()
        matching_installations = [
            installation
            for installation in installations
            if (
                isinstance(installation, dict)
                and (installation.get("account") or {}).get("login") == owner
                and installation.get("id")
            )
        ]

        if len(matching_installations) == 1:
            installation_id = int(matching_installations[0]["id"])
        elif len(matching_installations) > 1:
            installation_ids = ", ".join(str(item["id"]) for item in matching_installations)
            raise RuntimeError(
                f"Multiple GitHub App installations matched owner '{owner}' "
                f"for repo {owner_repo}: {installation_ids}. Set INSTALLATION_ID in .env."
            )
        elif len(installations) == 1 and isinstance(installations[0], dict) and installations[0].get("id"):
            installation_id = int(installations[0]["id"])
            logger.warning(
                "No owner-specific installation match found for %s; falling back to installation id %s",
                owner_repo,
                installation_id,
            )
        else:
            available_accounts = ", ".join(
                str((installation.get("account") or {}).get("login"))
                for installation in installations
                if isinstance(installation, dict)
            )
            raise RuntimeError(
                f"No GitHub App installation matched repo owner '{owner}' for {owner_repo}. "
                f"Available installation accounts: {available_accounts or 'none'}. "
                "Set INSTALLATION_ID in .env if needed."
            )

        self.installation_ids_by_repo[owner_repo] = installation_id
        self.installation_ids_by_owner[owner] = installation_id
        return installation_id

    def get_installation_token(self, owner_repo: str) -> str:
        installation_id = self.get_installation_id(owner_repo)
        cached = self.tokens_by_installation.get(installation_id)
        now = time.time()
        if cached and now < cached.expires_at_epoch - 60:
            return cached.token

        payload = self._request_json(
            "POST",
            f"{self.github_api_url}/app/installations/{installation_id}/access_tokens",
            headers={**self._app_headers(), "Content-Type": "application/json"},
            body=b"{}",
        )
        token = payload.get("token")
        expires_at = payload.get("expires_at")
        if not token or not expires_at:
            raise RuntimeError(
                f"GitHub API did not return token/expires_at for installation {installation_id}"
            )

        expires_at_epoch = datetime.fromisoformat(
            expires_at.replace("Z", "+00:00")
        ).astimezone(timezone.utc).timestamp()
        self.tokens_by_installation[installation_id] = InstallationToken(
            token=token,
            expires_at_epoch=expires_at_epoch,
        )
        logger.info(
            "Minted GitHub App installation token for installation %s; expires at %s",
            installation_id,
            expires_at,
        )
        return token

    def github_env(self, owner_repo: str, env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        token = self.get_installation_token(owner_repo)
        merged_env = dict(os.environ)
        if env:
            merged_env.update(env)
        merged_env["GH_TOKEN"] = token
        merged_env["GITHUB_TOKEN"] = token
        merged_env["GH_PROMPT_DISABLED"] = "1"
        merged_env["GIT_TERMINAL_PROMPT"] = "0"
        if self.github_host != "github.com":
            merged_env["GH_HOST"] = self.github_host
            merged_env["GH_ENTERPRISE_TOKEN"] = token
        return merged_env

    def repo_https_url(self, owner_repo: str) -> str:
        return f"{self.github_base_url}/{owner_repo}.git"

    def git_http_auth_header(self, token: str) -> str:
        basic_credentials = base64.b64encode(
            f"x-access-token:{token}".encode("utf-8")
        ).decode("ascii")
        return f"AUTHORIZATION: basic {basic_credentials}"

    def authenticated_git_command(
        self,
        command: Sequence[str],
        owner_repo: str,
        *,
        repo_url: Optional[str] = None,
        repo_path: Optional[Path] = None,
    ) -> list[str]:
        if not _git_command_needs_remote_auth(command):
            return list(command)

        remote_url = repo_url
        if not remote_url and repo_path is not None:
            remote_url = get_remote_origin_url(repo_path)

        if remote_url and _is_ssh_remote_url(remote_url):
            return list(command)

        token = self.get_installation_token(owner_repo)
        authenticated_command: list[str] = [
            "git",
            "-c",
            "credential.helper=",
            "-c",
            f"http.extraheader={self.git_http_auth_header(token)}",
        ]

        if len(command) > 1 and command[1] == "clone":
            clone_command = list(command)
            if len(clone_command) >= 3:
                clone_command[2] = self.repo_https_url(owner_repo)
            authenticated_command.extend(clone_command[1:])
            return authenticated_command

        if remote_url:
            prefix = _remote_prefix(remote_url, owner_repo)
            if prefix and not remote_url.startswith(self.github_base_url):
                authenticated_command.extend(
                    ["-c", f"url.{self.github_base_url}/.insteadOf={prefix}"]
                )

        authenticated_command.extend(list(command[1:]))
        return authenticated_command


_github_app_auth: Optional[GitHubAppAuth] = None
_github_app_auth_initialized = False


def initialize_github_auth() -> Optional[GitHubAppAuth]:
    global _github_app_auth, _github_app_auth_initialized
    if _github_app_auth_initialized:
        return _github_app_auth

    app_id = os.getenv("APP_ID", "").strip()
    private_key_path = os.getenv("PRIVATE_KEY_PATH", "").strip()

    if not app_id and not private_key_path:
        logger.info("GitHub App auth not configured; using existing git/gh authentication")
        _github_app_auth_initialized = True
        return None

    if not app_id or not private_key_path:
        raise RuntimeError("APP_ID and PRIVATE_KEY_PATH must both be set to enable GitHub App auth")

    _github_app_auth = GitHubAppAuth(
        app_id=app_id,
        private_key_path=private_key_path,
        github_base_url=os.getenv("GITHUB_BASE_URL", DEFAULT_GITHUB_BASE_URL),
        github_api_url=os.getenv("GITHUB_API", "").strip() or None,
        installation_id=os.getenv("INSTALLATION_ID", "").strip() or None,
    )
    _github_app_auth_initialized = True
    logger.info("GitHub App auth enabled; installation tokens will be minted and refreshed on demand")
    return _github_app_auth


def run_gh_command(command: Sequence[str], owner_repo: str, **kwargs) -> subprocess.CompletedProcess:
    auth = initialize_github_auth()
    env = kwargs.pop("env", None)
    if auth:
        env = auth.github_env(owner_repo, env)
    return subprocess.run(list(command), env=env, **kwargs)


def run_git_command(
    command: Sequence[str],
    *,
    repo_url: Optional[str] = None,
    repo_path: Optional[Path] = None,
    owner_repo: Optional[str] = None,
    **kwargs,
) -> subprocess.CompletedProcess:
    auth = initialize_github_auth()
    env = kwargs.pop("env", None)
    final_command = list(command)

    if auth:
        resolved_owner_repo = owner_repo
        if not resolved_owner_repo and repo_url:
            resolved_owner_repo = extract_owner_repo_from_remote_url(repo_url)
        if not resolved_owner_repo and repo_path is not None:
            remote_url = get_remote_origin_url(repo_path)
            if remote_url:
                resolved_owner_repo = extract_owner_repo_from_remote_url(remote_url)
        if resolved_owner_repo:
            env = auth.github_env(resolved_owner_repo, env)
            final_command = auth.authenticated_git_command(
                final_command,
                resolved_owner_repo,
                repo_url=repo_url,
                repo_path=repo_path,
            )

    return subprocess.run(final_command, env=env, **kwargs)
