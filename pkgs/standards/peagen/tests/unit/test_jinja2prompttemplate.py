import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from jinja2 import Environment, Template
from peagen._Jinja2PromptTemplate import Jinja2PromptTemplate, j2pt
from pydantic import FilePath


@pytest.mark.unit
class TestJinja2PromptTemplate:
    @pytest.fixture
    def template_instance(self):
        """Create a fresh template instance for each test"""
        return Jinja2PromptTemplate()

    @pytest.fixture
    def temp_template_file(self):
        """Create a temporary template file for testing"""
        with tempfile.NamedTemporaryFile(suffix=".j2", delete=False, mode="w") as f:
            f.write("Hello, {{ name }}!")
        try:
            yield f.name
        finally:
            os.unlink(f.name)

    def test_init_default(self, template_instance):
        """Test that the template initializes with default values"""
        assert template_instance.template == ""
        assert template_instance.variables == {}
        assert template_instance.templates_dir is None
        assert template_instance.type == "Jinja2PromptTemplate"

    def test_set_template_from_str(self, template_instance):
        """Test setting template from string"""
        template_str = "Hello, {{ name }}!"
        template_instance.set_template(template_str)
        assert template_instance.template == template_str

    def test_fill_with_string_template(self, template_instance):
        """Test filling a string template with variables"""
        template_instance.set_template("Hello, {{ name }}!")
        result = template_instance.fill({"name": "World"})
        assert result == "Hello, World!"

    def test_generate_prompt(self, template_instance):
        """Test the generate_prompt method"""
        template_instance.set_template("Hello, {{ name }}!")
        result = template_instance.generate_prompt({"name": "World"})
        assert result == "Hello, World!"

    def test_call_method(self, template_instance):
        """Test the __call__ method"""
        template_instance.set_template("Hello, {{ name }}!")
        result = template_instance({"name": "World"})
        assert result == "Hello, World!"

    def test_set_template_from_filepath(self, template_instance, temp_template_file):
        """Test setting template from a file path"""
        template_instance.set_template(FilePath(temp_template_file))
        assert isinstance(template_instance.template, Template)
        result = template_instance.fill({"name": "World"})
        assert result == "Hello, World!"

    def test_get_env(self, template_instance):
        """Test that get_env returns a proper Jinja2 Environment"""
        env = template_instance.get_env()
        assert isinstance(env, Environment)
        assert "split" in env.filters
        assert "make_singular" in env.filters

    def test_get_env_with_templates_dir_string(self):
        """Test get_env with string templates_dir"""
        template = Jinja2PromptTemplate(templates_dir="/tmp")
        env = template.get_env()
        assert isinstance(env, Environment)
        assert env.loader is not None
        assert "/tmp" in env.loader.searchpath

    def test_get_env_with_templates_dir_list(self):
        """Test get_env with list templates_dir"""
        template = Jinja2PromptTemplate(templates_dir=["/tmp", "/var"])
        env = template.get_env()
        assert isinstance(env, Environment)
        assert env.loader is not None
        assert "/tmp" in env.loader.searchpath
        assert "/var" in env.loader.searchpath

    def test_split_whitespace(self, template_instance):
        """Test the split_whitespace filter"""
        result = template_instance.split_whitespace("hello world")
        assert result == ["hello", "world"]

        result = template_instance.split_whitespace("hello,world", ",")
        assert result == ["hello", "world"]

    def test_split_whitespace_non_string(self, template_instance):
        """Test the split_whitespace filter with non-string input"""
        with pytest.raises(ValueError):
            template_instance.split_whitespace(123)

    @patch("inflect.engine")
    def test_make_singular(self, mock_engine, template_instance):
        """Test the make_singular filter"""
        mock_inflect = MagicMock()
        mock_engine.return_value = mock_inflect

        # Case 1: When singular_noun returns a value
        mock_inflect.singular_noun.return_value = "cat"
        result = template_instance.make_singular("cats")
        assert result == "cat"

        # Case 2: When singular_noun returns False (already singular)
        mock_inflect.singular_noun.return_value = False
        result = template_instance.make_singular("dog")
        assert result == "dog"

    def test_global_j2pt_instance(self):
        """Test that the global j2pt instance is properly initialized"""
        assert isinstance(j2pt, Jinja2PromptTemplate)
        assert j2pt.type == "Jinja2PromptTemplate"

    def test_template_with_complex_variables(self, template_instance):
        """Test template rendering with complex variables"""
        template_instance.set_template(
            "Items: {% for item in items %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}"
        )
        result = template_instance.fill({"items": ["apple", "banana", "cherry"]})
        assert result == "Items: apple, banana, cherry"

    def test_template_with_filter(self, template_instance):
        """Test template using custom filter"""
        template_instance.set_template("Words: {{ phrase|split|join('-') }}")
        result = template_instance.fill({"phrase": "hello world python"})
        assert result == "Words: hello-world-python"
