from tigrbl.hook.types import PHASES as HOOK_PHASES
from tigrbl.runtime.events import PHASES as RUNTIME_PHASES


def test_runtime_and_hook_phases_remain_in_sync() -> None:
    runtime_hook_window = tuple(
        phase for phase in RUNTIME_PHASES if phase in HOOK_PHASES
    )
    assert runtime_hook_window == HOOK_PHASES
