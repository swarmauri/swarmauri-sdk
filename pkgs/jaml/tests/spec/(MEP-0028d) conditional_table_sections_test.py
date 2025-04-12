import pytest
from copy import deepcopy

from jaml import (
    round_trip_loads,
    round_trip_dumps,
    resolve,
    render,
)

# The input JML content (as a multi-line string)
JML_INPUT = r'''
rootDir = "src"
packages = ${packages}

[f"file.{package.name}.{module.name}.source" 
  for package as %{package} in @{packages} if package.active
  for module as %{module} in @{package.modules} if module.enabled]
name = %{module.name} + ".py"
path = @{rootDir} + "/" + %{package.name} + "/" + %{name}
type = "python"
test_conf = { testFramework = "pytest", tests = %{module.tests} }

'''

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

expected_result = r'''
[file.auth.login.source]
name = "login.py"
path = "src/auth/login.py"
type = "python"
test_conf = { "testFramework" = "pytest", "tests" = ["test_v2_login", "test_v2_auth"] }

[file.auth.signup.source]
name = "signup.py"
path = "src/auth/signup.py"
type = "python"
test_conf = { "testFramework" = "pytest", "tests" = ["test_v2_source", "test_v2_auth"] }

'''

# @pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028d
def test_v2_round_trip_loads_valid():
    """
    Validate that the round_trip_loads API correctly parses the JML content into an AST.
    """
    ast = round_trip_loads(JML_INPUT)
    # Assuming that the AST is a dict-like structure and should contain a 'rootDir' key.
    assert isinstance(ast, dict), "The AST should be a dictionary."
    assert "rootDir" in ast, "AST should contain 'rootDir' key."
    

# @pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028d
def test_v2_update_root_dir():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    print('\n\n[TEST DEBUG]:')
    print(data,'\n\n')
    assert data["rootDir"] == "src"

    data["rootDir"].origin = '"new_src"'
    resolved_config = resolve(data)
    assert resolved_config["rootDir"] == '"new_src"'

    out = round_trip_dumps(data)
    rendered_data = render(out, context=BASE_CONTEXT)
    final_out = round_trip_dumps(rendered_data)

    print('\n\n\n\n[FINAL_OUT]:')
    print(final_out)    
    assert rendered_data["rootDir"] == "new_src"
    assert "src/auth" in final_out


@pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028d
def test_v2_update_context_env():
    """
    Validate that updating the external context (env from 'prod' to 'dev')
    causes the config file's environment to be updated in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    assert data["rootDir"] == "src"
    
    data["rootDir"].origin = '"new_src"'
    resolved_config = resolve(data)
    assert resolved_config["rootDir"] == '"new_src"'

    out = round_trip_dumps(data)
    new_context = dict(BASE_CONTEXT)
    new_context["env"] = "dev"
    rendered_data = render(out, context=new_context)
    assert rendered_data["rootDir"] == "new_src"

    final_out = round_trip_dumps(rendered_data)
    assert '"env" = "dev"' in final_out

@pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028d
def test_v2_update_module_extras():
    """
    Validate that updating a module's 'extras' (changing the owner for the login module)
    is reflected in the rendered output.
    """
    print('-'*10, '\n[TEST]: STARTING RT LOAD\n')

    data = round_trip_loads(JML_INPUT)
    print('-'*10, '\n[TEST]: STARTING FIRST DUMP\n')
    round_trip_dumps(data)


    print('-'*10, f'\n[TEST]: \n{data}\n')
    assert data["rootDir"] == "src"
    print('\n\n\n', data["rootDir"], type(data["rootDir"]), '\n\n')

    print('-'*10, '\n[TEST]: STARTING RESOLUTION\n')
    
    data["rootDir"].origin = '"new_src"'
    resolved_config = resolve(data)
    assert resolved_config["rootDir"] == '"new_src"'

    # Update the context to change the owner in the login module from "teamA" to "teamX".
    new_context = deepcopy(BASE_CONTEXT)
    new_context["packages"][0]["modules"][0]["extras"]["owner"] = "teamX"

    print('-'*10, '\n[TEST]: STARTING SECOND DUMP\n')
    out = round_trip_dumps(data)
    print('\n\n\n\n[DUMP]:', out,'\n\n---\n\n\n')
    print('-'*10, '\n[TEST]: STARTING RENDER\n')
    rendered_data = render(out, context=new_context)
    assert rendered_data["rootDir"] == "new_src"

    print('-'*10, '\n[TEST]: STARTING FINAL DUMP\n')
    final_out = round_trip_dumps(rendered_data)
    print('\n\n\n\n[FINAL DUMP]:', final_out,'\n\n---\n\n\n')

    assert final_out == expected_result

    assert """[[file.auth.signup.config]]
name = "signup.yaml"
path = "src/auth/config/signup.yaml"
type = "yaml"
extras = { "env" = "prod" }""" in final_out

    assert '"env" = "dev"' in final_out
    assert '"owner" = "teamX"' in final_out
