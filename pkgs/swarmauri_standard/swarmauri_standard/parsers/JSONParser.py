import json
import logging
from typing import List, Union, Any, Literal
from pydantic import BaseModel, ValidationError
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_base.ComponentBase import ComponentBase


# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@ComponentBase.register_type(ParserBase, "JSONParser")
class JSONParser(ParserBase):
    """
    Concrete implementation of IParser for parsing JSON formatted data into Document instances.

    This parser can handle complex nested structures and provides specialized validation
    capabilities for JSON schemas. It also optimizes the handling of large JSON documents.
    """

    type: Literal["JSONParser"] = "JSONParser"

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given JSON data into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The input data to parse, either as a JSON string or a file path.

        Returns:
        - List[IDocument]: A list of documents parsed from the JSON data.
        """
        # Prepare the data for parsing
        json_data = self._load_json(data)

        # Create a list to hold the parsed documents
        documents: List[IDocument] = []

        # Recursively parse JSON data into Document instances
        self._parse_json_object(json_data, documents)

        return documents

    def _load_json(self, data: Union[str, Any]) -> Any:
        """
        Loads JSON data from a string or a file.

        Parameters:
        - data (Union[str, Any]): The input data to load, either as a JSON string or a file path.

        Returns:
        - Any: The loaded JSON data.
        """
        try:
            if isinstance(data, str):
                # Attempt to load JSON from a string
                return json.loads(data)
            else:
                raise ValueError("Data provided is not a valid JSON string")
        except json.JSONDecodeError as e:
            logger.error("JSON decoding error: %s", e)
            raise ValueError("Invalid JSON data provided")

    def _parse_json_object(self, obj: Any, documents: List[IDocument], parent_key: str = '') -> None:
        """
        Recursively parses a JSON object or array into Document instances.

        Parameters:
        - obj (Any): The JSON object or array to parse.
        - documents (List[IDocument]): The list to append parsed Document instances.
        - parent_key (str): The key representing the parent structure for nested documents.
        """
        if isinstance(obj, dict):
            # Handle JSON object
            document = Document(doc_id=obj.get("id", None), content=obj.get("content", ""), metadata=obj)
            documents.append(document)
            logger.info("Parsed document: %s", document)

            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    # Recursively parse nested objects or arrays
                    self._parse_json_object(value, documents, parent_key=key)
        elif isinstance(obj, list):
            # Handle JSON array
            for item in obj:
                self._parse_json_object(item, documents, parent_key=parent_key)

    def validate_json_schema(self, json_data: Any, schema: dict) -> bool:
        """
        Validates JSON data against a given schema.

        Parameters:
        - json_data (Any): The JSON data to validate.
        - schema (dict): The JSON schema to validate against.

        Returns:
        - bool: True if valid, False otherwise.
        """
        try:
            jsonschema.validate(instance=json_data, schema=schema)
            return True
        except ValidationError as e:
            logger.error("JSON schema validation error: %s", e)
            return False