import random; random.seed(0xA11A)
import builtins
import types
import pytest

from peagen._external import chunk_content


@pytest.mark.unit
def test_chunk_multiple(monkeypatch):
    class FakeChunker:
        def chunk_text(self, text):
            return [(None, None, "c1"), (None, None, "c2")]

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "swarmauri.chunkers.MdSnippetChunker":
            return types.SimpleNamespace(MdSnippetChunker=FakeChunker)
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        assert chunk_content("x") == "c1"
    finally:
        monkeypatch.setattr(builtins, "__import__", real_import)


@pytest.mark.unit
def test_chunk_no_chunker(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "swarmauri.chunkers.MdSnippetChunker":
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        assert chunk_content("foo") == "foo"
    finally:
        monkeypatch.setattr(builtins, "__import__", real_import)
