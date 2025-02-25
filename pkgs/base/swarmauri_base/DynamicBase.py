# swarmauri_base/DynamicBase.py

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
from swarmauri_typing import UnionFactory, UnionFactoryMetadata
class DynamicBase(BaseModel):
    """
    Base class for all components.
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
        return cls._union_factory

    @classmethod
    def _set_union_factory(cls) -> None:
        cls._union_factory = UnionFactory(
           bound=cls.unified_subclass_getter,
           annotation_extenders=[Field(discriminator="type")]
        )

    @classmethod
    def _field_contains_subclass_union(cls, field_annotation) -> bool:
        # First, check if the field_annotation itself is metadata.
        if type(field_annotation).__name__ == "UnionFactoryMetadata":
            glogger.debug(f"Directly detected metadata: {field_annotation}")
            return True

        origin = get_origin(field_annotation)
        args = get_args(field_annotation)
        glogger.debug(f"_field_contains_subclass_union: get_origin: {origin}, get_args: {args}")

        if origin is Annotated:
            for arg in args:
                if type(arg).__name__ == "UnionFactoryMetadata":
                    glogger.debug(f"Field has UnionFactoryMetadata for {arg.data}")
                    return True
                if cls._field_contains_subclass_union(arg):
                    glogger.debug(f"Annotated field contains UnionFactory in '{arg}'")
                    return True
        elif origin in {Union, list, List, dict, Dict, set, Set, tuple, Tuple, Optional}:
            for arg in args:
                if cls._field_contains_subclass_union(arg):
                    glogger.debug(f"Container field '{field_annotation}' contains UnionFactory in its arguments")
                    return True

        glogger.debug(f"Field annotation '{field_annotation}' does not contain UnionFactory or UnionFactoryMetadata")
        return False


    @classmethod
    def _extract_parent_classes_from_field(cls, field_annotation) -> List[Type["DynamicBase"]]:
        glogger.debug(f"Extracting resource types from '{field_annotation}'.")
        parent_classes = []
        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)
            glogger.debug(f"_extract_parent_classes_from_field: get_origin: {get_origin(field_annotation)}, get_args: {get_args(field_annotation)}")
            if origin is Annotated:
                # Skip the first argument (base type), process metadata.
                for arg in args[1:]:
                    glogger.debug(f"\n\n annotated - {arg}\n\n")
                    if type(arg).__name__ == "UnionFactoryMetadata":
                        parent_classes.append(arg.data)
                    else:
                        parent_classes.extend(cls._extract_parent_classes_from_field(arg))
            elif origin in {Union, list, List, dict, Dict, set, Set, tuple, Tuple, Optional}:
                for arg in args:
                    glogger.debug(f"\n\n origin - {arg}\n\n")
                    parent_classes.extend(cls._extract_parent_classes_from_field(arg))
            glogger.debug(f"_extract_parent_classes_from_field result: {parent_classes}")
            return parent_classes
        except TypeError as e:
            glogger.error(f"TypeError while extracting resource types: {e}")
            return parent_classes

    @classmethod
    def _determine_new_type(cls, field_annotation, parent_class):
        glogger.debug(
            f"Determining new type for '{field_annotation}' with parent '{parent_class.__name__}'"
        )
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

            # If Annotated, preserve metadata, but remove previous UnionFactoryMetadata
            if origin is Annotated:
                base_type = args[0]
                metadata = [m for m in args[1:] if not isinstance(m, UnionFactoryMetadata)]
                # Use the dynamic union factory to generate fresh metadata.
                metadata.append(cls._union_factory[parent_class])
                field_annotation = Annotated[tuple([base_type, *metadata])]

            # Instead of using the old global UnionFactory, use the _union_factory from the instance.
            subclass_union = cls._union_factory[parent_class]

            # Reapply Optional if needed.
            new_type = Union[subclass_union, type(None)] if is_optional else subclass_union
            return new_type
        except TypeError as e:
            glogger.error(f"TypeError in _determine_new_type: {e}")
            return field_annotation

    @staticmethod
    def unified_subclass_getter(parent_cls: Union[str, Type["DynamicBase"]]) -> List[Type["DynamicBase"]]:
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
        Recursively update the annotation to replace any Annotated[...] that contains
        a UnionFactoryMetadata with the new type computed via _determine_new_type.
        """
        glogger.debug(
            f"Updating Annotation Recursively for '{annotation}' with parent '{parent_class.__name__}'"
        )

        origin = get_origin(annotation)
        if origin is Annotated:
            # We assume this Annotated block is the one that contains UnionFactoryMetadata.
            # Let _determine_new_type do its job.
            return cls._determine_new_type(annotation, parent_class)
        elif origin in {Union, list, List, dict, Dict, set, Set, tuple, Tuple, Optional}:
            args = get_args(annotation)
            # Recursively update each of the arguments.
            new_args = tuple(cls._update_annotation_recursively(arg, parent_class) for arg in args)
            try:
                if origin is Union:
                    return Union[new_args]
                else:
                    return origin[new_args]
            except Exception:
                # In case of error reconstructing the type, fallback.
                return annotation
        else:
            # No container or Annotated: nothing to update.
            return annotation

    @classmethod
    def _generate_models_with_fields(cls) -> Dict[Type[BaseModel], Dict[str, Any]]:
        """
        Generate a mapping of model classes (both base and subtypes) to a dict of field names and their updated type annotations.
        """
        glogger.debug("Generating models_with_fields from unified registry.")
        models_with_fields: Dict[Type[BaseModel], Dict[str, Any]] = {}

        # Iterate over each base model in the registry.
        for model_name, entry in cls._registry.items():
            base_model = entry["model_cls"]
            models_with_fields.setdefault(base_model, {})
            # Process fields on the base model.
            for field_name, field_info in base_model.model_fields.items():
                field_annotation = base_model.__annotations__.get(field_name)
                if not field_annotation:
                    continue
                if not cls._field_contains_subclass_union(field_annotation):
                    continue
                parent_classes = cls._extract_parent_classes_from_field(field_annotation)
                glogger.debug(f"_generate_models_with_fields parent_classes: '{parent_classes}'")
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
                    glogger.debug(f"_generate_models_with_fields parent_classes: '{parent_classes}'")

                    for parent in parent_classes:
                        new_type = cls._update_annotation_recursively(field_annotation, parent)
                        models_with_fields[subtype][field_name] = new_type

        glogger.debug("Completed generating models_with_fields.")
        return models_with_fields

    ###############################################################
    # Rebuild Models from the Unified Registry
    ###############################################################

    @classmethod
    def _recreate_models(cls):
        """
        Rebuild all models by updating fields that use UnionFactory based on the unified registry.
        This combines both base models and registered subtypes.
        """
        with cls._lock:
            models_with_fields = cls._generate_models_with_fields()
            glogger.debug(f"\n\n\n\n_recreate_models: {models_with_fields}\n\n\n\n")
            for model_class, fields in models_with_fields.items():
                for field_name, new_type in fields.items():
                    if field_name in model_class.model_fields:
                        original_type = model_class.model_fields[field_name].annotation
                        if original_type != new_type:
                            model_class.model_fields[field_name].annotation = new_type
                            glogger.debug(
                                f"Updated field '{field_name}' in model '{model_class.__name__}' from '{original_type}' to '{new_type}'"
                            )
                        else:
                            glogger.debug(
                                f"No change for field '{field_name}' in model '{model_class.__name__}'"
                            )
                    else:
                        glogger.error(
                            f"Field '{field_name}' does not exist in model '{model_class.__name__}'"
                        )
                        continue

                try:
                    model_class.model_rebuild(force=True)
                    glogger.debug(f"Rebuilt model '{model_class.__name__}'.")
                except ValidationError as ve:
                    glogger.error(f"Validation error rebuilding '{model_class.__name__}': {ve}")
                except Exception as e:
                    glogger.error(f"Error rebuilding '{model_class.__name__}': {e}")
            glogger.debug("All models have been successfully recreated from the unified registry.")

    ###############################################################
    # Registration Decorators
    ###############################################################

    @classmethod
    def register_model(cls):
        """
        Decorator to register a base model in the unified registry.
        """
        def decorator(model_cls: Type[BaseModel]):
            model_name = model_cls.__name__
            if model_name in cls._registry:
                glogger.debug(f"Model '{model_name}' is already in the unified registry; skipping duplicate.")
                return model_cls

            cls._registry[model_name] = {"model_cls": model_cls, "subtypes": {}}
            glogger.debug(f"Registered base model '{model_name}'.")
            DynamicBase._recreate_models()
            return model_cls

        return decorator

    @classmethod
    def register_type(cls, resource_type: Optional[Union[Type[T], List[Type[T]]]] = None, type_name: Optional[str] = None):
        """
        Decorator to register a subtype under one or more base models in the unified registry.
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
                    glogger.debug(f"Created new unified registry entry for base model '{base_model_name}'.")

                subtypes_dict = cls._registry[base_model_name]["subtypes"]
                if final_type_name in subtypes_dict:
                    glogger.debug(f"Type '{final_type_name}' already exists under '{base_model_name}'; skipping duplicate.")
                    continue

                subtypes_dict[final_type_name] = subclass
                glogger.debug(f"Registered '{subclass.__name__}' as '{final_type_name}' under '{base_model_name}'.")

            DynamicBase._recreate_models()
            return subclass

        return decorator

###########################################
# Subclass Union
###########################################
DynamicBase._set_union_factory()
SubclassUnion = DynamicBase._get_union_factory()

