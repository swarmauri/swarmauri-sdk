import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "infra: infrastructure tests requiring external services",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    markexpr = getattr(config.option, "markexpr", "")
    if markexpr and "infra" in markexpr:
        return
    skip_infra = pytest.mark.skip(reason="skip infra tests (use -m infra to run)")
    for item in items:
        if "infra" in item.keywords:
            item.add_marker(skip_infra)
