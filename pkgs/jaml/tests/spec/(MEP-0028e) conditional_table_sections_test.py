import pytest

from jaml import round_trip_loads

# The input JML content (as a multi-line string)
JML_INPUT = r"""
rootDir = "src"
packages = ${packages}

[f"file.{package.name}.{module.name}.source" 
  for package as %{package} in @{packages} if package.active
  for module as %{module} in package.modules if module.enabled]
name = %{module.name} + ".py"
path = @{rootDir} + "/" + %{package.name} + "/" + %{name}
type = "python"
test_conf = { testFramework = "pytest", tests = %{module.tests} }

"""

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

expected_result = r"""
rootDir = "src"
packages = {
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

[file.auth.login.source]
package = {
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
module = {
    "name": "login",
    "enabled": True,
    "isTest": True,
    "extras": {"owner": "teamA", "secret": "xyz"},
    "tests": ["test_v2_login", "test_v2_auth"],
}
name = "login.py"
path = "new_src/auth/login.py"
type = "python"
test_conf = { "testFramework" = "pytest", "tests" = ["test_v2_login", "test_v2_auth"] }

[file.auth.signup.source]
package = {
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
module =  {
    "name": "signup",
    "enabled": True,
    "isTest": False,
    "extras": {"owner": "teamB"},
}
name = "signup.py"
path = "new_src/auth/signup.py"
type = "python"
test_conf = { "testFramework" = "pytest", "tests" = ["test_v2_source", "test_v2_auth"] }

"""


@pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028e
def test_section_header_with_alias():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    print("\n\n[TEST DEBUG]:")
    print(data, "\n\n")
    assert data["rootDir"] == '"src"'

    data["rootDir"] = "new_src"
    resolved_config = data.resolve()
    assert resolved_config["rootDir"] == "new_src"

    # out = data.dumps()
    # rendered_data = data.render(out, context=BASE_CONTEXT)
    rendered_data = data.render(context=BASE_CONTEXT)
    print("\n\n\n\n[RENDERED DATA]:")
    print(rendered_data)
    assert rendered_data["rootDir"] == "new_src"

    final_out = data.dumps()
    print("\n\n\n\n[FINAL_OUT]:")
    print(final_out)
    assert "[file.auth.signup.source]" in final_out
    assert "new_src/auth" in final_out
