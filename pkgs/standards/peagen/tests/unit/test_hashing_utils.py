import pytest
from pathlib import Path

from peagen.utils import hashing
from peagen.utils.hashing import _yaml_file_digest


@pytest.mark.unit
def test_design_and_plan_hash(tmp_path: Path) -> None:
    text = "a: 1\nb: 2\n"
    design = tmp_path / "design.yaml"
    plan = tmp_path / "plan.yaml"
    design.write_text(text, encoding="utf-8")
    plan.write_text(text, encoding="utf-8")
    expected = "43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777"
    assert hashing.design_hash(design) == expected
    assert hashing.plan_hash(plan) == expected


@pytest.mark.unit
def test_yaml_file_digest(tmp_path: Path) -> None:
    text = "foo: 3\nbar: 4\n"
    path = tmp_path / "file.yaml"
    path.write_text(text, encoding="utf-8")
    expected = hashing.design_hash(path)
    assert _yaml_file_digest(path) == expected


@pytest.mark.unit
def test_payload_hash() -> None:
    data = {"foo": "bar", "num": 1}
    assert (
        hashing.payload_hash(data)
        == "1159feb256de4d1d5a7fac1e031195f8ab6374e35efd9e9b830e353df0d84fa7"
    )


@pytest.mark.unit
def test_revision_and_edge_hashes() -> None:
    payload_h = "deadbeef"
    rev_no_parent = hashing.revision_hash(None, payload_h)
    assert rev_no_parent == "32c0f7b422237f274057f406117892bdf34d9d2346064989ebe0c5d109b9ec4f"
    rev_with_parent = hashing.revision_hash("abc", payload_h)
    assert rev_with_parent == "eb93c4bf3f294dce1ecd0d1c849bc05dcb235b42c5d184bea54b6085264caa4c"

    edge1 = hashing.edge_hash("rev1", "child1", "op", None)
    assert edge1 == "f47042d1ce66c280e2cf1dd882267777634bdcdab567960952ea9b1f2db6a186"
    edge2 = hashing.edge_hash("rev1", "child1", "op", "dev")
    assert edge2 == "c0a6ba0c9464f9bda7a63e95bdbb21bc88a3ba03a7bcf0cc1daa0bb8c2c7eeda"

    fan = hashing.fanout_root_hash([edge2, edge1])
    assert fan == "2471e2af92d6ee0aa7faa4c1480e335703bd33b0b39202918c916b0df93b16fe"


@pytest.mark.unit
def test_artefact_and_status_hash() -> None:
    assert (
        hashing.artefact_cid(b"hello")
        == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )
    status = hashing.status_hash(
        "abc",
        "OK",
        "2023-01-01T00:00:00Z",
    )
    assert status == "106ca506c299196dd938be65d162753f47f1a3f342bdefdcb3e2b7fc23363a54"
