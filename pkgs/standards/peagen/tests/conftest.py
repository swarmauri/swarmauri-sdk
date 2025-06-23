import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "infra: infrastructure tests requiring external services",
    )
    config.addinivalue_line(
        "markers",
        "chaos: chaos tests targeting the remote gateway",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    markexpr = getattr(config.option, "markexpr", "")
    if "infra" not in markexpr:
        skip_infra = pytest.mark.skip(reason="skip infra tests (use -m infra to run)")
        for item in items:
            if "infra" in item.keywords:
                item.add_marker(skip_infra)
    if "chaos" not in markexpr:
        skip_chaos = pytest.mark.skip(reason="skip chaos tests (use -m chaos to run)")
        for item in items:
            if "chaos" in item.keywords:
                item.add_marker(skip_chaos)
