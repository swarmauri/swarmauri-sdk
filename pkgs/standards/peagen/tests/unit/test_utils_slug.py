import pytest
from peagen._utils.slug_utils import slugify, repo_slug


@pytest.mark.unit
def test_slugify_simple():
    assert slugify("My Project") == "my-project"
    assert slugify("Hello_World") == "hello_world"
    assert slugify("Some@Project!") == "some-project"


@pytest.mark.unit
def test_repo_slug_parses_refs():
    assert repo_slug("gh://org/repo") == "org-repo"
    assert repo_slug("git+https://github.com/org/repo.git@main") == "org-repo"
