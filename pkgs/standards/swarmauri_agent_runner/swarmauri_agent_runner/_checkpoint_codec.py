from swarmauri_core.run_stores import RunCheckpoint

from .RunState import RunState


def encode_checkpoint(
    state: RunState, *, advance: bool = False
) -> RunCheckpoint:
    payload = (
        state.model_copy(update={"revision": state.revision + 1})
        if advance
        else state
    )
    return RunCheckpoint(
        state.run_id, state.revision, payload.model_dump_json()
    )
