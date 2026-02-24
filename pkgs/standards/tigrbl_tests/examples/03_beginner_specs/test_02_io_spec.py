from tigrbl.specs import IO


def test_io_spec_controls_verb_visibility():
    """Validate that IO specs gate which verbs are exposed.

    Purpose: introduce IO specs as the place to declare which operations
    accept input or produce output for a field.

    Best practice: keep IO rules explicit so API behavior is transparent to
    consumers and consistent across endpoints.
    """
    # Setup: define IO verbs for write and read operations.
    io_spec = IO(in_verbs=("create", "update"), out_verbs=("read",))
    # Assertion: verify verb membership for both directions.
    assert "create" in io_spec.in_verbs
    assert "read" in io_spec.out_verbs


def test_io_spec_can_express_read_only_fields():
    """Show how to model read-only fields with IO specs.

    Purpose: demonstrate that a field can be excluded from writes while still
    being exposed in read responses.

    Best practice: protect server-managed fields (timestamps, IDs) by keeping
    them out of the input verbs.
    """
    # Setup: declare a read-only field with no input verbs.
    io_spec = IO(in_verbs=(), out_verbs=("read", "list"))
    # Assertion: the field is write-protected but visible in reads.
    assert io_spec.in_verbs == ()
    assert "read" in io_spec.out_verbs
