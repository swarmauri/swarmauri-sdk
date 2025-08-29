from typing import Annotated, Any, Tuple, Type, TypeVar, Union

T = TypeVar("T")


class IntersectionFactoryMetadata:
    """Metadata describing the classes used to build the intersection."""

    def __init__(self, classes: Tuple[Type[T]]):
        self.classes = classes

    def __repr__(self) -> str:
        return f"IntersectionFactoryMetadata(classes={self.classes!r})"


class IntersectionFactory:
    """Factory for building an Annotated union from common ancestors.

    Usage:
        IntersectionFactory[TypeA, TypeB, ...]

    This returns an ``Annotated`` ``Union`` of all classes common to the
    given types.
    """

    def __class_getitem__(cls, classes: Union[Type, Tuple[Type, ...]]) -> type:
        if not isinstance(classes, tuple):
            classes = (classes,)

        common = set(classes[0].__mro__)
        for c in classes[1:]:
            common.intersection_update(c.__mro__)

        ordered_common = [c for c in classes[0].__mro__ if c in common]

        if not ordered_common:
            return Annotated[Any, IntersectionFactoryMetadata(classes=(classes))]

        union_type = Union[tuple(ordered_common)]
        return Annotated[union_type, IntersectionFactoryMetadata(classes=(classes))]
