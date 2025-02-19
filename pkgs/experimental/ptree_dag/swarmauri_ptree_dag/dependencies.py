"""
dependencies.py

This module contains functions to resolve and manage dependency expressions
for file records. It supports expanding glob/path patterns, rendering dependency
strings using a context, and querying dependency relationships from a dependency graph.
"""

import os
import glob
from typing import List, Dict, Any
from jinja2 import Environment


def resolve_glob_dependencies(dependency_field: str, base_dir: str) -> List[str]:
    """
    Examines the given dependency field (which may include glob or path expressions)
    and returns a list of file paths that match the pattern.

    Parameters:
      dependency_field (str): The dependency expression, e.g. "shared/**/*.py".
      base_dir (str): The base directory to resolve the glob pattern against.

    Returns:
      List[str]: A list of matching file paths.
    """
    pattern = os.path.join(base_dir, dependency_field)
    matches = glob.glob(pattern, recursive=True)
    return matches


def _expand_dependency_pattern(dep_pattern: str, base_dir: str) -> List[str]:
    """
    Helper method that expands a dependency pattern relative to base_dir using glob.

    Parameters:
      dep_pattern (str): The dependency pattern, e.g. "shared/**/*.py".
      base_dir (str): The base directory to resolve the pattern.

    Returns:
      List[str]: A list of file paths matching the pattern.
    """
    pattern = os.path.join(base_dir, dep_pattern)
    return glob.glob(pattern, recursive=True)


def resolve_dependency_references(dependencies: List[str], context: dict) -> List[str]:
    """
    Renders each dependency string using the provided context.
    This is useful if dependency strings contain placeholders such as "{{ PKG.NAME }}".

    Parameters:
      dependencies (List[str]): List of dependency strings with potential placeholders.
      context (dict): Context dictionary used for rendering.

    Returns:
      List[str]: List of rendered dependency strings.
    """
    env = Environment(autoescape=False)
    resolved = []
    for dep in dependencies:
        try:
            template = env.from_string(dep)
            rendered = template.render(**context)
            resolved.append(rendered)
        except Exception as e:
            # In case of rendering failure, return the original dependency string.
            resolved.append(dep)
    return resolved


def get_direct_dependencies(file_record: dict, context: dict, base_dir: str = None) -> List[str]:
    """
    Returns a list of resolved direct dependency paths for a given file record.
    It first renders any dependency strings using the provided context. If a rendered
    dependency contains glob characters, it expands the glob pattern if base_dir is provided.

    Parameters:
      file_record (dict): The file record containing a "DEPENDENCIES" field.
      context (dict): The context used to render dependency placeholders.
      base_dir (str): Optional base directory for glob resolution.

    Returns:
      List[str]: List of resolved dependency paths.
    """
    dependencies = file_record.get("DEPENDENCIES", [])
    # Render dependency strings using the context.
    resolved_deps = resolve_dependency_references(dependencies, context)
    
    final_deps = []
    for dep in resolved_deps:
        if "*" in dep or "?" in dep:
            if base_dir:
                expanded = _expand_dependency_pattern(dep, base_dir)
                final_deps.extend(expanded)
            else:
                final_deps.append(dep)
        else:
            final_deps.append(dep)
    return final_deps


def get_transitive_dependencies(file_record: dict, dependency_graph: Dict[str, List[str]]) -> List[str]:
    """
    Recursively retrieves all transitive dependencies for the given file record
    from the dependency graph.

    Parameters:
      file_record (dict): The file record (must contain a unique identifier,
                          e.g. RENDERED_FILE_NAME).
      dependency_graph (Dict[str, List[str]]): A graph mapping file identifiers
                          to lists of dependency identifiers.

    Returns:
      List[str]: A list of unique file identifiers representing all transitive dependencies.
    """
    start = file_record.get("RENDERED_FILE_NAME")
    visited = set()

    def dfs(node: str):
        if node in visited:
            return
        visited.add(node)
        for neighbor in dependency_graph.get(node, []):
            dfs(neighbor)

    dfs(start)
    visited.discard(start)
    return list(visited)


def get_dependents(file_record: dict, dependency_graph: Dict[str, List[str]]) -> List[str]:
    """
    Returns all file identifiers that depend on the given file record (reverse dependencies).

    Parameters:
      file_record (dict): The file record (identified by RENDERED_FILE_NAME).
      dependency_graph (Dict[str, List[str]]): The dependency graph.

    Returns:
      List[str]: A list of file identifiers that depend on the given file record.
    """
    target = file_record.get("RENDERED_FILE_NAME")
    dependents = []
    for node, neighbors in dependency_graph.items():
        if target in neighbors:
            dependents.append(node)
    return dependents


def filter_dependencies_by_scope(dependencies: List[str], scope: str) -> List[str]:
    """
    Filters a list of dependency paths based on the specified scope.
    The scope might be "file", "module", "package", or "project".

    Parameters:
      dependencies (List[str]): List of dependency paths.
      scope (str): The scope filter (e.g. "file", "module", "package", "project").

    Returns:
      List[str]: Filtered list of dependency paths relevant to the specified scope.
    """
    scope = scope.lower()
    filtered = []
    for dep in dependencies:
        if scope == "file":
            # For file scope, assume files have a typical extension like .py
            if dep.endswith(".py"):
                filtered.append(dep)
        elif scope == "module":
            # Module-level dependencies might include a known module marker in the path.
            if "module" in dep.lower():
                filtered.append(dep)
        elif scope == "package":
            # For package scope, we may assume fewer subdirectory levels.
            if dep.count(os.sep) < 3:
                filtered.append(dep)
        elif scope == "project":
            # For project scope, perhaps even fewer separators.
            if dep.count(os.sep) < 2:
                filtered.append(dep)
        else:
            filtered.append(dep)
    return filtered
