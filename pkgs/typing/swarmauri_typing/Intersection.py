from typing import Type, TypeVar, Union, Any, Annotated, Tuple

T = TypeVar("T")


class IntersectionMetadata:
    def __init__(self, classes: Tuple[Type[T]]):
        self.classes = classes

    def __repr__(self):
        # Return a more 'developer-focused' string, e.g.:
        return f"IntersectionMetadata(classes={self.classes!r})"


# The Intersection metaclass as provided.
class Intersection(type):
    """
    A generic metaclass to create an intersection of discriminated subclasses.
    Usage:
        Intersection[TypeA, TypeB, ...]
    will return an Annotated Union of all registered classes that are common to
    all given resource types.
    """

    def __class_getitem__(cls, classes: Union[Type, Tuple[Type, ...]]) -> type:
        # Allow a single type or a tuple of types.
        if not isinstance(classes, tuple):
            classes = (classes,)

        # Compute the intersection of all MRO sets.
        common = set(classes[0].__mro__)
        for c in classes[1:]:
            common.intersection_update(c.__mro__)

        # Order the common classes as they appear in the first class's MRO.
        ordered_common = [c for c in classes[0].__mro__ if c in common]

        if not ordered_common:
            # Fallback to Any (should not happen as 'object' is always common)
            return Annotated[Any, IntersectionMetadata(classes=(classes))]
        else:
            # Construct a Union type from the ordered common bases.
            union_type = Union[tuple(ordered_common)]
            return Annotated[
                union_type,
                IntersectionMetadata(classes=(classes)),
            ]
