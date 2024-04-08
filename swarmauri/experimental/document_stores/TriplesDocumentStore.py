from typing import List, Union, Optional
import numpy as np
from rdflib import Graph, URIRef, Literal, BNode
from ampligraph.latent_features import ComplEx
from ampligraph.evaluation import train_test_split_no_unseen
from ampligraph.latent_features import EmbeddingModel
from ampligraph.utils import save_model, restore_model

from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.standard.vectorizers.concrete.AmpligraphVectorizer import AmpligraphVectorizer


class TriplesDocumentStore(IDocumentStore, IRetriever):
    def __init__(self, rdf_file_path: str, model_path: Optional[str] = None):
        """
        Initializes the TriplesDocumentStore.
        """
        self.graph = Graph()
        self.rdf_file_path = rdf_file_path
        self.graph.parse(rdf_file_path, format='turtle')
        self.documents = []
        self.vectorizer = AmpligraphVectorizer()
        self.model_path = model_path
        if model_path:
            self.model = restore_model(model_path)
        else:
            self.model = None
        self.metric = CosineDistance()
        self._load_documents()
        if not self.model:
            self._train_model()

    def _train_model(self):
        """
        Trains a model based on triples in the graph.
        """
        # Extract triples for embedding model
        triples = np.array([[str(s), str(p), str(o)] for s, p, o in self.graph])
        # Split data
        train, test = train_test_split_no_unseen(triples, test_size=0.1)
        self.model = ComplEx(batches_count=100, seed=0, epochs=20, k=150, eta=1,
                             optimizer='adam', optimizer_params={'lr': 1e-3},
                             loss='pairwise', regularizer='LP', regularizer_params={'p': 3, 'lambda': 1e-5},
                             verbose=True)
        self.model.fit(train)
        if self.model_path:
            save_model(self.model, self.model_path)

    def _load_documents(self):
        """
        Load documents into the store from the RDF graph.
        """
        for subj, pred, obj in self.graph:
            doc_id = str(hash((subj, pred, obj)))
            content = f"{subj} {pred} {obj}"
            document = Document(content=content, doc_id=doc_id, metadata={})
            self.documents.append(document)

    def add_document(self, document: IDocument) -> None:
        """
        Adds a single RDF triple document.
        """
        subj, pred, obj = document.content.split()  # Splitting content into RDF components
        self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.append(document)
        self._train_model()

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Adds multiple RDF triple documents.
        """
        for document in documents:
            subj, pred, obj = document.content.split()  # Assuming each document's content is "subj pred obj"
            self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.extend(documents)
        self._train_model()

    # Implementation for get_document, get_all_documents, delete_document, update_document remains same as before
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve documents similar to the query string.
        """
        if not self.model:
            self._train_model()
        query_vector = self.vectorizer.infer_vector(model=self.model, samples=[query])[0]
        document_vectors = [self.vectorizer.infer_vector(model=self.model, samples=[doc.content])[0] for doc in self.documents]
        similarities = self.metric.distances(SimpleVector(data=query_vector), [SimpleVector(vector) for vector in document_vectors])
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]