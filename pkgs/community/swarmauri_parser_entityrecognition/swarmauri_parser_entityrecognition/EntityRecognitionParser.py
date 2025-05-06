from typing import Any, List, Literal, Union

import spacy
from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.parsers.ParserBase import ParserBase

from swarmauri_standard.documents.Document import Document


@ComponentBase.register_type(ParserBase, "EntityRecognitionParser")
class EntityRecognitionParser(ParserBase):
    """
    EntityRecognitionParser leverages NER capabilities to parse text and
    extract entities with their respective tags such as PERSON, LOCATION, ORGANIZATION, etc.
    """

    _nlp: Any = PrivateAttr()
    type: Literal["EntityRecognitionParser"] = "EntityRecognitionParser"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            self._nlp = spacy.load("en_core_web_sm")
            self._nlp.initialize()
        except OSError:
            # First fallback: Try using blank English model
            print(
                "Warning: Could not load en_core_web_sm model. Using fallback options."
            )
            try:
                # Install the model if not found
                import subprocess

                subprocess.check_call(
                    ["python", "-m", "spacy", "download", "en_core_web_sm"]
                )
                self._nlp = spacy.load("en_core_web_sm")
            except Exception:
                # Final fallback: Use a blank model with minimal NER capabilities.
                print(
                    "Warning: Using blank English model with minimal NER capabilities."
                )
                self._nlp = spacy.blank("en")
                # Add a basic entity recognizer
                self._nlp.add_pipe("ner")
                # Initialize the pipeline
                self._nlp.initialize()

    def parse(self, text: Union[str, Any]) -> List[Document]:
        """
        Parses the input text, identifies entities, and returns a list of documents with entities tagged.

        Parameters:
        - text (Union[str, Any]): The input text to be parsed and analyzed for entities.

        Returns:
        - List[IDocument]: A list of IDocument instances representing the identified entities in the text.
        """
        # Ensure the input is a string type before processing
        if not isinstance(text, str):
            text = str(text)

        # Apply the NER model
        doc = self._nlp(text)

        # Compile identified entities into documents
        entities_docs = []
        for i, ent in enumerate(doc.ents):
            # Create a document for each entity with metadata carrying entity type
            # Remove doc_id from the constructor parameters
            entity_doc = Document(
                content=ent.text,
                metadata={
                    "entity_type": ent.label_,
                    "entity_id": str(i),  # Add an identifier in metadata if needed
                    "text": ent.text,  # Store the entity text in metadata too
                },
            )
            entities_docs.append(entity_doc)

        return entities_docs
