import numpy as np

import torch
from torch import nn
from transformers import BertTokenizer, BertModel

from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel


class SpatialDocVectorizer(nn.Module, IVectorize, ISaveModel, IFeature):
    def __init__(self, special_tokens_dict=None):
        self.special_tokens_dict = special_tokens_dict or {
            'additional_special_tokens': ['[DIR]', '[TYPE]', '[SECTION]', '[PATH]']
        }
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.tokenizer.add_special_tokens(self.special_tokens_dict)
        self.model = BertModel.from_pretrained('bert-base-uncased', return_dict=True)
        self.model.resize_token_embeddings(len(self.tokenizer))

    def add_metadata(self, text, section_header, file_path, doc_type):
        dir_token = f"[DIR={file_path.split('/')[-2]}]"
        doc_type_token = f"[TYPE={doc_type}]"
        metadata_str = f"{dir_token} {doc_type_token} [SECTION={section_header}] [PATH={file_path}] "
        return metadata_str + text

    def tokenize_and_encode(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = self.model(**inputs)
        return outputs.pooler_output

    def enhance_embedding_with_positional_info(self, embeddings, doc_position, total_docs):
        position_effect = torch.sin(torch.tensor(doc_position / total_docs, dtype=torch.float))
        enhanced_embeddings = embeddings + position_effect
        return enhanced_embeddings

    def vectorize_document(self, chunks, section_headers, file_paths, doc_types):
        all_embeddings = []
        total_chunks = len(chunks)
        for i, (chunk, header, path, doc_type) in enumerate(zip(chunks, section_headers, file_paths, doc_types)):
            embedded_text = self.add_metadata(chunk, header, path, doc_type)
            embeddings = self.tokenize_and_encode(embedded_text)
            enhanced_embeddings = self.enhance_embedding_with_positional_info(embeddings, i, total_chunks)
            all_embeddings.append(enhanced_embeddings)
        document_embedding = torch.mean(torch.stack(all_embeddings), dim=0)
        return SimpleVector(data=document_embedding.detach().numpy().tolist())

    def vectorize(self, text):
        inputs = self.tokenize_and_encode(text)
        return SimpleVector(data=inputs.cpu().detach().numpy().tolist())

    def fit(self, data):
        # Although this vectorizer might not need to be fitted in the traditional sense,
        # this method placeholder allows integration into pipelines that expect a fit method.
        return self

    def transform(self, data):
        if isinstance(data, list):
            return [self.vectorize(text).data for text in data]
        else:
            return self.vectorize(data).data

    def fit_transform(self, data):
        self.fit(data)
        return self.transform(data)

    def infer_vector(self, data, *args, **kwargs):
        return self.vectorize(data)

    def save_model(self, path):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'tokenizer': self.tokenizer
        }, path)
    
    def load_model(self, path):
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.tokenizer = checkpoint['tokenizer']

    def extract_feature(self, text):
        inputs = self.tokenize_and_encode(text)
        return SimpleVector(data=inputs.cpu().detach().numpy().tolist())