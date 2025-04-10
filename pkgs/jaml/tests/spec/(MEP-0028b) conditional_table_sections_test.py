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
packages = $ctx.packages

[[file.{package.name}.{module.name}.source
  for package as %package in @packages if package.active
  for module as %module in package.modules if module.enabled]]
name = %module.name + ".py"
path = @rootDir + "/" + %package.name + "/" + %name
type = "python"
extras = ["k" = v for k, v in %module.extras.items if k != "secret"] else {}

[[file.{package.name}.{module.name}.test
  for package as %package in @packages if package.active
  for module as %module in package.modules if module.enabled if module.isTest]]
name = %module.name + "_test.py"
path = @rootDir + "/" + %package.name + "/tests/" + %name
type = "python"
extras = { "testFramework" = "pytest", "tests" = [%module.tests] }

[[file.{package.name}.{module.name}.readme
  for package as %package in @packages if package.active
  for module as %module in package.modules if module.enabled]]
name = "README_" + %module.name + ".md"
path = @rootDir + "/" + %package.name + "/README_" + %name
type = "markdown"
extras = ["k" = v for k, v in %module.extras.items if k in ["owner", "desc"]] else { "desc" = "Module docs" }

[[file.{package.name}.{module.name}.config
  for package as %package in @packages if package.active
  for module as %module in package.modules if module.enabled]]
name = %module.name + ".yaml"
path = @rootDir + "/" + %package.name + "/config/" + %name
type = "yaml"
extras = { "env" = $ctx.env }
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
                    "tests": ["test_login", "test_auth"],
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


@pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028
def test_round_trip_loads_valid():
    """
    Validate that the round_trip_loads API correctly parses the JML content into an AST.
    """
    ast = round_trip_loads(JML_INPUT)
    # Assuming that the AST is a dict-like structure and should contain a 'rootDir' key.
    assert isinstance(ast, dict), "The AST should be a dictionary."
    assert "rootDir" in ast, "AST should contain 'rootDir' key."
    # Optionally, ensure some structure from the file blocks is present.
    # For instance, one could check for a key related to file blocks if defined by the transformer.
    

@pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028
def test_update_root_dir():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    ast = round_trip_loads(JML_INPUT)
    # Update the rootDir value from "src" to "source"
    ast["rootDir"] = "source"
    resolved_ast = resolve(ast)
    dumped_text = round_trip_dumps(resolved_ast)
    rendered_output = render(dumped_text, context=BASE_CONTEXT)
    # Verify that the update is reflected in file paths (e.g., "source/auth" should appear instead of "src/auth")
    assert "source/auth" in rendered_output, "Updated rootDir not reflected in file paths."


@pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028
def test_update_context_env():
    """
    Validate that updating the external context (env from 'prod' to 'dev')
    causes the config file's environment to be updated in the rendered output.
    """
    ast = round_trip_loads(JML_INPUT)
    resolved_ast = resolve(ast)
    dumped_text = round_trip_dumps(resolved_ast)
    # Update the environment value in the context.
    new_context = dict(BASE_CONTEXT)
    new_context["env"] = "dev"
    rendered_output = render(dumped_text, context=new_context)
    # Check that the config block now has extras with "env" set to "dev".
    assert '"env" = "dev"' in rendered_output, "Updated env value not reflected in config extras."


@pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028
def test_update_module_extras():
    """
    Validate that updating a module's 'extras' (changing the owner for the login module)
    is reflected in the rendered output.
    """
    ast = round_trip_loads(JML_INPUT)
    # Update the context to change the owner in the login module from "teamA" to "teamX".
    new_context = deepcopy(BASE_CONTEXT)
    new_context["packages"][0]["modules"][0]["extras"]["owner"] = "teamX"
    resolved_ast = resolve(ast)
    dumped_text = round_trip_dumps(resolved_ast)
    rendered_output = render(dumped_text, context=new_context)
    # Check that the rendered output now contains the updated owner value.
    assert '"owner" = "teamX"' in rendered_output, "Updated module extras not reflected in rendered output."
