import spacy
from typing import List, Union, Any, Literal
from pydantic import PrivateAttr
from swarmauri_core.documents.IDocument import IDocument
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase

class EntityRecognitionParser(ParserBase):
    """
    EntityRecognitionParser leverages NER capabilities to parse text and 
    extract entities with their respective tags such as PERSON, LOCATION, ORGANIZATION, etc.
    """
    _nlp: Any = PrivateAttr()
    type: Literal['EntityRecognitionParser'] = 'EntityRecognitionParser'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load a SpaCy model. The small model is used for demonstration; larger models provide improved accuracy.
        self._nlp = spacy.load("en_core_web_sm")
    
    def parse(self, text: Union[str, Any]) -> List[IDocument]:
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
        for ent in doc.ents:
            # Create a document for each entity with metadata carrying entity type
            entity_doc = Document(doc_id=ent.text, content=ent.text, metadata={"entity_type": ent.label_})
            entities_docs.append(entity_doc)
        
        return entities_docs