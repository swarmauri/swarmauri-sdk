import pytest
from peagen._graph import (
    _build_forward_graph,
    _build_reverse_graph,
    _get_transitive_dependencies,
    _topological_sort,
    _transitive_dependency_sort,
)


@pytest.mark.r8n
class TestGraph:
    @pytest.fixture
    def simple_payload(self):
        """A simple payload with clear dependency structure"""
        return [
            {
                "RENDERED_FILE_NAME": "file1.py",
                "EXTRAS": {"DEPENDENCIES": ["file2.py", "file3.py"]},
            },
            {
                "RENDERED_FILE_NAME": "file2.py",
                "EXTRAS": {"DEPENDENCIES": ["file3.py"]},
            },
            {"RENDERED_FILE_NAME": "file3.py", "EXTRAS": {}},
        ]

    @pytest.fixture
    def complex_payload(self):
        """A more complex payload with multiple paths"""
        return [
            {
                "RENDERED_FILE_NAME": "app.py",
                "EXTRAS": {"DEPENDENCIES": ["utils.py", "config.py"]},
            },
            {
                "RENDERED_FILE_NAME": "utils.py",
                "EXTRAS": {"DEPENDENCIES": ["helpers.py"]},
            },
            {
                "RENDERED_FILE_NAME": "config.py",
                "EXTRAS": {"DEPENDENCIES": ["constants.py"]},
            },
            {
                "RENDERED_FILE_NAME": "helpers.py",
                "EXTRAS": {"DEPENDENCIES": ["constants.py"]},
            },
            {"RENDERED_FILE_NAME": "constants.py", "EXTRAS": {}},
        ]

    @pytest.fixture
    def cyclic_payload(self):
        """A payload with cyclic dependencies"""
        return [
            {
                "RENDERED_FILE_NAME": "cyclic1.py",
                "EXTRAS": {"DEPENDENCIES": ["cyclic2.py"]},
            },
            {
                "RENDERED_FILE_NAME": "cyclic2.py",
                "EXTRAS": {"DEPENDENCIES": ["cyclic3.py"]},
            },
            {
                "RENDERED_FILE_NAME": "cyclic3.py",
                "EXTRAS": {"DEPENDENCIES": ["cyclic1.py"]},
            },
        ]

    def test_build_forward_graph_simple(self, simple_payload):
        """Test building a forward graph with simple dependencies"""
        forward_graph, in_degree, all_nodes = _build_forward_graph(simple_payload)

        # Check graph structure
        assert forward_graph["file3.py"] == ["file1.py", "file2.py"]
        assert forward_graph["file2.py"] == ["file1.py"]
        assert forward_graph["file1.py"] == []

        # Check in-degree
        assert in_degree["file1.py"] == 2
        assert in_degree["file2.py"] == 1
        assert in_degree["file3.py"] == 0

        # Check all nodes
        assert all_nodes == {"file1.py", "file2.py", "file3.py"}

    def test_build_forward_graph_with_missing_extras(self):
        """Test that a payload entry with no EXTRAS still works"""
        payload = [
            {"RENDERED_FILE_NAME": "file1.py"},
            {
                "RENDERED_FILE_NAME": "file2.py",
                "EXTRAS": {"DEPENDENCIES": ["file1.py"]},
            },
        ]

        forward_graph, in_degree, all_nodes = _build_forward_graph(payload)

        assert forward_graph["file1.py"] == ["file2.py"]
        assert forward_graph["file2.py"] == []
        assert in_degree["file1.py"] == 0
        assert in_degree["file2.py"] == 1
        assert all_nodes == {"file1.py", "file2.py"}

    def test_build_forward_graph_with_missing_deps(self):
        """Test that dependencies that aren't in the payload are ignored"""
        payload = [
            {
                "RENDERED_FILE_NAME": "file1.py",
                "EXTRAS": {"DEPENDENCIES": ["missing.py"]},
            },
            {
                "RENDERED_FILE_NAME": "file2.py",
                "EXTRAS": {"DEPENDENCIES": ["file1.py"]},
            },
        ]

        forward_graph, in_degree, all_nodes = _build_forward_graph(payload)

        assert forward_graph["file1.py"] == ["file2.py"]
        assert forward_graph["file2.py"] == []
        assert "missing.py" not in forward_graph
        assert in_degree["file1.py"] == 0
        assert in_degree["file2.py"] == 1

    def test_build_reverse_graph(self):
        """Test building a reverse graph from a forward graph"""
        forward_graph = {
            "file1.py": ["file2.py", "file3.py"],
            "file2.py": [],
            "file3.py": [],
        }

        reverse_graph = _build_reverse_graph(forward_graph)

        assert reverse_graph["file1.py"] == []
        assert reverse_graph["file2.py"] == ["file1.py"]
        assert reverse_graph["file3.py"] == ["file1.py"]

    def test_topological_sort_simple(self, simple_payload):
        """Test topological sorting with a simple acyclic graph"""
        sorted_entries = _topological_sort(simple_payload)

        # Check that the order respects dependencies
        sorted_names = [entry["RENDERED_FILE_NAME"] for entry in sorted_entries]

        # file3.py should come first, as it has no dependencies
        assert sorted_names[0] == "file3.py"

        # file2.py depends on file3.py, so file3.py should come before file2.py
        assert sorted_names.index("file3.py") < sorted_names.index("file2.py")

        # file1.py depends on both file2.py and file3.py, so it should come last
        assert sorted_names.index("file2.py") < sorted_names.index("file1.py")
        assert sorted_names.index("file3.py") < sorted_names.index("file1.py")

    def test_topological_sort_complex(self, complex_payload):
        """Test topological sorting with a complex dependency graph"""
        sorted_entries = _topological_sort(complex_payload)
        sorted_names = [entry["RENDERED_FILE_NAME"] for entry in sorted_entries]

        # constants.py has no dependencies, should come first
        assert sorted_names[0] == "constants.py"

        # helpers.py depends on constants.py
        assert sorted_names.index("constants.py") < sorted_names.index("helpers.py")

        # utils.py depends on helpers.py
        assert sorted_names.index("helpers.py") < sorted_names.index("utils.py")

        # config.py depends on constants.py
        assert sorted_names.index("constants.py") < sorted_names.index("config.py")

        # app.py depends on utils.py and config.py
        assert sorted_names.index("utils.py") < sorted_names.index("app.py")
        assert sorted_names.index("config.py") < sorted_names.index("app.py")

    def test_topological_sort_cyclic(self, cyclic_payload):
        """Test that topological sort raises an exception for cyclic dependencies"""
        with pytest.raises(Exception) as excinfo:
            _topological_sort(cyclic_payload)

        assert "Cyclic or missing dependencies" in str(excinfo.value)

    def test_topological_sort_alphabetical_tiebreaking(self):
        """Test that topological sort breaks ties alphabetically"""
        payload = [
            {"RENDERED_FILE_NAME": "c.py", "EXTRAS": {}},
            {"RENDERED_FILE_NAME": "b.py", "EXTRAS": {}},
            {"RENDERED_FILE_NAME": "a.py", "EXTRAS": {}},
        ]

        sorted_entries = _topological_sort(payload)
        sorted_names = [entry["RENDERED_FILE_NAME"] for entry in sorted_entries]

        # With no dependencies, files should be sorted alphabetically
        assert sorted_names == ["a.py", "b.py", "c.py"]

    def test_get_transitive_dependencies(self):
        """Test finding transitive dependencies"""
        reverse_graph = {
            "app.py": ["utils.py", "config.py"],
            "utils.py": ["helpers.py"],
            "config.py": ["constants.py"],
            "helpers.py": ["constants.py"],
            "constants.py": [],
        }

        # Find all dependencies of app.py
        deps = _get_transitive_dependencies("app.py", reverse_graph)
        expected = {"app.py", "utils.py", "config.py", "helpers.py", "constants.py"}
        assert deps == expected

        # Find all dependencies of utils.py
        deps = _get_transitive_dependencies("utils.py", reverse_graph)
        expected = {"utils.py", "helpers.py", "constants.py"}
        assert deps == expected

        # Find all dependencies of constants.py
        deps = _get_transitive_dependencies("constants.py", reverse_graph)
        expected = {"constants.py"}
        assert deps == expected

    def test_transitive_dependency_sort(self, complex_payload):
        """Test sorting transitive dependencies for a specific file"""
        # Sort dependencies for app.py
        sorted_deps = _transitive_dependency_sort(complex_payload, "app.py")
        sorted_names = [entry["RENDERED_FILE_NAME"] for entry in sorted_deps]

        # Should include all files in correct order
        assert len(sorted_names) == 5
        assert sorted_names[0] == "constants.py"  # No dependencies
        # Both helpers.py and config.py depend on constants.py
        assert "helpers.py" in sorted_names[1:3]
        assert "config.py" in sorted_names[1:3]
        assert sorted_names[3] == "utils.py"  # Depends on helpers.py
        assert sorted_names[4] == "app.py"  # Depends on utils.py and config.py

        # Sort dependencies for utils.py
        sorted_deps = _transitive_dependency_sort(complex_payload, "utils.py")
        sorted_names = [entry["RENDERED_FILE_NAME"] for entry in sorted_deps]

        # Should include only utils.py, helpers.py, and constants.py
        assert len(sorted_names) == 3
        assert sorted_names[0] == "constants.py"
        assert sorted_names[1] == "helpers.py"
        assert sorted_names[2] == "utils.py"

    def test_transitive_dependency_sort_missing_file(self, complex_payload):
        """Test error handling for non-existent target file"""
        with pytest.raises(ValueError) as excinfo:
            _transitive_dependency_sort(complex_payload, "missing.py")

        assert "not found in payload" in str(excinfo.value)
