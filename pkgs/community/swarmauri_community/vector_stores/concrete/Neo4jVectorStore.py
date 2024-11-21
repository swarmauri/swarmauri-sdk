from typing import List, Union, Literal, Optional
from pydantic import BaseModel, PrivateAttr
from neo4j import GraphDatabase
import json

from swarmauri.documents.concrete.Document import Document
from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)



class Neo4jVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase, BaseModel):
    type: Literal['Neo4jVectorStore'] = 'Neo4jVectorStore'
    uri: str
    user: str
    password: str
    collection_name: Optional[str] = None

    # Private attributes are excluded from serialization by default
    _driver: Optional[GraphDatabase.driver] = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)

        self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self._initialize_schema()

    def _initialize_schema(self):
        """
        Initialize the Neo4j schema, creating necessary indexes and constraints.
        """
        
        with self._driver.session() as session:
            # Create a unique constraint on Document ID with a specific constraint name

            session.run(
                """
            CREATE CONSTRAINT unique_document_id IF NOT EXISTS
            FOR (d:Document)
            REQUIRE d.id IS UNIQUE
        """
            )


    def add_document(self, document: Document) -> None:
        """
        Add a single document to the Neo4j store.

        :param document: Document to add
        """
       
        with self._driver.session() as session:
            session.run(
                """
                MERGE (d:Document {id: $id})
                SET d.content = $content,
                    d.metadata = $metadata

            """,
                id=document.id,
                content=document.content,
                metadata=json.dumps(document.metadata),
            )


    def add_documents(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the Neo4j store.

        :param documents: List of documents to add
        """

        with self._driver.session() as session:
            for document in documents:
                session.run(
                    """
                    MERGE (d:Document {id: $id})
                    SET d.content = $content,
                        d.metadata = $metadata

                """,
                    id=document.id,
                    content=document.content,
                    metadata=json.dumps(document.metadata),
                )


    def get_document(self, id: str) -> Union[Document, None]:
        """
        Retrieve a document by its ID.

        :param id: Document ID
        :return: Document object or None if not found
        """
        
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (d:Document {id: $id})
                RETURN d.id AS id, d.content AS content, d.metadata AS metadata
            """,
                id=id,
            ).single()
            if result:
                return Document(
                    id=result["id"],
                    content=result["content"],
                    metadata=json.loads(result["metadata"]),
                )
            return None


    def get_all_documents(self) -> List[Document]:
        """
        Retrieve all documents from the Neo4j store.

        :return: List of Document objects
        """
        with self._driver.session() as session:
            results = session.run(
                """
                MATCH (d:Document)
                RETURN d.id AS id, d.content AS content, d.metadata AS metadata
            """
            )
            documents = []
            for record in results:
                documents.append(
                    Document(
                        id=record["id"],
                        content=record["content"],
                        metadata=json.loads(record["metadata"]),
                    )
                )
            return documents


    def delete_document(self, id: str) -> None:
        """
        Delete a document by its ID.

        :param id: Document ID
        """

        with self._driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $id})
                DETACH DELETE d
            """,
                id=id,
            )


    def update_document(self, id: str, updated_document: Document) -> None:
        """
        Update an existing document.

        :param id: Document ID
        :param updated_document: Document object with updated data
        """

        with self._driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $id})
                SET d.content = $content,
                    d.metadata = $metadata

            """,
                id=id,
                content=updated_document.content,
                metadata=json.dumps(updated_document.metadata),
            )

    def retrieve(
        self, query: str, top_k: int = 5, string_field: str = "content"
    ) -> List[Document]:

        """
        Retrieve the top_k most similar documents to the query based on Levenshtein distance using APOC's apoc.text.distance.

        :param query: Query string
        :param top_k: Number of top similar documents to retrieve
        :param string_field: Specific field to apply Levenshtein distance (default: 'content')
        :return: List of Document objects
        """

        input_text = query

        with self._driver.session() as session:
            cypher_query = f"""
                MATCH (d:Document)
                RETURN d.id AS id, d.content AS content, d.metadata AS metadata,
                        apoc.text.distance(d.{string_field}, $input_text) AS distance
                ORDER BY distance ASC
                LIMIT $top_k
            """
            results = session.run(cypher_query, input_text=input_text, top_k=top_k)

            documents = []
            for record in results:
                documents.append(
                    Document(
                        id=record["id"],
                        content=record["content"],
                        metadata=json.loads(record["metadata"]),
                    )
                )
            return documents

    def close(self):
        """
        Close the Neo4j driver connection.
        """

        if self._driver:
            self._driver.close()


    def __del__(self):
        self.close()


