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
            subclasses = tuple(obj.get_subclasses())
            if isinstance(v, subclasses):
                return v
            raise TypeError(f'Value must be an instance of {subclasses}')
        raise TypeError('Invalid object type')

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, model):
        obj = model.__args__[0]
        subclasses = obj.get_subclasses() if obj and issubclass(obj, ComponentBase) else []

        subclasses_list = []
        for each in subclasses:
            tmp_obj = {"name": each.__name__, "module_path": each, "type": each.type}
            subclasses_list.append(tmp_obj)

        mappings = {sub['name']: sub['module_path'] for sub in subclasses_list}
        logging.info(mappings)
        return {
            'type': 'object',
            'discriminator': {
                'propertyName': 'type',
                'mapping': mappings
            },
            'oneOf': [{'type': 'object', '$ref': f'#/definitions/{sub.__name__}'} for sub in subclasses]
        }

    @classmethod
    def update_schema(cls, model: Type[BaseModel]):
        """Force Pydantic to refresh the schema."""
        model.update_forward_refs()

    def __class_getitem__(cls, item: Type[ComponentType]):
        logging.info(f"Fetching subclasses for: {item.__name__}")
        union_type = Union[tuple(item.get_subclasses())]
        annotated_type = Annotated[union_type, Field(discriminator='type')]

        # Automatically update schema for the model using this SubclassUnion
        cls._register_schema_update(item)
        
        return annotated_type

    @classmethod
    def _register_schema_update(cls, item: Type[ComponentType]):
        """Register schema update for models using this SubclassUnion."""
        # Locate all models using this SubclassUnion and update their schemas
        for subclass in BaseModel.__subclasses__():
            for name, field in subclass.__annotations__.items():
                if isinstance(field, SubclassUnion):
                    logging.info(f"Updating schema for model: {subclass.__name__}")
                    cls.update_schema(subclass)