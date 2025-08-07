import importlib
import uuid
from unittest.mock import Mock, patch

import click
import pytest
import typer

from peagen.cli.commands import init as init_cmd
from peagen.defaults import DEFAULT_TENANT_ID
from peagen.orm import Repository


@pytest.mark.unit
def test_remote_init_repo_uses_current_user_id():
    rpc = Mock()
    ctx = typer.Context(click.Command("cmd"), obj={"rpc": rpc})

    autoapi_module = importlib.reload(importlib.import_module("autoapi.v2"))
    orig_get_schema = autoapi_module.AutoAPI.get_schema
    User = importlib.import_module("autoapi.v2.tables.user").User

    SURead = orig_get_schema(User, "read")
    user = SURead(username="tester", id=uuid.uuid4(), tenant_id=DEFAULT_TENANT_ID)
    SRepoRead = orig_get_schema(Repository, "read")
    repo = SRepoRead(
        name="repo",
        url="https://git.peagen.com/foo/repo.git",
        default_branch="main",
        remote_name="origin",
        id=uuid.uuid4(),
        tenant_id=DEFAULT_TENANT_ID,
        owner_id=user.id,
    )
    rpc.call.side_effect = [user, repo]

    with (
        patch.object(init_cmd.AutoAPI, "get_schema", orig_get_schema),
        patch("peagen.cli.commands.init._remote_task"),
    ):
        init_cmd.remote_init_repo(
            ctx, "foo/repo", origin=None, upstream=None, default_branch="main"
        )

    assert rpc.call.call_args_list[0][0][0] == "Users.me"
    second_call = rpc.call.call_args_list[1]
    assert second_call[0][0] == "Repositories.create"
    params = second_call[1]["params"]
    assert str(params.owner_id) == str(user.id)
