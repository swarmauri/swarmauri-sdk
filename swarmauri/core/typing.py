from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Union, Annotated, Type
from swarmauri.core.ComponentBase import ComponentBase, ComponentType

class SubclassUnion(Generic[ComponentType]):
    @staticmethod
    def __get_validators__():
        yield SubclassUnionModel.validate

    @classmethod
    def validate(cls, v, field):
        obj = field.sub_fields[0].type_ if field.sub_fields else None
        if obj and issubclass(obj, ComponentBase):
            subclasses = tuple(obj.get_subclasses())
            if isinstance(v, subclasses):
                return v
            raise TypeError(f'Value must be an instance of {subclasses}')
        raise TypeError('Invalid object type')

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, model):
        obj = model.__args__[0]
        subclasses = obj.get_subclasses() if obj and issubclass(obj, ComponentBase) else []
        return {
            'type': 'object',
            'discriminator': {
                'propertyName': 'type',
                'mapping': {sub.__name__: sub for sub in subclasses}
            },
            'oneOf': [{'type': 'object', '$ref': f'#/definitions/{sub.__name__}'} for sub in subclasses]
        }

    def __class_getitem__(cls, item: Type[ComponentType]):
        return Annotated[
            Union[tuple(item.get_subclasses())],
            Field(discriminator='type')
        ]

SubclassUnion = SubclassUnionModel