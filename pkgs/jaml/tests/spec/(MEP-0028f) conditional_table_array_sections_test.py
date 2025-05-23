import pytest

from jaml import round_trip_loads


# @pytest.mark.xfail(reason="pending validation")
@pytest.mark.spec
@pytest.mark.mep0028f
def test_section_headers_with_clauses():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """

    # The input JML content (as a multi-line string)
    JML_INPUT = r"""
    rootDir = "src"

    [[f"file.{package.name}.{module.name}.source"
for package in ${packages} if package.active
for module in package.modules if package.active]]"""

    # The base external context used during rendering.
    BASE_CONTEXT = {
        "env": "prod",
        "packages": [
            {
                "name": "auth",
                "active": True,
                "modules": [
                    {
                        "name": "login",
                        "enabled": True,
                        "isTest": True,
                        "extras": {"owner": "teamA", "secret": "xyz"},
                        "tests": ["test_v2_login", "test_v2_auth"],
                    },
                    {
                        "name": "signup",
                        "enabled": True,
                        "isTest": False,
                        "extras": {"owner": "teamB"},
                    },
                ],
            }
        ],
    }

    data = round_trip_loads(JML_INPUT)
    print("\n\n[TEST DEBUG]:")
    print(data, "\n\n")
    assert data["rootDir"] == '"src"'

    data["rootDir"] = '"new_src"'
    resolved_config = data.resolve()
    assert resolved_config["rootDir"] == "new_src"
    assert (
        """f"file.{package.name}.{module.name}.source"
for package in ${packages} if package.active
for module in package.modules if package.active"""
        in data
    )

    # out = data.dumps()
    # rendered_data = data.render(out, context=BASE_CONTEXT)
    rendered_data = data.render(context=BASE_CONTEXT)
    print("\n\n\n\n[RENDERED DATA]:")
    print(rendered_data)
    assert rendered_data["rootDir"] == "new_src"
    assert rendered_data["file"]
    assert rendered_data["file"]["auth"]["login"]
    assert rendered_data["file"]["auth"]["signup"]
    assert (
        """f"file.{package.name}.{module.name}.source"
for package in ${packages} if package.active
for module in package.modules if package.active"""
        not in rendered_data
    )

    final_out = data.dumps()
    print("\n\n\n\n[FINAL_OUT]:")
    print(final_out)
    assert "[[file.auth.signup.source]]" in final_out
