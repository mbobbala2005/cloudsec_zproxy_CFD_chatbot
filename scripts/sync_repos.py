#!/usr/bin/env python3
"""
Clone or fast-forward the local BAP repos used by this workspace.
"""

from __future__ import annotations

import argparse
import logging
import os
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from github_auth import extract_owner_repo_from_remote_url, get_remote_origin_url, run_git_command

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class RepoSpec:
    env_var: str
    owner_repo: str
    dirname: str


REPO_SPECS: tuple[RepoSpec, ...] = (
    RepoSpec("NIDZ_API_REPO_PATH", "cisco-sbg/cloudsec_zproxy_nidz_api", "cloudsec_zproxy_nidz_api"),
    RepoSpec("AUTH_BROKER_REPO_PATH", "cisco-sbg/cloudsec_zproxy_auth", "cloudsec_zproxy_auth"),
    RepoSpec("ENVOY_REPO_PATH", "cisco-sbg/cloudsec_zproxy_envoy_zproxy", "cloudsec_zproxy_envoy_zproxy"),
    RepoSpec("ENVOY_CONTROLLER_REPO_PATH", "cisco-sbg/cloudsec_zproxy_envoy_controller", "cloudsec_zproxy_envoy_controller"),
    RepoSpec("POLICY_BROKER_REPO_PATH", "cisco-sbg/cloudsec_zproxy_policy_broker", "cloudsec_zproxy_policy_broker"),
    RepoSpec("POLICY_GEN_REPO_PATH", "cisco-sbg/cloudsec_zproxy_policy_gen", "cloudsec_zproxy_policy_gen"),
    RepoSpec("GUACD_REPO_PATH", "cisco-sbg/cloudsec_zproxy_guacd", "cloudsec_zproxy_guacd"),
    RepoSpec("GUACAMOLE_LITE_REPO_PATH", "cisco-sbg/cloudsec_zproxy_guacamole_lite", "cloudsec_zproxy_guacamole_lite"),
    RepoSpec("TERRAFORM_REPO_PATH", "cisco-sbg/cloudsec_zproxy_terraform", "cloudsec_zproxy_terraform"),
    RepoSpec("OPS_REPO_PATH", "cisco-sbg/cloudsec_zproxy_ops", "cloudsec_zproxy_ops"),
    RepoSpec("RELEASE_INFO_REPO_PATH", "cisco-sbg/cloudsec_zproxy_release_info", "cloudsec_zproxy_release_info"),
)


def repo_path_for_spec(spec: RepoSpec) -> Path:
    explicit = os.getenv(spec.env_var, "").strip()
    if explicit:
        return Path(explicit).expanduser()

    repo_base_dir = os.getenv("REPO_BASE_DIR", "").strip()
    if not repo_base_dir:
        raise RuntimeError(
            f"{spec.env_var} is not set and REPO_BASE_DIR is unavailable; cannot resolve repo path"
        )
    return Path(repo_base_dir).expanduser() / spec.dirname


def run_checked(command: Sequence[str], *, repo_path: Path | None, owner_repo: str, cwd: Path | None = None) -> str:
    LOGGER.info("$ %s", " ".join(shlex.quote(part) for part in command))
    result = run_git_command(
        command,
        repo_path=repo_path,
        owner_repo=owner_repo,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    if result.stderr.strip():
        LOGGER.debug(result.stderr.strip())
    return result.stdout.strip()


def ensure_clean_worktree(repo_path: Path, owner_repo: str) -> None:
    status = run_checked(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        repo_path=repo_path,
        owner_repo=owner_repo,
        cwd=repo_path,
    )
    if status:
        raise RuntimeError(
            f"Refusing to sync {repo_path}: local tracked changes are present.\n{status}"
        )


def ensure_expected_remote(repo_path: Path, owner_repo: str) -> None:
    remote_url = get_remote_origin_url(repo_path)
    if not remote_url:
        raise RuntimeError(f"{repo_path} has no origin remote configured")
    actual_owner_repo = extract_owner_repo_from_remote_url(remote_url)
    if actual_owner_repo and actual_owner_repo != owner_repo:
        raise RuntimeError(
            f"{repo_path} points at {actual_owner_repo}, expected {owner_repo}"
        )


def clone_repo(repo_path: Path, owner_repo: str) -> None:
    repo_path.parent.mkdir(parents=True, exist_ok=True)
    repo_url = f"https://github.com/{owner_repo}.git"
    run_checked(
        ["git", "clone", repo_url, str(repo_path)],
        repo_path=None,
        owner_repo=owner_repo,
        cwd=repo_path.parent,
    )


def sync_existing_repo(repo_path: Path, owner_repo: str) -> None:
    ensure_expected_remote(repo_path, owner_repo)
    ensure_clean_worktree(repo_path, owner_repo)
    run_checked(
        ["git", "fetch", "--all", "--prune", "--tags"],
        repo_path=repo_path,
        owner_repo=owner_repo,
        cwd=repo_path,
    )
    run_checked(
        ["git", "pull", "--ff-only"],
        repo_path=repo_path,
        owner_repo=owner_repo,
        cwd=repo_path,
    )


def sync_repo(spec: RepoSpec) -> None:
    repo_path = repo_path_for_spec(spec)
    LOGGER.info("Preparing %s at %s", spec.owner_repo, repo_path)

    if not repo_path.exists():
        clone_repo(repo_path, spec.owner_repo)
        return

    if not (repo_path / ".git").exists():
        raise RuntimeError(f"{repo_path} exists but is not a git repository")

    sync_existing_repo(repo_path, spec.owner_repo)


def resolve_specs(selected: Sequence[str]) -> list[RepoSpec]:
    if not selected:
        return list(REPO_SPECS)

    by_env = {spec.env_var: spec for spec in REPO_SPECS}
    resolved: list[RepoSpec] = []
    for item in selected:
        if item in by_env:
            resolved.append(by_env[item])
            continue
        matches = [spec for spec in REPO_SPECS if spec.owner_repo == item]
        if matches:
            resolved.extend(matches)
            continue
        raise RuntimeError(f"Unknown repo selector: {item}")
    return resolved


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clone or fast-forward the repos used by this workspace.")
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        help="Repo env var or owner/repo to sync. Repeat for multiple repos. Defaults to all configured repos.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the known repo selectors and exit.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python logging level. Default: INFO",
    )
    return parser.parse_args(argv)


def list_specs(specs: Iterable[RepoSpec]) -> int:
    for spec in specs:
        print(f"{spec.env_var}\t{spec.owner_repo}\t{spec.dirname}")
    return 0


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(message)s")

    if args.list:
        return list_specs(REPO_SPECS)

    specs = resolve_specs(args.repo)
    for spec in specs:
        sync_repo(spec)
    LOGGER.info("Repository sync complete for %d repo(s)", len(specs))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        LOGGER.error(str(exc))
        raise SystemExit(1)
