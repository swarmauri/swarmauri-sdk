from tigrbl.hook.types import PHASES as HOOK_PHASES
from tigrbl.runtime.events import PHASES as RUNTIME_PHASES


def test_runtime_and_hook_phases_remain_in_sync() -> None:
    assert RUNTIME_PHASES == HOOK_PHASES
