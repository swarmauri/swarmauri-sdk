import os
import uuid
import subprocess
from pathlib import Path

import httpx
import pytest

pytestmark = pytest.mark.e2e

GITHUB_API = "https://api.github.com"
GATEWAY_RPC = os.getenv("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")


def _repo_exists_github(slug: str, token: str) -> bool:
    res = httpx.get(
        f"{GITHUB_API}/repos/{slug}",
        headers={"Authorization": f"token {token}"},
        timeout=10,
    )
    return res.status_code == 200


def _repo_exists_shadow(base: str, slug: str, token: str) -> bool:
    res = httpx.get(
        f"{base.rstrip('/')}/api/v1/repos/{slug}",
        headers={"Authorization": f"token {token}"},
        timeout=10,
    )
    return res.status_code == 200


def _gateway_available(url: str) -> bool:
    envelope = {"jsonrpc": "2.0", "method": "Workers.list", "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code == 200


def test_remote_init_repo(tmp_path: Path) -> None:
    github_pat = os.getenv("GITHUB_PAT")
    shadow_pat = os.getenv("PEAGEN_GIT_SHADOW_PAT")
    shadow_base = os.getenv("PEAGEN_GIT_SHADOW_URL", "https://git.peagen.com")
    if not github_pat or not shadow_pat:
        pytest.skip("tokens not provided")
    if not _gateway_available(GATEWAY_RPC):
        pytest.skip("gateway not reachable")

    user_res = httpx.get(
        f"{GITHUB_API}/user",
        headers={"Authorization": f"token {github_pat}"},
        timeout=10,
    )
    user_res.raise_for_status()
    login = user_res.json()["login"]

    repo_name = f"peagen-init-test-{uuid.uuid4().hex[:8]}"
    slug = f"{login}/{repo_name}"

    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "README.md").write_text("demo repo")
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "add", "README.md"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir, check=True)

    env = os.environ.copy()
    env["GITHUB_PAT"] = github_pat
    env["PEAGEN_GIT_SHADOW_PAT"] = shadow_pat

    gh_auth_url = f"https://{github_pat}@github.com/{slug}.git"
    subprocess.run(
        [
            "peagen",
            "local",
            "init",
            "repo",
            slug,
            "--pat",
            github_pat,
            "--path",
            ".",
            "--origin",
            gh_auth_url,
            "--upstream",
            gh_auth_url,
        ],
        cwd=repo_dir,
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "peagen",
            "remote",
            "init",
            "repo",
            slug,
            "--url",
            f"https://github.com/{slug}",
        ],
        cwd=repo_dir,
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert _repo_exists_github(slug, github_pat)
    assert _repo_exists_shadow(shadow_base, slug, shadow_pat)
