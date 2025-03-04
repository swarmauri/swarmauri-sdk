from typing import Any, List, Literal, Union

import torch
from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument
from transformers import BertModel, BertTokenizer

from swarmauri_standard.documents.Document import Document


@ComponentBase.register_type(ParserBase, "BERTEmbeddingParser")
class BERTEmbeddingParser(ParserBase):
    """
    A parser that transforms input text into document embeddings using BERT.

    This parser tokenizes the input text, passes it through a pre-trained BERT model,
    and uses the resulting embeddings as the document content.
    """

    parser_model_name: str = "bert-base-uncased"
    _model: Any = PrivateAttr()
    type: Literal["BERTEmbeddingParser"] = "BERTEmbeddingParser"
    _tokenizer: Any = PrivateAttr()

    def __init__(self, **kwargs):
        """
        Initializes the BERTEmbeddingParser with a specific BERT model.

        Parameters:
        - model_name (str): The name of the pre-trained BERT model to use.
        """
        super().__init__(**kwargs)
        self._tokenizer = BertTokenizer.from_pretrained(self.parser_model_name)
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
        inputs = self._tokenizer(
            data, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

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
        documents = []
        for i, emb in enumerate(doc_embeddings):
            # Store the original input text as content and embeddings in metadata
            input_text = data[i] if isinstance(data, list) else data
            doc = Document(content=input_text)
            # Add the embedding and source to metadata
            doc.metadata = {"source": "BERTEmbeddingParser", "embedding": emb}
            # Set an ID if needed in your application
            doc.id = str(i)
            documents.append(doc)

        return documents
