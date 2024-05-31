import os
from typing import List, Union
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

from swarmauri.standard.vectorizers.concrete.Doc2VecVectorizer import Doc2VecVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.documents.concrete.Document import Document
import chromadb

class ChromaDBVectorStore(VectorDocumentStoreRetrieveBase, SaveLoadStoreBase):
    def __init__(self, db_name):
        self.vectorizer = Doc2VecVectorizer()
        self.metric = CosineDistance()
        self.db_name = db_name
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=db_name)
        SaveLoadStoreBase.__init__(self, self.vectorizer, [])

    def add_document(self, document: IDocument) -> None:
        try:
            embedding = self.vectorizer.infer_vector(document.content).data
            self.collection.add(ids=[document.id],
                    documents=[document.content], 
                    embeddings=[embedding], 
                    metadatas=[document.metadata] )
        except:
            texts = [document.content]
            self.vectorizer.fit_transform(texts)
            embedding = self.vectorizer.infer_vector(document.content).data
            self.collection.add(ids=[document.id],
                                documents=[document.content], 
                                embeddings=[embedding], 
                                metadatas=[document.metadata] )
            

    def add_documents(self, documents: List[IDocument]) -> None:
        ids = [doc.id for doc in documents]
        texts = [doc.content for doc in documents]
        embeddings = [self.vectorizer.infer_vector(doc.content).data for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        self.collection.add(ids=ids,
                            documents=texts, 
                            embeddings=embeddings, 
                            metadatas=metadatas)

    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        try:
            results = self.collection.get(ids=[doc_id])
            document = Document(id=results['ids'][0],
                             content=results['documents'][0],
                                 metadata=results['metadatas'][0])
        except Exception as e:
            print(str(e))
            document = None
        return document if document else []

    def get_all_documents(self) -> List[IDocument]:
        try:
            results = self.collection.get()
            print(results)
            return [Document(id=results['ids'][idx],
                                 content=results['documents'][idx],
                                 metadata=results['metadatas'][idx])
                    for idx, value in enumerate(results['ids'])]
        except Exception as e:
            print(str(e))
            document = None
        return document if document else []
            

    def delete_document(self, doc_id: str) -> None:
        self.collection.delete(ids=[doc_id])

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        self.delete_document(doc_id)
        self.add_document(updated_document)

    def clear_documents(self) -> None:
        self.client.delete_collection(self.db_name)

    def document_count(self) -> int:
        try:
            return len(self.get_all_documents())
        except StopIteration:
            return 0

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        embedding = self.vectorizer.infer_vector(query).data
        results = self.collection.query(query_embeddings=embedding,
                                        n_results=top_k)
        print('retrieve reults', results)
        print(results['ids'][0])
        documents = []
        for idx in range(len(results['ids'])):
            documents.append(Document(id=results['ids'][idx],
                             content=results['documents'][idx],
                             metadata=results['metadatas'][idx]))
        return documents