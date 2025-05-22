import pytest
from peagen.slug_utils import slugify

@pytest.mark.unit
class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self):
        assert slugify("C++_Project@2020") == "c-_project-2020"

    def test_trimmed(self):
        assert slugify("!!Danger!!") == "danger"
