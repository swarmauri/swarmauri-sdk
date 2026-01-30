from tigrbl.specs import S
from tigrbl.types import Integer


def test_storage_spec_captures_column_metadata():
    """Confirm the storage spec holds database-level column details.

    Purpose: reinforce that ``S`` is the authoritative source for storage
    configuration such as type, primary key status, and nullability.

    Best practice: declare storage rules in one place so migrations and models
    remain consistent across teams.
    """
    # Setup: define a storage spec with explicit primary key metadata.
    storage = S(type_=Integer, nullable=False, primary_key=True)
    # Assertion: storage settings are preserved on the spec object.
    assert storage.type_ is Integer
    assert storage.primary_key is True


def test_storage_spec_respects_nullability_flags():
    """Highlight how nullability travels through storage specs.

    Purpose: demonstrate that setting ``nullable=False`` is explicit and
    discoverable, enabling schema reviewers to enforce data requirements.

    Best practice: keep nullability decisions intentional so consumers know
    which fields are mandatory.
    """
    # Setup: declare a non-nullable storage spec.
    storage = S(type_=Integer, nullable=False)
    # Assertion: nullable flags remain explicit.
    assert storage.nullable is False
