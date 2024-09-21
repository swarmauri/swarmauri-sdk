import logging
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Union, Annotated, Type


class SubclassUnion:

    @classmethod
    def __class_getitem__(cls, baseclass):
        subclasses = cls.__swm__get_subclasses__(baseclass)
        return Union[tuple(subclasses)]

    @classmethod
    def __swm__get_subclasses__(cls, baseclass) -> set:
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