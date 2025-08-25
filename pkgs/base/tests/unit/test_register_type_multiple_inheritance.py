from pydantic import BaseModel


from swarmauri_base import register_model, register_type
from swarmauri_base.DynamicBase import DynamicBase


def test_registers_all_inherited_bases():
    @register_model()
    class BaseParent(DynamicBase):
        pass

    @register_model()
    class BaseA(BaseParent):
        pass

    @register_model()
    class BaseB(DynamicBase):
        pass

    @register_type()
    class Child(BaseA, BaseB):
        pass

    assert "Child" in DynamicBase._registry["BaseA"]["subtypes"]
    assert "Child" in DynamicBase._registry["BaseB"]["subtypes"]
    assert "Child" in DynamicBase._registry["BaseParent"]["subtypes"]

    for name in ["BaseParent", "BaseA", "BaseB", "Child"]:
        DynamicBase._registry.pop(name, None)
    DynamicBase._recreate_models()


def test_excludes_mixins_from_registration():
    @register_model()
    class BaseB(DynamicBase):
        pass

    @register_model(mixin=True)
    class MixinA(BaseModel):
        pass

    @register_type()
    class ChildMixin(MixinA, BaseB):
        pass

    assert "ChildMixin" in DynamicBase._registry["BaseB"]["subtypes"]
    assert "ChildMixin" not in DynamicBase._registry["MixinA"]["subtypes"]

    for name in ["BaseB", "MixinA", "ChildMixin"]:
        DynamicBase._registry.pop(name, None)
    DynamicBase._recreate_models()
