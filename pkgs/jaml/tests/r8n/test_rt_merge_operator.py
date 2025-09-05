import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
def test_rt_local_merge():
    jml = """
[section]
defaults = { retries = 3, timeout = 100 }

user_settings = { <<: section.defaults, theme = "dark", retries = 5 }
    """.strip()

    # 1. Round-trip parse -> AST
    ast = round_trip_loads(jml)

    # 3. Dump the updated AST to a JML string
    dumped_str = round_trip_dumps(ast)

    # 4. Re-parse with a plain load
    data = loads(dumped_str)

    expected = {
        "section": {
            "defaults": {"retries": 3, "timeout": 100},
            "user_settings": {"retries": 5, "timeout": 100, "theme": "dark"},
        }
    }
    assert data == expected


@pytest.mark.unit
def test_rt_alias_merge():
    jml = """
[section]
defaults = { retries = 3, timeout = 100 }

user_settings = { <<: @section.defaults, theme = "dark", retries = 5 }
    """.strip()

    # 1. Round-trip parse -> AST
    ast = round_trip_loads(jml)

    # 3. Dump the updated AST to a JML string
    dumped_str = round_trip_dumps(ast)

    # 4. Re-parse with a plain load
    data = loads(dumped_str)

    expected = {
        "section": {
            "defaults": {"retries": 3, "timeout": 100},
            "user_settings": {"retries": 5, "timeout": 100, "theme": "dark"},
        }
    }
    assert data == expected
