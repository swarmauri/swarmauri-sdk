from tigrbl.specs import IO


def test_io_spec_controls_verb_visibility():
    """Test io spec controls verb visibility."""
    io_spec = IO(in_verbs=("create", "update"), out_verbs=("read",))
    assert "create" in io_spec.in_verbs
    assert "read" in io_spec.out_verbs
