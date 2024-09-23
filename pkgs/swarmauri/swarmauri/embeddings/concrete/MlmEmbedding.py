from typing import List, Union, Any, Literal
import logging
from pydantic import PrivateAttr
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from swarmauri.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.vectors.concrete.Vector import Vector

class MlmEmbedding(EmbeddingBase):
    """
    EmbeddingBase implementation that fine-tunes a Masked Language Model (MLM).
    """

    embedding_name: str = 'bert-base-uncased'
    batch_size: int = 32
    learning_rate: float = 5e-5
    masking_ratio: float = 0.15
    randomness_ratio: float = 0.10
    epochs: int = 0
    add_new_tokens: bool = False
    _tokenizer = PrivateAttr()
    _model = PrivateAttr()
    _device = PrivateAttr()
    _mask_token_id = PrivateAttr()        
    type: Literal['MlmEmbedding'] = 'MlmEmbedding'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tokenizer = AutoTokenizer.from_pretrained(self.embedding_name)
        self._model = AutoModelForMaskedLM.from_pretrained(self.embedding_name)
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model.to(self._device)
        self._mask_token_id = self._tokenizer.convert_tokens_to_ids([self._tokenizer.mask_token])[0]

    def extract_features(self) -> List[str]:
        """
        Extracts the tokens from the vocabulary of the fine-tuned MLM.

        Returns:
        - List[str]: A list of token strings in the model's vocabulary.
        """
        # Get the vocabulary size
        vocab_size = len(self._tokenizer)
        
        # Retrieve the token strings for each id in the vocabulary
        token_strings = [self._tokenizer.convert_ids_to_tokens(i) for i in range(vocab_size)]
        
        return token_strings

    def _mask_tokens(self, encodings):
        input_ids = encodings.input_ids.to(self._device)
        attention_mask = encodings.attention_mask.to(self._device)

        labels = input_ids.detach().clone()

        probability_matrix = torch.full(labels.shape, self.masking_ratio, device=self._device)
        special_tokens_mask = [
            self._tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool, device=self._device), value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()

        labels[~masked_indices] = -100
        
        indices_replaced = torch.bernoulli(torch.full(labels.shape, self.masking_ratio, device=self._device)).bool() & masked_indices
        input_ids[indices_replaced] = self._mask_token_id

        indices_random = torch.bernoulli(torch.full(labels.shape, self.randomness_ratio, device=self._device)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self._tokenizer), labels.shape, dtype=torch.long, device=self._device)
        input_ids[indices_random] = random_words[indices_random]

        return input_ids, attention_mask, labels

    def fit(self, documents: List[Union[str, Any]]):
        # Check if we need to add new tokens
        if self.add_new_tokens:
            new_tokens = self.find_new_tokens(documents)
            if new_tokens:
                num_added_toks = self._tokenizer.add_tokens(new_tokens)
                if num_added_toks > 0:
                    logging.info(f"Added {num_added_toks} new tokens.")
                    self.model.resize_token_embeddings(len(self._tokenizer))

        encodings = self._tokenizer(documents, return_tensors='pt', padding=True, truncation=True, max_length=512)
        input_ids, attention_mask, labels = self._mask_tokens(encodings)
        optimizer = AdamW(self._model.parameters(), lr=self.learning_rate)
        dataset = TensorDataset(input_ids, attention_mask, labels)
        data_loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self._model.train()
        for batch in data_loader:
            batch = {k: v.to(self._device) for k, v in zip(['input_ids', 'attention_mask', 'labels'], batch)}
            outputs = self._model(**batch)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        self.epochs += 1
        logging.info(f"Epoch {self.epochs} complete. Loss {loss.item()}")

    def find_new_tokens(self, documents):
        # Identify unique words in documents that are not in the tokenizer's vocabulary
        unique_words = set()
        for doc in documents:
            tokens = set(doc.split())  # Simple whitespace tokenization
            unique_words.update(tokens)
        existing_vocab = set(self._tokenizer.get_vocab().keys())
        new_tokens = list(unique_words - existing_vocab)
        return new_tokens if new_tokens else None

    def transform(self, documents: List[Union[str, Any]]) -> List[Vector]:
        """
        Generates embeddings for a list of documents using the fine-tuned MLM.
        """
        self._model.eval()
        embedding_list = []
        
        for document in documents:
            inputs = self._tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self._model(**inputs)
            # Extract embedding (for simplicity, averaging the last hidden states)
            if hasattr(outputs, 'last_hidden_state'):
                embedding = outputs.last_hidden_state.mean(1)
            else:
                # Fallback or corrected attribute access
                embedding = outputs['logits'].mean(1)
            embedding = embedding.cpu().numpy()
            embedding_list.append(Vector(value=embedding.squeeze().tolist()))

        return embedding_list

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[Vector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: Union[str, Any], *args, **kwargs) -> Vector:
        """
        Generates an embedding for the input data.

        Parameters:
        - data (Union[str, Any]): The input data, expected to be a textual representation.
                                  Could be a single string or a batch of strings.
        """
        # Tokenize the input data and ensure the tensors are on the correct device.
        self._model.eval()
        inputs = self._tokenizer(data, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        # Generate embeddings using the model
        with torch.no_grad():
            outputs = self._model(**inputs)

        if hasattr(outputs, 'last_hidden_state'):
            # Access the last layer and calculate the mean across all tokens (simple pooling)
            embedding = outputs.last_hidden_state.mean(dim=1)
        else:
            embedding = outputs['logits'].mean(1)
        # Move the embeddings back to CPU for compatibility with downstream tasks if necessary
        embedding = embedding.cpu().numpy()

        return Vector(value=embedding.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the model and tokenizer to the specified directory.
        """
        self._model.save_pretrained(path)
        self._tokenizer.save_pretrained(path)

    def load_model(self, path: str) -> None:
        """
        Loads the model and tokenizer from the specified directory.
        """
        self._model = AutoModelForMaskedLM.from_pretrained(path)
        self._tokenizer = AutoTokenizer.from_pretrained(path)
        self._model.to(self._device)  # Ensure the model is loaded to the correct device