from typing import List, Union, Any, Literal
from transformers import BertTokenizer, BertModel
import torch
from pydantic import PrivateAttr
from swarmauri_core.documents.IDocument import IDocument
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase

class BERTEmbeddingParser(ParserBase):
    """
    A parser that transforms input text into document embeddings using BERT.
    
    This parser tokenizes the input text, passes it through a pre-trained BERT model,
    and uses the resulting embeddings as the document content.
    """
    parser_model_name: str = 'bert-base-uncased'
    _model: Any = PrivateAttr()
    type: Literal['BERTEmbeddingParser'] = 'BERTEmbeddingParser'

    def __init__(self, **kwargs):
        """
        Initializes the BERTEmbeddingParser with a specific BERT model.
        
        Parameters:
        - model_name (str): The name of the pre-trained BERT model to use.
        """
        super().__init__(**kwargs)
        self.tokenizer = BertTokenizer.from_pretrained(self.parser_model_name)
        self._model = BertModel.from_pretrained(self.parser_model_name)
        self._model.eval()  # Set model to evaluation mode

    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Tokenizes input data and generates embeddings using a BERT model.

        Parameters:
        - data (Union[str, Any]): Input data, expected to be a single string or batch of strings.

        Returns:
        - List[IDocument]: A list containing a single IDocument instance with BERT embeddings as content.
        """
        
        # Tokenization
        inputs = self.tokenizer(data, return_tensors='pt', padding=True, truncation=True, max_length=512)

        # Generate embeddings
        with torch.no_grad():
            outputs = self._model(**inputs)

        # Use the last hidden state as document embeddings (batch_size, sequence_length, hidden_size)
        embeddings = outputs.last_hidden_state
        
        # Convert to list of numpy arrays
        embeddings = embeddings.detach().cpu().numpy()
        
        # For simplicity, let's consider the mean of embeddings across tokens to represent the document
        doc_embeddings = embeddings.mean(axis=1)
        
        # Creating document object(s)
        documents = [Document(doc_id=str(i), content=emb, metadata={"source": "BERTEmbeddingParser"}) for i, emb in enumerate(doc_embeddings)]
        
        return documents