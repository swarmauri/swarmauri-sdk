import subprocess
from pathlib import Path

import pytest

from swarmauri_vectorstore_git import GitVectorStore


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout.strip()


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "user.email", "test@example.com")

    (repo / "app.txt").write_text("bootstrap\n", encoding="utf-8")
    git(repo, "add", "app.txt")
    git(repo, "commit", "-m", "bootstrap project")

    (repo / "app.txt").write_text("bootstrap\nauth token\n", encoding="utf-8")
    git(repo, "add", "app.txt")
    git(repo, "commit", "-m", "fix auth token flow")

    git(repo, "checkout", "-b", "feature/logging")
    (repo / "logging.txt").write_text("memory leak traced\n", encoding="utf-8")
    git(repo, "add", "logging.txt")
    git(repo, "commit", "-m", "add logging for memory leak")
    feature_commit = git(repo, "rev-parse", "HEAD")

    git(repo, "checkout", "main")
    git(repo, "tag", "v1.0.0")
    (repo / "main.txt").write_text("head only branch work\n", encoding="utf-8")
    git(repo, "add", "main.txt")
    git(repo, "commit", "-m", "ship mainline update")

    assert feature_commit
    return repo


@pytest.mark.unit
def test_head_scope_indexes_only_head_history(sample_repo: Path):
    store = GitVectorStore(repo_path=sample_repo.as_posix(), scope="head", document_kinds=("commit",))
    store.build_index()
    subjects = {document.metadata["subject"] for document in store.documents}

    assert "ship mainline update" in subjects
    assert "fix auth token flow" in subjects
    assert "add logging for memory leak" not in subjects


@pytest.mark.unit
def test_ref_scope_indexes_specific_branch(sample_repo: Path):
    store = GitVectorStore(
        repo_path=sample_repo.as_posix(),
        scope="ref",
        ref="feature/logging",
        document_kinds=("commit",),
    )
    store.build_index()
    subjects = {document.metadata["subject"] for document in store.documents}

    assert "add logging for memory leak" in subjects
    assert "ship mainline update" not in subjects


@pytest.mark.unit
def test_all_refs_scope_includes_feature_branch(sample_repo: Path):
    store = GitVectorStore(
        repo_path=sample_repo.as_posix(),
        scope="all_refs",
        document_kinds=("commit", "log"),
    )
    store.build_index()
    subjects = [document.metadata["subject"] for document in store.documents]

    assert "add logging for memory leak" in subjects
    assert len(store.documents) >= 8


@pytest.mark.unit
def test_retrieve_returns_relevant_git_documents(sample_repo: Path):
    store = GitVectorStore(
        repo_path=sample_repo.as_posix(),
        scope="all_refs",
        document_kinds=("commit",),
    )
    store.build_index()

    results = store.retrieve("auth token bug", top_k=2)

    assert results
    assert results[0].metadata["subject"] == "fix auth token flow"
