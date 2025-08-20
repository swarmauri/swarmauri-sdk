from autoapi.v3.specs import IO


def test_in_verbs_attribute() -> None:
    io = IO(in_verbs=("create", "update"))
    assert io.in_verbs == ("create", "update")


def test_out_verbs_attribute() -> None:
    io = IO(out_verbs=("read",))
    assert io.out_verbs == ("read",)


def test_mutable_verbs_attribute() -> None:
    io = IO(mutable_verbs=("update",))
    assert io.mutable_verbs == ("update",)


def test_alias_in_attribute() -> None:
    io = IO(alias_in="nickname")
    assert io.alias_in == "nickname"


def test_alias_out_attribute() -> None:
    io = IO(alias_out="nickname")
    assert io.alias_out == "nickname"


def test_sensitive_attribute() -> None:
    io = IO(sensitive=True)
    assert io.sensitive is True


def test_redact_last_attribute() -> None:
    io = IO(redact_last=2)
    assert io.redact_last == 2


def test_filter_ops_attribute() -> None:
    io = IO(filter_ops=("eq", "gt"))
    assert io.filter_ops == ("eq", "gt")


def test_sortable_attribute() -> None:
    io = IO(sortable=True)
    assert io.sortable is True


def test_allow_in_attribute() -> None:
    io = IO(allow_in=False)
    assert io.allow_in is False


def test_allow_out_attribute() -> None:
    io = IO(allow_out=False)
    assert io.allow_out is False
