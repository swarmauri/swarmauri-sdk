import logging
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Union, Annotated, Type
from swarmauri.core.ComponentBase import ComponentBase, ComponentType

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
        subclasses = baseclass.__swm__get_subclasses__()
        return Union[tuple(subclasses)]
