from swarmauri_core.swarms.ISwarmComponent import ISwarmComponent

class SwarmComponentBase(ISwarmComponent):
    """
    Interface for defining basics of any component within the swarm system.
    """
    def __init__(self, key: str, name: str, superclass: str, module: str, class_name: str, args=None, kwargs=None):
        self.key = key
        self.name = name
        self.superclass = superclass
        self.module = module
        self.class_name = class_name
        self.args = args or []
        self.kwargs = kwargs or {}
    