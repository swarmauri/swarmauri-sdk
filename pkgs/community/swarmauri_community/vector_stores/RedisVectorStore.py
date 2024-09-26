import json
from typing import List, Union, Literal, Dict

# import sys
# sys.path.append(r"C:\Users\Ishaan\Desktop\swarmauri\swarmauri-sdk\pkgs\swarmauri")

import numpy as np
import redis
from redis.commands.search.field import VectorField, TextField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.documents.concrete.Document import Document
from swarmauri.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding  # or your specific embedder
from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin


class RedisVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal["RedisVectorStore"] = "RedisVectorStore"
    index_name: str = "documents_index"
    embedding_dimension: int = 8000

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: str = None,
        embedding_dimension: int = 8000,  # Adjust based on your embedder
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._embedder = Doc2VecEmbedding()  # Replace with your specific embedder if different
        self.embedding_dimension = embedding_dimension

        # Initialize Redis client
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=False  # For binary data
        )
        
        self.redis_client.ft(self.index_name).dropindex(delete_documents=False)
        vector_field = VectorField(
            "embedding",
            "FLAT",
            {
                "TYPE": "FLOAT32",
                "DIM": self.embedding_dimension,
                "DISTANCE_METRIC": "COSINE"
            }
        )
        text_field = TextField("content")
        
        try:
            from redis.commands.search import Search
            self.redis_client.ft(self.index_name).info()
        except redis.exceptions.ResponseError:
            schema = (
                text_field,
                vector_field
            )
            definition = IndexDefinition(
                prefix=["doc:"],
                index_type=IndexType.HASH
            )
            self.redis_client.ft(self.index_name).create_index(
                fields=schema,
                definition=definition
            )

    def _doc_key(self, document_id: str) -> str:
        return f"doc:{document_id}"

    def add_document(self, document: Document) -> None:
        doc = document
        pipeline = self.redis_client.pipeline()
    
            # Embed the document content
        embedding = self._embedder.fit_transform([doc.content])[0]

        if isinstance(embedding, Vector):
            embedding = embedding.value 
        metadata = doc.metadata
               
        # print("METADATA ::::::::::::::::::::", metadata)
        doc_key = self._doc_key(doc.id)
        # print("DOC KEY ::::::::::::::::::::", doc_key)
        pipeline.hset(doc_key, mapping={
            "content": doc.content,
            "metadata": json.dumps(metadata),  # Store metadata as JSON
            "embedding": np.array(embedding, dtype=np.float32).tobytes()  # Convert embedding values to bytes
        })
        add = pipeline.execute()

    def add_documents(self, documents: List[Document]) -> None:
        pipeline = self.redis_client.pipeline()
        for doc in documents:
            if not doc.content:
                continue
            # Embed the document content
            embedding = self._embedder.fit_transform([doc.content])[0]
            
            if isinstance(embedding, Vector):
                embedding = embedding.value
            metadata={doc.metadata}
           
            doc_key = self._doc_key(doc.id)
            pipeline.hset(doc_key, mapping={
                "content": doc.content,
                "metadata": json.dumps(metadata),
                "embedding": np.array(embedding, dtype=np.float32).tobytes()
            })
        pipeline.execute()

    def get_document(self, id: str) -> Union[Document, None]:
        
        doc_key = self._doc_key(id)
        data = self.redis_client.hgetall(doc_key)
        if not data:
            return None
        
        metadata_raw = data.get(b"metadata", b"{}").decode("utf-8")  
        metadata = json.loads(metadata_raw)

        content = data.get(b"content", b"").decode("utf-8")
        # print("METAAAAAAA ::::::::::::", metadata)

        embedding_bytes = data.get(b"embedding")
        if embedding_bytes:
            embedding = Vector(value=np.frombuffer(embedding_bytes, dtype=np.float32).tolist())
        else:
            embedding = None
        return Document(
            id=id,
            content=content,
            metadata=metadata,
            embedding=embedding
        )

    def get_all_documents(self) -> List[Document]:
        cursor = '0'
        documents = []
        while cursor != 0:
            cursor, keys = self.redis_client.scan(cursor=cursor, match="doc:*", count=1000)
            for key in keys:
                data = self.redis_client.hgetall(key)
                if not data:
                    continue
                doc_id = key.decode("utf-8").split("doc:")[1]
                metadata_raw = data.get(b"metadata", b"{}").decode("utf-8")  
                metadata = json.loads(metadata_raw)
                content = data.get(b"content", b"").decode("utf-8")
                embedding_bytes = data.get(b"embedding")
                if embedding_bytes:
                    embedding = Vector(value=np.frombuffer(embedding_bytes, dtype=np.float32).tolist())
                else:
                    embedding = None
                document = Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    embedding=embedding
                )
                documents.append(document)
        return documents

    def delete_document(self, id: str) -> None:
        doc_key = self._doc_key(id)
        self.redis_client.delete(doc_key)

    def update_document(self, document: Document) -> None:
        doc_key = self._doc_key(document.id)
        if not self.redis_client.exists(doc_key):
            raise ValueError(f"Document with id {document.id} does not exist.")
        # Update the document by re-adding it
        self.add_documents([document])
        

    def cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0
        return dot_product / (norm_vec1 * norm_vec2)


    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._embedder.infer_vector(query)
            
        all_documents = self.get_all_documents()
        # print("ALL DOCUMENTS ::::::::::::::::::::", all_documents[:10])
        similarities = []
        for doc in all_documents:
            if doc.embedding is not None:
                doc_vector = doc.embedding
                # print("DOC VECTOR ::::::::::::::::::::", doc_vector.value[:10])
                similarity = self.cosine_similarity(query_vector.value, doc_vector.value)
                similarities.append((doc, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        # print("SIMILARITIES ::::::::::::::::::::", similarities[:10])
        top_documents = [doc for doc, _ in similarities[:top_k]]
        # print(f"Found {len(top_documents)} similar documents.")
        return top_documents
        
    
    class Config:
        extra = 'allow'
