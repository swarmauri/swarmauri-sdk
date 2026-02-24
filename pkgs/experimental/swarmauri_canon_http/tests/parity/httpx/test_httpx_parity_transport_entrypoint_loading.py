import swarmauri_canon_http


def test_httpx_parity_load_registered_transports_imports_all_registered_entry_points(
    monkeypatch,
):
    loaded = []

    class FakeEntryPoint:
        def __init__(self, name: str, obj: object):
            self.name = name
            self._obj = obj

        def load(self):
            loaded.append(self.name)
            return self._obj

    fake_entry_points = [
        FakeEntryPoint("transport_one", object()),
        FakeEntryPoint("transport_two", object()),
    ]

    monkeypatch.setattr(
        swarmauri_canon_http,
        "_get_transport_entry_points",
        lambda: fake_entry_points,
    )

    loaded_transports = swarmauri_canon_http.load_registered_transports()

    assert loaded == ["transport_one", "transport_two"]
    assert set(loaded_transports) == {"transport_one", "transport_two"}
