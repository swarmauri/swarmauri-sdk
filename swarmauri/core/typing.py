import logging
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Union, Annotated, Type
from swarmauri.core.ComponentBase import ComponentBase

ComponentType = TypeVar('ComponentType', bound=ComponentBase)

class SubclassUnion(Generic[ComponentType]):
    @staticmethod
    def __get_validators__():
        yield SubclassUnion.validate

    @classmethod
    def validate(cls, v, field):
        obj = field.sub_fields[0].type_ if field.sub_fields else None
        if obj and issubclass(obj, ComponentBase):
            subclasses = tuple(obj.__swm__get_subclasses__())
            if isinstance(v, subclasses):
                return v
            raise TypeError(f'Value must be an instance of {subclasses}')
        raise TypeError('Invalid object type')

    @classmethod
    def __class_getitem__(cls, baseclass: Type[ComponentType]):
        subclasses = cls.__swm__get_subclasses__(baseclass)
        return Union[tuple(subclasses)]

    @classmethod
    def __swm__get_subclasses__(cls, baseclass: Type[ComponentType]) -> set:
        logging.debug('__swm__get_subclasses__ executed\n')
        def is_excluded_module(module_name: str) -> bool:
            return (module_name == 'builtins' or 
                    module_name == 'types')

        subclasses_dict = {baseclass.__name__: baseclass}
        for subclass in baseclass.__subclasses__():
            if not is_excluded_module(subclass.__module__):
                subclasses_dict.update({_s.__name__: _s for _s in cls.__swm__get_subclasses__(subclass) 
                    if not is_excluded_module(_s.__module__)})

        return set(subclasses_dict.values())