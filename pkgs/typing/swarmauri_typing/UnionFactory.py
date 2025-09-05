from typing import (
    Type,
    TypeVar,
    Callable,
    List,
    Union,
    Any,
    Annotated,
    get_args,
    Optional,
)

T = TypeVar("T")


class UnionFactoryMetadata:
    """
    Stores any metadata related to the union created by 'UnionFactory'.
    You can store anything you like in here (e.g., the original input
    or other context data).
    """

    def __init__(self, data: Any, name: Optional[str] = None):
        self.data = data
        self.name = name or self.__class__.__name__

    def __repr__(self):
        # Return a more 'developer-focused' string, e.g.:
        return f"UnionFactoryMetadata(name={self.name!r}, data={self.data!r})"


class UnionFactory:
    """
    A configurable factory for creating Annotated Union types.

    This can be used for many scenarios—e.g., uniting a set of classes
    discovered dynamically, or enumerating a set of allowed types
    based on a function you supply.
    """

    def __init__(
        self,
        bound: Callable[[Type[T]], List[type]],
        name: "str" = None,
        annotation_extenders: List[Any] = None,
    ):
        """
        :param bound:
            A function that takes an input (like a parent class or any other
            context) and returns a list of types to be included in the union.
        :param annotation_extenders:
            A list of metadata items to be appended (in order) to the final
            Annotated[...] union (beyond the default UnionFactoryMetadata).
        """
        self.name = name or self.__class__.__name__
        self._union_types_getter = bound
        self._annotation_extenders = annotation_extenders or []

    def _add_metadata(self, annotated_type: Any, new_metadata: Any) -> Any:
        """
        Appends 'new_metadata' to an existing Annotated type,
        or wraps a bare type in Annotated if it's not already Annotated.
        """
        if not (
            hasattr(annotated_type, "__origin__")
            and annotated_type.__origin__ is Annotated
        ):
            return Annotated[annotated_type, new_metadata]

        args = get_args(annotated_type)
        base_type = args[0]
        old_metadata = args[1:]
        return Annotated.__class_getitem__((base_type, *old_metadata, new_metadata))

    def __getitem__(self, input_data: Union[Type[T], str]) -> type:
        """
        Usage example:
          union_factory = UnionFactory(my_types_getter, [meta1, meta2])
          MyUnion = union_factory[MyParentClassOrOtherInput]

        Returns:
          An Annotated[...] union (or Annotated[Any, ...]) with:
            • A UnionFactoryMetadata object referencing 'input_data'
            • Any additional metadata from 'annotation_extenders'
        """

        if isinstance(input_data, str):
            model_name = input_data
        else:
            model_name = input_data.__name__

        union_members = self._union_types_getter(model_name)

        # If no types are returned, fall back to Annotated[Any, UnionFactoryMetadata]
        if not union_members:
            final_annotated = Annotated[
                Any, UnionFactoryMetadata(data=model_name, name=self.name)
            ]
        else:
            union_type = Union[tuple(union_members)]
            final_annotated = Annotated[
                union_type, UnionFactoryMetadata(data=model_name, name=self.name)
            ]

            # Add any additional metadata
            for extension in self._annotation_extenders:
                final_annotated = self._add_metadata(final_annotated, extension)

        return final_annotated
