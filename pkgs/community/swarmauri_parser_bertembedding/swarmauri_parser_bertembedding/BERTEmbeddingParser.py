from typing import List, Union, Any, Literal

from swarmauri_core.ComponentBase import ComponentBase
from transformers import BertTokenizer, BertModel
import torch
from pydantic import ConfigDict, PrivateAttr
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase


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
    model_config = ConfigDict(arbitrary_types_allowed=True)

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

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Tokenizes input data and generates embeddings using a BERT model.

        Parameters:
        - data (Union[str, Any]): Input data, expected to be a single string or batch of strings.

        Returns:
        - List[IDocument]: A list containing a single IDocument instance with BERT embeddings as content.
        """
        if data is None or not data:
            raise ValueError("Input data cannot be None.")

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
        documents = [
            Document(id=str(i), content=emb, metadata={"source": "BERTEmbeddingParser"})
            for i, emb in enumerate(doc_embeddings)
        ]

        return documents
