import ast
from typing import List, Union, Any, Literal
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument

class PythonParser(ParserBase):
    """
    A parser that processes Python source code to extract structural elements
    such as functions, classes, and their docstrings.
    
    This parser utilizes the `ast` module to parse the Python code into an abstract syntax tree (AST)
    and then walks the tree to extract relevant information.
    """
    type: Literal['PythonParser'] = 'PythonParser'
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given Python source code to extract structural elements.

        Args:
            data (Union[str, Any]): The input Python source code as a string.

        Returns:
            List[IDocument]: A list of IDocument objects, each representing a structural element 
                             extracted from the code along with its metadata.
        """
        if not isinstance(data, str):
            raise ValueError("PythonParser expects a string input.")
        
        documents = []
        tree = ast.parse(data)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                element_name = node.name
                docstring = ast.get_docstring(node)
                
                # Get the source code snippet
                source_code = ast.get_source_segment(data, node)
                
                # Create a metadata dictionary
                metadata = {
                    "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                    "name": element_name,
                    "docstring": docstring,
                    "source_code": source_code
                }
                
                # Create a Document for each structural element
                document = Document(content=docstring, metadata=metadata)
                documents.append(document)
                
        return documents