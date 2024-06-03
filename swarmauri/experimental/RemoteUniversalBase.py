import requests
import hashlib
from functools import wraps
from uuid import uuid4
import inspect

def remote_local_transport(cls):
    original_init = cls.__init__
    def init_wrapper(self, *args, **kwargs):
        host = kwargs.pop('host', None)
        resource = kwargs.get('resource', cls.__name__)
        owner = kwargs.get('owner')
        name = kwargs.get('name')
        id = kwargs.get('id')
        #path = kwargs.get('path')
        if host:
            #self.is_remote = True
            self.host = host
            self.resource = resource
            self.owner = owner
            self.id = id
            #self.path = path
            url = f"{host}/{owner}/{resource}/{id}"
            data = {"class_name": cls.__name__, "owner": owner, "name": name, **kwargs}
            response = requests.post(url, json=data)
            if not response.ok:
                raise Exception(f"Failed to initialize remote {cls.__name__}: {response.text}")
        else:
            original_init(self, owner, name, **kwargs)  # Ensure proper passing of positional arguments

    setattr(cls, '__init__', init_wrapper)

    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("_"):
            setattr(cls, attr_name, method_wrapper(attr_value))
        elif isinstance(attr_value, property):
            prop_get = attr_value.fget and method_wrapper(attr_value.fget)
            prop_set = attr_value.fset and method_wrapper(attr_value.fset)
            prop_del = attr_value.fdel and method_wrapper(attr_value.fdel)
            setattr(cls, attr_name, property(prop_get, prop_set, prop_del, attr_value.__doc__))
    return cls


def method_wrapper(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        self = args[0]
        if getattr(self, 'host'):
            print('[x] Executing remote call...')
            url = f"{self.path}".lower()
            response = requests.post(url, json={"args": args[1:], "kwargs": kwargs})
            if response.ok:
                return response.json()
            else:
                raise Exception(f"Remote method call failed: {response.text}")
        else:
            return method(*args, **kwargs)
    return wrapper

class RemoteLocalMeta(type):
    def __new__(metacls, name, bases, class_dict):
        cls = super().__new__(metacls, name, bases, class_dict)
        if bases:  # This prevents BaseComponent itself from being decorated
            cls = remote_local_transport(cls)
        cls.class_hash = cls._calculate_class_hash()
        return cls

    def _calculate_class_hash(cls):
        sig_hash = hashlib.sha256()
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not attr_name.startswith("_"):
                sig = inspect.signature(attr_value)
                sig_hash.update(str(sig).encode())
        return sig_hash.hexdigest()
    

class BaseComponent(metaclass=RemoteLocalMeta):
    version = "1.0.0"  # Semantic versioning initialized here
    def __init__(self, owner, name, host=None, members=[], resource=None):
        self.id = uuid4()
        self.owner = owner
        self.name = name
        self.host = host  
        #self.is_remote = bool(self.host) 
        self.members = members
        self.resource = resource if resource else self.__class__.__name__
        self.path = f"{self.host if self.host else ''}/{self.owner}/{self.resource}/{self.id}"

    @property
    def is_remote(self):
        return bool(self.host)

    @classmethod
    def public_interfaces(cls):
        methods = []
        for attr_name in dir(cls):
            # Retrieve the attribute
            attr_value = getattr(cls, attr_name)
            # Check if it's callable or a property and not a private method
            if (callable(attr_value) and not attr_name.startswith("_")) or isinstance(attr_value, property):
                methods.append(attr_name)
        return methods

    @classmethod
    def is_method_registered(cls, method_name):
        """
        Checks if a public method with the given name is registered on the class.
        Args:
            method_name (str): The name of the method to check.
        Returns:
            bool: True if the method is registered, False otherwise.
        """
        return method_name in cls.public_interfaces()

    @classmethod
    def method_with_signature(cls, input_signature):
        """
        Checks if there is a method with the given signature available in the class.
        
        Args:
            input_signature (str): The string representation of the method signature to check.
        
        Returns:
            bool: True if a method with the input signature exists, False otherwise.
        """
        for method_name in cls.public_interfaces():
            method = getattr(cls, method_name)
            if callable(method):
                sig = str(inspect.signature(method))
                if sig == input_signature:
                    return True
        return False