def decorate_cls(cls, decorator_fn):
    import types
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if isinstance(attr, types.FunctionType):
            setattr(cls, attr_name, decorator_fn(attr))
    return cls

def decorate_instance(instance, decorator_fn):
    import types
    for attr_name in dir(instance):
        attr = getattr(instance, attr_name)
        if isinstance(attr, types.MethodType):
            setattr(instance, attr_name, decorator_fn(attr.__func__).__get__(instance))

def decorate_instance_method(instance, method_name, decorator_fn):
    # Get the method from the instance
    original_method = getattr(instance, method_name)
    
    # Decorate the method
    decorated_method = decorator_fn(original_method)
    
    # Rebind the decorated method to the instance
    setattr(instance, method_name, decorated_method.__get__(instance, instance.__class__))