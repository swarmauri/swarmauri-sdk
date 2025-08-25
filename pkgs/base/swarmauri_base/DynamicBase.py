"""
DynamicBase module.

This module defines the DynamicBase class, which serves as the base class for all components.
It provides a unified registry for model types and supports dynamic deserialization using a custom
UnionFactory. The class also includes methods to update model annotations and rebuild models
based on the unified registry.

All classes and methods in this module use Spacy-style docstrings.
"""

import functools
import inspect
from threading import Lock
from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from pydantic import BaseModel, Field, ConfigDict

from swarmauri_base.glogging import glogger
from swarmauri_typing import UnionFactory
from swarmauri_typing import UnionFactoryMetadata


T = TypeVar("T", bound="DynamicBase")


class DynamicBase(BaseModel):
    """
    Base class for all components.

    This class provides a unified registry mapping model names to their corresponding model classes
    and subtypes. It integrates a custom UnionFactory to support dynamic deserialization of models
    with union types and updates model annotations accordingly.

    Attributes:
        type (Literal["DynamicBase"]): The type identifier for the model.
    """

    # Unified registry mapping model names to a dict with "model_cls" and "subtypes"
    _registry: ClassVar[Dict[str, Dict[str, Any]]] = {}
    _subclass_union_factory: ClassVar[Optional[UnionFactory]] = None
    _full_union_factory: ClassVar[Optional[UnionFactory]] = None
    _lock: ClassVar[Lock] = Lock()
    _type: ClassVar[str] = "DynamicBase"

    # Instance-attribute type (to support deserialization)
    type: Literal["DynamicBase"] = "DynamicBase"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init_subclass__(cls, **kwargs):
        """Initialize a subclass of ``DynamicBase``.

        ``pydantic`` version 2 is strict about field overrides.  Tests in this
        repository dynamically create subclasses that simply assign ``type =
        "Dummy"`` without providing a type annotation.  When ``BaseModel``
        processes such a class it raises a ``PydanticUserError`` because the
        ``type`` field on ``DynamicBase`` is annotated.  To remain backwards
        compatible we inject the appropriate annotation before calling
        ``BaseModel.__init_subclass__``.

        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments passed to the superclass.
        """
        # Ensure the ``type`` annotation exists before ``BaseModel`` processes
        # the subclass.  If the subclass already defines an annotation we leave
        # it untouched.
        annotations = dict(getattr(cls, "__annotations__", {}))
        annotations.setdefault("type", Literal[cls.__name__])
        cls.__annotations__ = annotations
        cls.type = cls.__name__
        cls._type = cls.__name__

        super().__init_subclass__(**kwargs)

    ###############################################################
    # _subclass_union_factory methods
    ###############################################################

    @classmethod
    def _get_subclass_union_factory(cls) -> UnionFactory:
        """
        Retrieve the UnionFactory associated with this class.

        Returns:
            UnionFactory: The union factory for dynamic model resolution.
        """
        return cls._subclass_union_factory

    @classmethod
    def _set_subclass_union_factory(cls) -> None:
        """
        Set up the UnionFactory for the class.

        This method initializes the UnionFactory with a bound function to retrieve unified subclasses
        and applies an annotation extender to use a discriminator field 'type'.
        """
        cls._subclass_union_factory = UnionFactory(
            bound=cls._subclass_union_getter,
            name="subclass_union",
            annotation_extenders=[Field(discriminator="type")],
        )

    @staticmethod
    def _subclass_union_getter(
        parent_cls: Union[str, Type["DynamicBase"]],
    ) -> List[Type["DynamicBase"]]:
        """
        Retrieve registered subclasses for a given parent class.

        Parameters:
            parent_cls (Union[str, Type[DynamicBase]]): The parent class or its name.

        Returns:
            List[Type[DynamicBase]]: A list of registered subclass types.
        """
        if isinstance(parent_cls, str):
            model_name = parent_cls
        else:
            model_name = parent_cls.__name__
        entry = DynamicBase._registry.get(model_name)
        if not entry:
            return []
        return list(entry["subtypes"].values())

    ###############################################################
    # _full_union_factory methods
    ###############################################################

    @classmethod
    def _get_full_union_factory(cls) -> UnionFactory:
        """
        Retrieve the UnionFactory associated with this class.

        Returns:
            UnionFactory: The union factory for dynamic model resolution.
        """
        return cls._full_union_factory

    @classmethod
    def _set_full_union_factory(cls) -> None:
        """
        Set up the UnionFactory for the class.

        This method initializes the UnionFactory with a bound function to retrieve unified subclasses
        and applies an annotation extender to use a discriminator field 'type'.
        """
        cls._full_union_factory = UnionFactory(
            bound=cls._full_union_getter,
            name="full_union",
            annotation_extenders=[Field(discriminator="type")],
        )

    @staticmethod
    def _full_union_getter(
        parent_cls: Union[str, Type["DynamicBase"]],
    ) -> List[Type["DynamicBase"]]:
        """
        Retrieve registered subclasses for a given parent class.

        Parameters:
            parent_cls (Union[str, Type[DynamicBase]]): The parent class or its name.

        Returns:
            List[Type[DynamicBase]]: A list of registered subclass types.
        """
        if isinstance(parent_cls, str):
            model_name = parent_cls
        else:
            model_name = parent_cls.__name__
        entry = DynamicBase._registry.get(model_name)
        if not entry:
            # Fallback: if no registry entry exists, include the parent if possible.
            return [parent_cls] if isinstance(parent_cls, type) else []
        # Parent first, then its subtypes.
        return [entry["model_cls"]] + list(entry["subtypes"].values())

    ###############################################################
    # Annotation Update Helpers
    ##############################################################

    @classmethod
    def _collect_union_field_updates(
        cls, model_class: Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Traverse the model's MRO to collect union-annotated field updates.
        This ensures that inherited union fields are considered.
        """
        union_fields = {}
        # Traverse the MRO from the base upward so that more derived classes override earlier ones.
        for base in reversed(model_class.__mro__):
            if base is object:
                continue
            annotations = getattr(base, "__annotations__", {})
            for field_name, field_annotation in annotations.items():
                if cls._field_contains_subclass_union(field_annotation):
                    # Extract parent classes from the annotation.
                    parent_classes = cls._extract_parent_classes_from_field(
                        field_annotation
                    )
                    for parent in parent_classes:
                        # Calculate the updated union type.
                        new_type = cls._update_annotation_recursively(
                            field_annotation, parent
                        )
                        union_fields[field_name] = new_type
        return union_fields

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _field_contains_subclass_union(cls, field_annotation) -> bool:
        """
        Determine if the field annotation contains a UnionFactory or UnionFactoryMetadata.

        Parameters:
            field_annotation: The type annotation to inspect.

        Returns:
            bool: True if the annotation contains UnionFactoryMetadata, False otherwise.
        """
        if type(field_annotation).__name__ == "UnionFactoryMetadata":
            glogger.debug(
                "Detected UnionFactoryMetadata directly in field: %s", field_annotation
            )
            return True

        origin = get_origin(field_annotation)
        args = get_args(field_annotation)
        glogger.debug("Checking field annotation. Origin: %s, Args: %s", origin, args)

        if origin is Annotated:
            for arg in args:
                if type(arg).__name__ == "UnionFactoryMetadata":
                    glogger.debug(
                        "Field has UnionFactoryMetadata for: %s",
                        getattr(arg, "data", arg),
                    )
                    return True
                if cls._field_contains_subclass_union(arg):
                    glogger.debug("Annotated field contains UnionFactory in: %s", arg)
                    return True
        elif origin in {
            Union,
            list,
            List,
            dict,
            Dict,
            set,
            Set,
            tuple,
            Tuple,
            Optional,
        }:
            for arg in args:
                if cls._field_contains_subclass_union(arg):
                    glogger.debug(
                        "Container field %s contains UnionFactory in its arguments.",
                        field_annotation,
                    )
                    return True

        glogger.debug(
            "Field annotation %s does not contain UnionFactory or UnionFactoryMetadata.",
            field_annotation,
        )
        return False

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _extract_parent_classes_from_field(
        cls, field_annotation
    ) -> List[Type["DynamicBase"]]:
        """
        Extract parent DynamicBase classes from a field annotation.

        Parameters:
            field_annotation: The type annotation to inspect.

        Returns:
            List[Type[DynamicBase]]: A list of parent classes extracted from the annotation.
        """
        glogger.debug(
            "Extracting resource types from field annotation: %s", field_annotation
        )
        parent_classes = []
        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)
            glogger.debug("Extraction details - Origin: %s, Args: %s", origin, args)
            if origin is Annotated:
                # Skip the first argument (base type) and process metadata.
                for arg in args[1:]:
                    glogger.debug("Annotated metadata encountered: %s", arg)
                    if type(arg).__name__ == "UnionFactoryMetadata":
                        parent_classes.append(arg.data)
                    else:
                        parent_classes.extend(
                            cls._extract_parent_classes_from_field(arg)
                        )
            elif origin in {
                Union,
                list,
                List,
                dict,
                Dict,
                set,
                Set,
                tuple,
                Tuple,
                Optional,
            }:
                for arg in args:
                    glogger.debug("Processing container argument: %s", arg)
                    parent_classes.extend(cls._extract_parent_classes_from_field(arg))
            glogger.debug("Extracted parent classes: %s", parent_classes)
            return parent_classes
        except TypeError as e:
            glogger.error("TypeError while extracting resource types: %s", e)
            return parent_classes

    @classmethod
    def _determine_new_type(cls, field_annotation, parent_class):
        """
        Determine a new type annotation for a field based on the parent class.

        Parameters:
            field_annotation: The original field annotation.
            parent_class: The parent DynamicBase class to consider.

        Returns:
            The updated type annotation incorporating the subclass union.
        """
        glogger.debug(
            "Determining new type for field %s with parent %s",
            field_annotation,
            parent_class,
        )
        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)
            is_optional = False

            # Handle Optional[...] (i.e. Union[..., None])
            if origin is Union and type(None) in args:
                glogger.debug(f"\n\norigin - {args}\n\n")
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    field_annotation = non_none_args[0]
                    origin = get_origin(field_annotation)
                    args = get_args(field_annotation)
                    is_optional = True

            # If Annotated, preserve metadata while removing previous UnionFactoryMetadata.
            if origin is Annotated:
                glogger.debug(f"\n\nAnnotated - {args}")
                base_type = args[0]  # noqa: F841
                union_factory_metadata = args[1]
                glogger.debug(f"Annotated - {union_factory_metadata}\n\n")
                metadata = [
                    m for m in args[1:] if not isinstance(m, UnionFactoryMetadata)
                ]
                metadata.append(cls._subclass_union_factory[parent_class])
                field_annotation = Annotated[tuple([base_type, *metadata])]

            # Generate the subclass union using the instance's UnionFactory.
            if union_factory_metadata.name == "full_union":
                union_type = cls._full_union_factory[parent_class]
            else:
                union_type = cls._subclass_union_factory[parent_class]

            # Reapply Optional if needed.
            new_type = Union[union_type, type(None)] if is_optional else union_type
            glogger.debug(
                "Determined new type for:\n\t field %s \n\t with parent %s \n\t to be %s \n",
                field_annotation,
                parent_class,
                new_type,
            )
            return new_type
        except TypeError as e:
            glogger.error("TypeError in _determine_new_type: %s", e)
            return field_annotation

    ###############################################################
    # Helpers to Generate Field Updates
    ###############################################################

    @classmethod
    def _update_annotation_recursively(cls, annotation, parent_class) -> Any:
        """
        Recursively update a type annotation by replacing any Annotated block containing
        UnionFactoryMetadata with an updated type based on the parent class.

        Parameters:
            annotation: The original type annotation.
            parent_class: The parent DynamicBase class to consider.

        Returns:
            The updated type annotation.
        """
        glogger.debug(
            "Recursively updating annotation %s with parent %s",
            annotation,
            parent_class,
        )
        origin = get_origin(annotation)
        if origin is Annotated:
            return cls._determine_new_type(annotation, parent_class)
        elif origin in {
            Union,
            list,
            List,
            dict,
            Dict,
            set,
            Set,
            tuple,
            Tuple,
            Optional,
        }:
            args = get_args(annotation)
            new_args = tuple(
                cls._update_annotation_recursively(arg, parent_class) for arg in args
            )
            try:
                if origin is Union:
                    return Union[new_args]
                else:
                    return origin[new_args]
            except Exception:
                return annotation
        else:
            return annotation

    @classmethod
    def _generate_models_with_fields(cls) -> Dict[Type[BaseModel], Dict[str, Any]]:
        """
        Generate a mapping of model classes to their fields with updated type annotations.

        Returns:
            Dict[Type[BaseModel], Dict[str, Any]]:
                A dictionary mapping each model class to a dictionary of its fields and their new type annotations.
        """
        glogger.debug(
            "Generating models with updated field annotations from the unified registry."
        )
        models_with_fields: Dict[Type[BaseModel], Dict[str, Any]] = {}

        # Process each base model in the registry.
        for model_name, entry in cls._registry.items():
            base_model = entry["model_cls"]
            models_with_fields.setdefault(base_model, {})
            for field_name, field_info in base_model.model_fields.items():
                field_annotation = base_model.__annotations__.get(field_name)
                if not field_annotation:
                    continue
                if not cls._field_contains_subclass_union(field_annotation):
                    continue
                parent_classes = cls._extract_parent_classes_from_field(
                    field_annotation
                )
                glogger.debug(
                    "Parent classes for field %s: %s", field_name, parent_classes
                )
                for parent in parent_classes:
                    new_type = cls._update_annotation_recursively(
                        field_annotation, parent
                    )
                    models_with_fields[base_model][field_name] = new_type

            # Process each subtype registered under the base model.
            for subtype in entry["subtypes"].values():
                models_with_fields.setdefault(subtype, {})
                for field_name, field_info in subtype.model_fields.items():
                    field_annotation = subtype.__annotations__.get(field_name)
                    if not field_annotation:
                        continue
                    if not cls._field_contains_subclass_union(field_annotation):
                        continue
                    parent_classes = cls._extract_parent_classes_from_field(
                        field_annotation
                    )
                    glogger.debug(
                        "Parent classes for field %s in subtype %s: %s",
                        field_name,
                        subtype.__name__,
                        parent_classes,
                    )
                    for parent in parent_classes:
                        new_type = cls._update_annotation_recursively(
                            field_annotation, parent
                        )
                        models_with_fields[subtype][field_name] = new_type

        glogger.debug("Completed generating models with updated fields.")
        return models_with_fields

    @classmethod
    def _recreate_models(cls):
        """Rebuild registered ``pydantic`` models after registry changes."""
        with cls._lock:
            models_with_fields = cls._generate_models_with_fields()
            glogger.debug(
                "Recreating models with updated fields: %s", models_with_fields
            )

            # Now, for every registered model (base or subtype), merge in union updates
            for model_class in models_with_fields.keys():
                if model_class.__name__ != "BaseModel":
                    # Merge in any inherited union field updates:
                    merged_union_fields = cls._collect_union_field_updates(model_class)
                    for field_name, new_type in merged_union_fields.items():
                        if field_name in model_class.model_fields:
                            original_type = model_class.model_fields[
                                field_name
                            ].annotation
                            # Only update if there's a change.
                            if original_type != new_type:
                                model_class.model_fields[
                                    field_name
                                ].annotation = new_type
                                glogger.debug(
                                    "Merged union update for field '%s' in model '%s' from '%s' to '%s'",
                                    field_name,
                                    model_class.__name__,
                                    original_type,
                                    new_type,
                                )
                    try:
                        model_class.model_rebuild(force=True)
                        glogger.debug("Rebuilt model '%s'.", model_class.__name__)
                    except Exception as e:
                        glogger.error(
                            "Error rebuilding '%s': %s", model_class.__name__, e
                        )

            glogger.debug(
                "All models have been successfully recreated following the dependency chain."
            )

    ###############################################################
    # Registration Decorators
    ###############################################################

    @classmethod
    def register_model(cls, *, mixin: bool = False):
        """Register a base model or mixin in the unified registry.

        Parameters:
            mixin (bool): Set to ``True`` if the model is intended to be used as a
                mixin. Subclasses of mixins will not be registered under the
                mixin's namespace when ``register_type`` is invoked.

        Returns:
            Callable: A decorator function that registers the model class.
        """

        def decorator(model_cls: Type[BaseModel]):
            """Register ``model_cls`` as a base model or mixin."""
            model_name = model_cls.__name__
            if model_name in cls._registry:
                glogger.warning(
                    "Model '%s' is already registered; skipping duplicate.", model_name
                )
                return model_cls

            cls._registry[model_name] = {
                "model_cls": model_cls,
                "subtypes": {},
                "mixin": mixin,
            }
            setattr(model_cls, "_is_mixin", mixin)
            glogger.debug(
                "Registered base model '%s'%s.",
                model_name,
                " as mixin" if mixin else "",
            )
            DynamicBase._recreate_models()
            return model_cls

        return decorator

    @classmethod
    def register_type(
        cls,
        resource_type: Optional[Union[Type[T], List[Type[T]]]] = None,
        type_name: Optional[str] = None,
    ):
        """
        Decorator to register a subtype under one or more base models in the unified registry.

        Parameters:
            resource_type (Optional[Union[Type[T], List[Type[T]]]]):
                The base model(s) under which to register the subtype. If ``None``, all
                inherited non-mixin base classes (excluding ``DynamicBase`` itself) are
                used.
            type_name (Optional[str]): An optional custom type name for the subtype.

        Returns:
            Callable: A decorator function that registers the subtype.
        """

        def decorator(subclass: Type["DynamicBase"]):
            """Register ``subclass`` as a subtype."""
            if resource_type is None:
                mro_bases = inspect.getmro(subclass)[1:]
                resource_types = []
                for base in mro_bases:
                    if base in (cls, object):
                        continue
                    entry = cls._registry.get(base.__name__)
                    if not entry or entry.get("mixin"):
                        continue
                    model_cls = entry["model_cls"]
                    if model_cls not in resource_types:
                        resource_types.append(model_cls)
            elif not isinstance(resource_type, list):
                resource_types = [resource_type]
            else:
                resource_types = resource_type

            for rt in resource_types:
                if not issubclass(subclass, rt):
                    raise TypeError(
                        f"'{subclass.__name__}' must be a subclass of '{rt.__name__}'."
                    )
                final_type_name = type_name or getattr(
                    subclass, "_type", subclass.__name__
                )
                base_model_name = rt.__name__

                if base_model_name not in cls._registry:
                    cls._registry[base_model_name] = {"model_cls": rt, "subtypes": {}}
                    glogger.debug(
                        "Created new registry entry for base model '%s'.",
                        base_model_name,
                    )

                subtypes_dict = cls._registry[base_model_name]["subtypes"]
                if final_type_name in subtypes_dict:
                    glogger.warning(
                        "Type '%s' already exists under '%s'; skipping duplicate.",
                        final_type_name,
                        base_model_name,
                    )
                    continue

                subtypes_dict[final_type_name] = subclass
                glogger.debug(
                    "Registered '%s' as '%s' under '%s'.",
                    subclass.__name__,
                    final_type_name,
                    base_model_name,
                )

            DynamicBase._recreate_models()
            return subclass

        return decorator


###########################################
# Exports: Subclass Union
###########################################
DynamicBase._set_subclass_union_factory()
DynamicBase._set_full_union_factory()
SubclassUnion = DynamicBase._get_subclass_union_factory()
FullUnion = DynamicBase._get_full_union_factory()

###########################################
# Exports: Subclass Union
###########################################
register_type = DynamicBase.register_type
register_model = DynamicBase.register_model
