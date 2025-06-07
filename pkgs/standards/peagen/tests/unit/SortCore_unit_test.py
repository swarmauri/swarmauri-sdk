import os
from pathlib import Path

import pytest

from peagen.core.sort_core import _merge_cli_into_toml, sort_file_records


@pytest.mark.unit
def test_merge_cli_into_toml(tmp_path):
    toml_path = tmp_path / ".peagen.toml"
    toml_path.write_text("template_paths = []\n")
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        params = _merge_cli_into_toml(
            projects_payload="payload.yaml",
            project_name="proj",
            start_idx=None,
            start_file=None,
            verbose=1,
            transitive=True,
            show_dependencies=False,
        )
    finally:
        os.chdir(cwd)
    assert params["cfg"]["transitive"] is True
    assert params["start_idx"] == 0
    assert params["project_name"] == "proj"
    assert params["projects_payload_path"] == "payload.yaml"


@pytest.mark.unit
def test_sort_file_records_basic():
    records = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": []}, "PROCESS_TYPE": "COPY"},
        {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}, "PROCESS_TYPE": "COPY"},
        {"RENDERED_FILE_NAME": "c", "EXTRAS": {"DEPENDENCIES": ["b"]}, "PROCESS_TYPE": "COPY"},
    ]
    sorted_records, next_idx = sort_file_records(records)
    names = [r["RENDERED_FILE_NAME"] for r in sorted_records]
    assert names == ["a", "b", "c"]
    assert next_idx == 3


@pytest.mark.unit
def test_sort_file_records_start_file_and_idx():
    records = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": []}, "PROCESS_TYPE": "COPY"},
        {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}, "PROCESS_TYPE": "COPY"},
        {"RENDERED_FILE_NAME": "c", "EXTRAS": {"DEPENDENCIES": ["b"]}, "PROCESS_TYPE": "COPY"},
    ]
    sorted_records, next_idx = sort_file_records(records, start_idx=1, start_file="b")
    names = [r["RENDERED_FILE_NAME"] for r in sorted_records]
    assert names == ["c"]
    assert next_idx == 2


@pytest.mark.unit
def test_sort_file_records_transitive():
    records = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": []}, "PROCESS_TYPE": "COPY"},
        {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}, "PROCESS_TYPE": "COPY"},
        {"RENDERED_FILE_NAME": "c", "EXTRAS": {"DEPENDENCIES": ["b"]}, "PROCESS_TYPE": "COPY"},
    ]
    sorted_records, next_idx = sort_file_records(records, start_file="c", transitive=True)
    names = [r["RENDERED_FILE_NAME"] for r in sorted_records]
    assert names == ["a", "b", "c"]
    assert next_idx == 3
