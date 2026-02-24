from abc import ABC, abstractmethod

class IParser(ABC):
    """Abstract base class for all parsers."""

    @abstractmethod
    def parse(self, input_data):
        """Parses the given input data and returns an AST."""
        pass

    @abstractmethod
    def dump(self, ast_tree):
        """Returns a human-readable dump of the AST."""
        pass

    @abstractmethod
    def walk(self, ast_tree):
        """Walks through all nodes in the AST."""
        pass

    @abstractmethod
    def iter_child_nodes(self, node):
        """Iterates over child nodes of a given node."""
        pass

    @abstractmethod
    def update_node(self, ast_tree, target_value, new_value):
        """Modifies a specific node in the AST."""
        pass

    @abstractmethod
    def analyze_ast(self, ast_tree):
        """Analyzes the AST for specific properties."""
        pass

    @abstractmethod
    def validate_ast(self, ast_tree):
        """Validates the AST against a set of rules."""
        pass

    @abstractmethod
    def unparse(self, ast_tree):
        """Converts an AST back into source code."""
        pass

    @abstractmethod
    def literal_eval(self, expression):
        """Safely evaluates an expression containing literals."""
        pass

    @abstractmethod
    def compile(self, ast_tree):
        """Compiles the AST into executable bytecode."""
        pass

    @abstractmethod
    def execute(self, compiled_code):
        """Executes compiled bytecode."""
        pass

    @abstractmethod
    def flatten(self, ast_tree):
        """Flattens an AST into a sequential list of nodes."""
        pass

    @abstractmethod
    def add_node(self, parent_node, new_node, position="left"):
        """Adds a single node to the AST."""
        pass

    @abstractmethod
    def add_nodes(self, parent_node, new_nodes):
        """Adds multiple nodes to the AST."""
        pass

    @abstractmethod
    def remove_node(self, ast_tree, target_value):
        """Removes a single node from the AST."""
        pass

    @abstractmethod
    def remove_nodes(self, ast_tree, target_values):
        """Removes multiple nodes from the AST."""
        pass

    @abstractmethod
    def search(self, ast_tree, condition):
        """Searches the AST based on a condition."""
        pass

# Example: Attempting to instantiate IParser will raise an error since it's abstract
try:
    parser = IParser()
except TypeError as e:
    print(f"Error: {e}")  # Abstract class instantiation error
