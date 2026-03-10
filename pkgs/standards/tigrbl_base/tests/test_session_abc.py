import pytest

from tigrbl_base._base._session_abc import SessionABC


def test_session_abc_is_abstract() -> None:
    with pytest.raises(TypeError):
        SessionABC()
