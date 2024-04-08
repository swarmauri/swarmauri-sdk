from typing import List, Union, Any, Optional
import torch
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from transformers import BertTokenizer, BertModel, BertForSequenceClassification, AdamW
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class BERTEmbeddingVectorizer(IVectorize, IFeature):
    def __init__(self, model_name: str = 'bert-base-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()

    def extract_features(self):
        raise NotImplementedError('Extract_features not implemented on BERTEmbeddingVectorizer.')

    def fit(self, documents: List[str], epochs: int = 4, batch_size: int = 8, learning_rate: float = 2e-5):

        # Tokenize and prepare input dat
        input_ids = []
        attention_masks = []

        for doc in documents:
            encoded_dict = self.tokenizer.encode_plus(doc, add_special_tokens=True, max_length=64, pad_to_max_length=True, return_attention_mask=True, return_tensors='pt',)
            input_ids.append(encoded_dict['input_ids'])
            attention_masks.append(encoded_dict['attention_mask'])
            
        # Convert lists into tensors
        input_ids = torch.cat(input_ids, dim=0)
        attention_masks = torch.cat(attention_masks, dim=0)
        labels = torch.tensor(labels)

        # Create the DataLoader
        dataset = TensorDataset(input_ids, attention_masks, labels)
        dataloader = DataLoader(dataset, sampler=RandomSampler(dataset), batch_size=batch_size)

        # Prepare model for training
        self.model.train()
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        # Training loop
        for _ in range(epochs):
            for batch in dataloader:
                b_input_ids, b_input_mask, b_labels = batch
                self.model.zero_grad()
                
                # Perform a forward pass
                outputs = self.model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
                loss = outputs[0]
                
                # Backward pass to calculate the gradients
                loss.backward()
                
                # Update the parameters
                optimizer.step()
                
    def transform(self, documents: List[str]) -> List[IVector]:
        vectors = []
        for document in documents:
            inputs = self.tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(1)
                vectors.append(SimpleVector(embeddings.squeeze().tolist()))
        return vectors

    def infer_vector(self, document: Union[str, Any]) -> IVector:
        inputs = self.tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(1)
            return SimpleVector(embeddings.squeeze().tolist())
        
