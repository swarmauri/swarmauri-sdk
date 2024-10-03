import logging
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Union, Annotated, Type


class SubclassUnion:
    _registry = {}

    @classmethod
    def __class_getitem__(cls, baseclass):
        subclasses = cls.__swm__get_subclasses__(baseclass)
        return Union[tuple(subclasses)]

    @classmethod
    def __swm__get_subclasses__(cls, baseclass) -> set:
        logging.debug("__swm__get_subclasses__ executed\n")

        def is_excluded_module(module_name: str) -> bool:
            return module_name == "builtins" or module_name == "types"

        subclasses_dict = {baseclass.__name__: baseclass}
        for subclass in baseclass.__subclasses__():
            if not is_excluded_module(subclass.__module__):
                subclasses_dict.update(
                    {
                        _s.__name__: _s
                        for _s in cls.__swm__get_subclasses__(subclass)
                        if not is_excluded_module(_s.__module__)
                    }
                )

        return set(subclasses_dict.values())

    @classmethod
    def update(cls, baseclass, type_name: str, obj):
        """
        Registers a class with the SubclassUnion.
        """
        if baseclass not in cls._registry:
            cls._registry[baseclass] = {}

        cls._registry[baseclass][type_name] = obj
        logging.debug(f"Registered {type_name} under {baseclass.__name__}")

    @classmethod
    def get_registry(cls, baseclass):
        """
        Retrieves the registry of subclasses for a given base class.
        """
        return cls._registry.get(baseclass, {})
