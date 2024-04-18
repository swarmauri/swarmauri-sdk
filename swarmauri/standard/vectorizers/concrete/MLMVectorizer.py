from typing import List, Union, Any
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel

class MLMVectorizer(IVectorize, IFeature, ISaveModel):
    """
    IVectorize implementation that fine-tunes a Masked Language Model (MLM).
    """

    def __init__(self, model_name='bert-base-uncased', 
        batch_size = 32, 
        learning_rate = 5e-5, 
        masking_ratio: float = 0.15, 
        randomness_ratio: float = 0.10,
        add_new_tokens: bool = False):
        """
        Initializes the vectorizer with a pre-trained MLM model and tokenizer for fine-tuning.
        
        Parameters:
        - model_name (str): Identifier for the pre-trained model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.epochs = 0
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.masking_ratio = masking_ratio
        self.randomness_ratio = randomness_ratio
        self.add_new_tokens = add_new_tokens
        self.mask_token_id = self.tokenizer.convert_tokens_to_ids([self.tokenizer.mask_token])[0]

    def extract_features(self):
        raise NotImplementedError('Extract_features not implemented on MLMVectorizer.')

    def _mask_tokens(self, encodings):
        input_ids = encodings.input_ids.to(self.device)
        attention_mask = encodings.attention_mask.to(self.device)

        labels = input_ids.detach().clone()

        probability_matrix = torch.full(labels.shape, self.masking_ratio, device=self.device)
        special_tokens_mask = [
            self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool, device=self.device), value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()

        labels[~masked_indices] = -100
        
        indices_replaced = torch.bernoulli(torch.full(labels.shape, self.masking_ratio, device=self.device)).bool() & masked_indices
        input_ids[indices_replaced] = self.mask_token_id

        indices_random = torch.bernoulli(torch.full(labels.shape, self.randomness_ratio, device=self.device)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long, device=self.device)
        input_ids[indices_random] = random_words[indices_random]

        return input_ids, attention_mask, labels

    def fit(self, documents: List[Union[str, Any]]):
        # Check if we need to add new tokens
        if self.add_new_tokens:
            new_tokens = self.find_new_tokens(documents)
            if new_tokens:
                num_added_toks = self.tokenizer.add_tokens(new_tokens)
                if num_added_toks > 0:
                    print(f"Added {num_added_toks} new tokens.")
                    self.model.resize_token_embeddings(len(self.tokenizer))

        encodings = self.tokenizer(documents, return_tensors='pt', padding=True, truncation=True, max_length=512)
        input_ids, attention_mask, labels = self._mask_tokens(encodings)
        optimizer = AdamW(self.model.parameters(), lr=self.learning_rate)
        dataset = TensorDataset(input_ids, attention_mask, labels)
        data_loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model.train()
        for batch in data_loader:
            batch = {k: v.to(self.device) for k, v in zip(['input_ids', 'attention_mask', 'labels'], batch)}
            outputs = self.model(**batch)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        self.epochs += 1
        print(f"Epoch {self.epochs} complete. Loss {loss.item()}")

    def find_new_tokens(self, documents):
        # Identify unique words in documents that are not in the tokenizer's vocabulary
        unique_words = set()
        for doc in documents:
            tokens = set(doc.split())  # Simple whitespace tokenization
            unique_words.update(tokens)
        existing_vocab = set(self.tokenizer.get_vocab().keys())
        new_tokens = list(unique_words - existing_vocab)
        return new_tokens if new_tokens else None

    def transform(self, documents: List[Union[str, Any]]) -> List[IVector]:
        """
        Generates embeddings for a list of documents using the fine-tuned MLM.
        """
        self.model.eval()
        embedding_list = []
        
        for document in documents:
            inputs = self.tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Extract embedding (for simplicity, averaging the last hidden states)
            if hasattr(outputs, 'last_hidden_state'):
                embedding = outputs.last_hidden_state.mean(1)
            else:
                # Fallback or corrected attribute access
                embedding = outputs['logits'].mean(1)
            embedding = embedding.cpu().numpy()
            embedding_list.append(SimpleVector(embedding.squeeze().tolist()))

        return embedding_list

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[IVector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: Union[str, Any], *args, **kwargs) -> IVector:
        """
        Generates an embedding for the input data.

        Parameters:
        - data (Union[str, Any]): The input data, expected to be a textual representation.
                                  Could be a single string or a batch of strings.
        """
        # Tokenize the input data and ensure the tensors are on the correct device.
        self.model.eval()
        inputs = self.tokenizer(data, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embeddings using the model
        with torch.no_grad():
            outputs = self.model(**inputs)

        if hasattr(outputs, 'last_hidden_state'):
            # Access the last layer and calculate the mean across all tokens (simple pooling)
            embedding = outputs.last_hidden_state.mean(dim=1)
        else:
            embedding = outputs['logits'].mean(1)
        # Move the embeddings back to CPU for compatibility with downstream tasks if necessary
        embedding = embedding.cpu().numpy()

        return SimpleVector(embedding.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the model and tokenizer to the specified directory.
        """
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)

    def load_model(self, path: str) -> None:
        """
        Loads the model and tokenizer from the specified directory.
        """
        self.model = AutoModelForMaskedLM.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model.to(self.device)  # Ensure the model is loaded to the correct device