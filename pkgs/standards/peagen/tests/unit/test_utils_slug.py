import pytest
from peagen._utils.slug_utils import slugify


@pytest.mark.unit
def test_slugify_simple():
    assert slugify("My Project") == "my-project"
    assert slugify("Hello_World") == "hello_world"
    assert slugify("Some@Project!") == "some-project"
