def apply_metaclass_to_cls(cls, metaclass):
    # Create a new class using the metaclass, with the same name, bases, and attributes as the original class
    new_class = metaclass(cls.__name__, cls.__bases__, dict(cls.__dict__))
    return new_class
