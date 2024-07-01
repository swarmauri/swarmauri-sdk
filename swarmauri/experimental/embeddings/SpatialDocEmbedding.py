import torch
from transformers import BertTokenizer, BertModel
from torch import nn
import numpy as np
from typing import Literal
from pydantic import PrivateAttr

from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class SpatialDocEmbedding(EmbeddingBase):
    _special_tokens_dict = PrivateAttr()
    _tokenizer = PrivateAttr()
    _model = PrivateAttr()
    _device = PrivateAttr()
    type: Literal['SpatialDocEmbedding'] = 'SpatialDocEmbedding'
    
    def __init__(self, special_tokens_dict=None, **kwargs):
        super().__init__(**kwargs)
        self._special_tokens_dict = special_tokens_dict or {
            'additional_special_tokens': [
                '[DIR]', '[TYPE]', '[SECTION]', '[PATH]',
                '[PARAGRAPH]', '[SUBPARAGRAPH]', '[CHAPTER]', '[TITLE]', '[SUBSECTION]'
            ]
        }
        self._tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self._tokenizer.add_special_tokens(self._special_tokens_dict)
        self._model = BertModel.from_pretrained('bert-base-uncased', return_dict=True)
        self._model.resize_token_embeddings(len(self._tokenizer))
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model.to(self._device)

    def add_metadata(self, text, metadata_dict):
        metadata_components = []
        for key, value in metadata_dict.items():
            if f"[{key.upper()}]" in self._special_tokens_dict['additional_special_tokens']:
                token = f"[{key.upper()}={value}]"
                metadata_components.append(token)
        metadata_str = ' '.join(metadata_components)
        return metadata_str + ' ' + text if metadata_components else text

    def tokenize_and_encode(self, text):
        inputs = self._tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        # Move the input tensors to the same device as the model
        inputs = {key: value.to(self._device) for key, value in inputs.items()}
        outputs = self._model(**inputs)
        return outputs.pooler_output

    def enhance_embedding_with_positional_info(self, embeddings, doc_position, total_docs):
        position_effect = torch.sin(torch.tensor(doc_position / total_docs, dtype=torch.float))
        enhanced_embeddings = embeddings + position_effect
        return enhanced_embeddings

    def vectorize_document(self, chunks, metadata_list=None):
        all_embeddings = []
        total_chunks = len(chunks)
        if not metadata_list:
            # Default empty metadata if none provided
            metadata_list = [{} for _ in chunks]
        
        for i, (chunk, metadata) in enumerate(zip(chunks, metadata_list)):
            # Use add_metadata to include any available metadata dynamically
            embedded_text = self.add_metadata(chunk, metadata)
            embeddings = self.tokenize_and_encode(embedded_text)
            enhanced_embeddings = self.enhance_embedding_with_positional_info(embeddings, i, total_chunks)
            all_embeddings.append(enhanced_embeddings)

        return all_embeddings



    def fit(self, data):
        # Although this vectorizer might not need to be fitted in the traditional sense,
        # this method placeholder allows integration into pipelines that expect a fit method.
        pass

    def transform(self, data):
        print(data)
        if isinstance(data, list):
            return [self.infer_vector(text).value for text in data]
        else:
            return self.infer_vector(data).value

    def fit_transform(self, data):
        #self.fit(data)
        return self.transform(data)

    def infer_vector(self, data, *args, **kwargs):
        print(data)
        inputs = self.tokenize_and_encode(data)
        print(inputs)
        inputs = inputs.cpu().detach().numpy().tolist()
        print(inputs)
        return Vector(value=[1,2,3]) # Placeholder

    def save_model(self, path):
        torch.save({
            'model_state_dict': self._model.state_dict(),
            'tokenizer': self._tokenizer
        }, path)
    
    def load_model(self, path):
        checkpoint = torch.load(path)
        self._model.load_state_dict(checkpoint['model_state_dict'])
        self._tokenizer = checkpoint['tokenizer']

    def extract_features(self, text):
        inputs = self.tokenize_and_encode(text)
        return Vector(value=inputs.cpu().detach().numpy().tolist())

