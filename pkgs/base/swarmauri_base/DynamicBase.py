"""
DynamicBase module.

This module defines the DynamicBase class, which serves as the base class for all components.
It provides a unified registry for model types and supports dynamic deserialization using a custom
UnionFactory. The class also includes methods to update model annotations and rebuild models
based on the unified registry.

All classes and methods in this module use Spacy-style docstrings.
"""

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

###########################################
# Logging
###########################################
from .glogging import glogger

###########################################
# Typing
###########################################
T = TypeVar("T", bound="DynamicBase")

###########################################
# DynamicBase
###########################################
from swarmauri_typing import UnionFactory
from swarmauri_typing import UnionFactoryMetadata


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
    _union_factory: ClassVar[Optional[UnionFactory]] = None
    _lock: ClassVar[Lock] = Lock()
    _type: ClassVar[str] = "DynamicBase"

    # Instance-attribute type (to support deserialization)
    type: Literal["DynamicBase"] = "DynamicBase"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init_subclass__(cls, **kwargs):
        """
        Initialize a subclass of DynamicBase.

        This method is automatically called when a subclass is defined. It sets the type attribute,
        updates the class annotations, and initializes the UnionFactory for the subclass.

        Parameters:
            **kwargs: Additional keyword arguments.
        """
        super().__init_subclass__(**kwargs)
        cls._type = cls.__name__
        cls.__annotations__["type"] = Literal[cls.__name__]
        cls.type = cls.__name__
        cls._set_union_factory()

    ###############################################################
    # UnionFactory Support Methods
    ###############################################################

    @classmethod
    def _get_union_factory(cls) -> UnionFactory:
        """
        Retrieve the UnionFactory associated with this class.

        Returns:
            UnionFactory: The union factory for dynamic model resolution.
        """
        return cls._union_factory

    @classmethod
    def _set_union_factory(cls) -> None:
        """
        Set up the UnionFactory for the class.

        This method initializes the UnionFactory with a bound function to retrieve unified subclasses
        and applies an annotation extender to use a discriminator field 'type'.
        """
        cls._union_factory = UnionFactory(
            bound=cls.unified_subclass_getter,
            annotation_extenders=[Field(discriminator="type")]
        )

    @classmethod
    def _field_contains_subclass_union(cls, field_annotation) -> bool:
        """
        Determine if the field annotation contains a UnionFactory or UnionFactoryMetadata.

        Parameters:
            field_annotation: The type annotation to inspect.

        Returns:
            bool: True if the annotation contains UnionFactoryMetadata, False otherwise.
        """
        if type(field_annotation).__name__ == "UnionFactoryMetadata":
            glogger.debug("Detected UnionFactoryMetadata directly in field: %s", field_annotation)
            return True

        origin = get_origin(field_annotation)
        args = get_args(field_annotation)
        glogger.debug("Checking field annotation. Origin: %s, Args: %s", origin, args)

        if origin is Annotated:
            for arg in args:
                if type(arg).__name__ == "UnionFactoryMetadata":
                    glogger.debug("Field has UnionFactoryMetadata for: %s", getattr(arg, 'data', arg))
                    return True
                if cls._field_contains_subclass_union(arg):
                    glogger.debug("Annotated field contains UnionFactory in: %s", arg)
                    return True
        elif origin in {Union, list, List, dict, Dict, set, Set, tuple, Tuple, Optional}:
            for arg in args:
                if cls._field_contains_subclass_union(arg):
                    glogger.debug("Container field %s contains UnionFactory in its arguments.", field_annotation)
                    return True

        glogger.debug("Field annotation %s does not contain UnionFactory or UnionFactoryMetadata.", field_annotation)
        return False

    @classmethod
    def _extract_parent_classes_from_field(cls, field_annotation) -> List[Type["DynamicBase"]]:
        """
        Extract parent DynamicBase classes from a field annotation.

        Parameters:
            field_annotation: The type annotation to inspect.

        Returns:
            List[Type[DynamicBase]]: A list of parent classes extracted from the annotation.
        """
        glogger.debug("Extracting resource types from field annotation: %s", field_annotation)
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
                        parent_classes.extend(cls._extract_parent_classes_from_field(arg))
            elif origin in {Union, list, List, dict, Dict, set, Set, tuple, Tuple, Optional}:
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
        glogger.debug("Determining new type for field %s with parent %s", field_annotation, parent_class)
        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)
            is_optional = False

            # Handle Optional[...] (i.e. Union[..., None])
            if origin is Union and type(None) in args:
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    field_annotation = non_none_args[0]
                    origin = get_origin(field_annotation)
                    args = get_args(field_annotation)
                    is_optional = True

            # If Annotated, preserve metadata while removing previous UnionFactoryMetadata.
            if origin is Annotated:
                base_type = args[0]
                metadata = [m for m in args[1:] if not isinstance(m, UnionFactoryMetadata)]
                metadata.append(cls._union_factory[parent_class])
                field_annotation = Annotated[tuple([base_type, *metadata])]

            # Generate the subclass union using the instance's UnionFactory.
            subclass_union = cls._union_factory[parent_class]

            # Reapply Optional if needed.
            new_type = Union[subclass_union, type(None)] if is_optional else subclass_union
            return new_type
        except TypeError as e:
            glogger.error("TypeError in _determine_new_type: %s", e)
            return field_annotation

    @staticmethod
    def unified_subclass_getter(parent_cls: Union[str, Type["DynamicBase"]]) -> List[Type["DynamicBase"]]:
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
        glogger.debug("Recursively updating annotation %s with parent %s", annotation, parent_class)
        origin = get_origin(annotation)
        if origin is Annotated:
            return cls._determine_new_type(annotation, parent_class)
        elif origin in {Union, list, List, dict, Dict, set, Set, tuple, Tuple, Optional}:
            args = get_args(annotation)
            new_args = tuple(cls._update_annotation_recursively(arg, parent_class) for arg in args)
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
        glogger.debug("Generating models with updated field annotations from the unified registry.")
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
                parent_classes = cls._extract_parent_classes_from_field(field_annotation)
                glogger.debug("Parent classes for field %s: %s", field_name, parent_classes)
                for parent in parent_classes:
                    new_type = cls._update_annotation_recursively(field_annotation, parent)
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
                    parent_classes = cls._extract_parent_classes_from_field(field_annotation)
                    glogger.debug("Parent classes for field %s in subtype %s: %s", field_name, subtype.__name__, parent_classes)
                    for parent in parent_classes:
                        new_type = cls._update_annotation_recursively(field_annotation, parent)
                        models_with_fields[subtype][field_name] = new_type

        glogger.debug("Completed generating models with updated fields.")
        return models_with_fields

    @classmethod
    def _recreate_models(cls):
        """
        Rebuild all models by updating fields that use UnionFactory based on the unified registry.

        This method iterates through each model in the registry, updates their field annotations,
        and rebuilds the model schema.
        """
        with cls._lock:
            models_with_fields = cls._generate_models_with_fields()
            glogger.debug("Recreating models with updated fields: %s", models_with_fields)
            for model_class, fields in models_with_fields.items():
                for field_name, new_type in fields.items():
                    if field_name in model_class.model_fields:
                        original_type = model_class.model_fields[field_name].annotation
                        if original_type != new_type:
                            model_class.model_fields[field_name].annotation = new_type
                            glogger.debug(
                                "Updated field '%s' in model '%s' from '%s' to '%s'",
                                field_name, model_class.__name__, original_type, new_type
                            )
                        else:
                            glogger.debug("No change for field '%s' in model '%s'", field_name, model_class.__name__)
                    else:
                        glogger.error("Field '%s' does not exist in model '%s'", field_name, model_class.__name__)
                        continue

                try:
                    model_class.model_rebuild(force=True)
                    glogger.debug("Rebuilt model '%s'.", model_class.__name__)
                except Exception as e:
                    glogger.error("Error rebuilding '%s': %s", model_class.__name__, e)
            glogger.debug("All models have been successfully recreated from the unified registry.")

    ###############################################################
    # Registration Decorators
    ###############################################################

    @classmethod
    def register_model(cls):
        """
        Decorator to register a base model in the unified registry.

        Returns:
            Callable: A decorator function that registers the model class.
        """
        def decorator(model_cls: Type[BaseModel]):
            model_name = model_cls.__name__
            if model_name in cls._registry:
                glogger.warn("Model '%s' is already registered; skipping duplicate.", model_name)
                return model_cls

            cls._registry[model_name] = {"model_cls": model_cls, "subtypes": {}}
            glogger.debug("Registered base model '%s'.", model_name)
            DynamicBase._recreate_models()
            return model_cls

        return decorator

    @classmethod
    def register_type(cls, resource_type: Optional[Union[Type[T], List[Type[T]]]] = None, type_name: Optional[str] = None):
        """
        Decorator to register a subtype under one or more base models in the unified registry.

        Parameters:
            resource_type (Optional[Union[Type[T], List[Type[T]]]]):
                The base model(s) under which to register the subtype. If None, all direct base classes (except DynamicBase)
                are used.
            type_name (Optional[str]): An optional custom type name for the subtype.

        Returns:
            Callable: A decorator function that registers the subtype.
        """
        def decorator(subclass: Type["DynamicBase"]):
            if resource_type is None:
                resource_types = [base for base in subclass.__bases__ if base is not cls]
            elif not isinstance(resource_type, list):
                resource_types = [resource_type]
            else:
                resource_types = resource_type

            for rt in resource_types:
                if not issubclass(subclass, rt):
                    raise TypeError(f"'{subclass.__name__}' must be a subclass of '{rt.__name__}'.")
                final_type_name = type_name or getattr(subclass, "_type", subclass.__name__)
                base_model_name = rt.__name__

                if base_model_name not in cls._registry:
                    cls._registry[base_model_name] = {"model_cls": rt, "subtypes": {}}
                    glogger.debug("Created new registry entry for base model '%s'.", base_model_name)

                subtypes_dict = cls._registry[base_model_name]["subtypes"]
                if final_type_name in subtypes_dict:
                    glogger.warn("Type '%s' already exists under '%s'; skipping duplicate.", final_type_name, base_model_name)
                    continue

                subtypes_dict[final_type_name] = subclass
                glogger.debug("Registered '%s' as '%s' under '%s'.", subclass.__name__, final_type_name, base_model_name)

            DynamicBase._recreate_models()
            return subclass

        return decorator


###########################################
# Subclass Union
###########################################
DynamicBase._set_union_factory()
SubclassUnion = DynamicBase._get_union_factory()
