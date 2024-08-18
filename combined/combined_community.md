```swarmauri/community/__init__.py



```

```swarmauri/community/tools/__init__.py



```

```swarmauri/community/tools/base/__init__.py



```

```swarmauri/community/tools/concrete/__init__.py



```

```swarmauri/community/tools/concrete/EntityRecognitionTool.py

import json
from transformers import pipeline, logging as hf_logging
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

hf_logging.set_verbosity_error()

class EntityRecognitionTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter("text","string","The text for entity recognition",True)
        ]
        super().__init__(name="EntityRecognitionTool", 
                         description="Extracts named entities from text", 
                         parameters=parameters)
        

    def __call__(self, text: str) -> dict:
        try:
            self.nlp = pipeline("ner")
            entities = self.nlp(text)
            organized_entities = {}
            for entity in entities:
                if entity['entity'] not in organized_entities:
                    organized_entities[entity['entity']] = []
                organized_entities[entity['entity']].append(entity['word'])
            return json.dumps(organized_entities)
        except Exception as e:
            raise e
        finally:
            del self.nlp

```

```swarmauri/community/tools/concrete/GmailSendTool.py

import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient.discovery import build
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class GmailSendTool(ToolBase):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, credentials_path: str, sender_email: str):
        """
        Initializes the GmailSendTool with a path to the credentials JSON file and the sender email.

        Parameters:
        credentials_path (str): The path to the Gmail service JSON file.
        sender_email (str): The email address being used to send emails.
        """
        
        parameters = [
            Parameter(
                name="recipients",
                type="string",
                description="The email addresses of the recipients, separated by commas",
                required=True
            ),
            Parameter(
                name="subject",
                type="string",
                description="The subject of the email",
                required=True
            ),
            Parameter(
                name="htmlMsg",
                type="string",
                description="The HTML message to be sent as the email body",
                required=True
            )
        ]
        
        super().__init__(name="GmailSendTool", 
                         description="Sends an email using the Gmail API.",
                         parameters=parameters)
        self.credentials_path = credentials_path
        self.sender_email = sender_email
        

    def authenticate(self):
        """
        Authenticates the user and creates a Gmail API service for sending emails.
        """
        credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES)
        
        delegated_credentials = credentials.with_subject(self.sender_email)
        self.service = build('gmail', 'v1', credentials=delegated_credentials)

    def create_message(self, to: str, subject: str, message_text: str):
        """
        Create a MIMEText message for sending an email.

        Parameters:
        sender (str): The email address of the sender.
        to (str): The email address of the recipient.
        subject (str): The subject of the email.
        message_text (str): The HTML body of the email.

        Returns:
        The created MIMEText message.
        """
        message = MIMEMultipart('alternative')
        message['from'] = self.sender_email
        message['to'] = to
        message['subject'] = subject
        mime_text = MIMEText(message_text, 'html')
        message.attach(mime_text)
        raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8')}

    def __call__(self, recipients, subject, htmlMsg):
        """
        Sends an email to the specified recipients with the given subject and HTML message.
        
        Parameters:
        sender (str): The email address of the sender.
        recipients (str): The email address of the recipients, separated by commas.
        subject (str): The subject of the email.
        htmlMsg (str): The HTML content of the email body.

        Returns:
        The result of sending the email or an error message if the operation fails.
        """
        self.authenticate()
        try:
            message = self.create_message(recipients, subject, htmlMsg)
            sent_message = (self.service.users().messages().send(userId='me', body=message).execute())
            return f"Email sent successfully to {recipients}"

        except Exception as e:
            return f"An error occurred in sending the email: {e}"
        finally:
            del self.service

```

```swarmauri/community/tools/concrete/GmailReadTool.py

import base64
import json
from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient.discovery import build
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class GmailReadTool(ToolBase):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, credentials_path: str, sender_email: str):
        """
        Initializes the GmailReadTool with a path to the credentials JSON file.

        Parameters:
        credentials_path (str): The path to the Gmail service JSON file.
        """
        
        parameters = [
            Parameter(
                name="query",
                type="string",
                description='''The query to filter emails. For example, "is:unread" or "from:example@gmail.com" or "from:sender@company.com"''',
                required=True
            ),
            Parameter(
                name="max_results",
                type="integer",
                description='''The number of emails to return. Defaults to 10.'''
            )
        ]
        
        
        super().__init__(name="GmailReadTool", 
                         description="Read emails from a Gmail account.", 
                         parameters = parameters)
        self.credentials_path = credentials_path
        self.sender_email = sender_email
        

    def authenticate(self):
        """
        Authenticates the user and creates a Gmail API service.
        """
        credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES)
        
        delegated_credentials = credentials.with_subject(self.sender_email)
        self.service = discovery.build('gmail', 'v1', credentials=delegated_credentials)



    def __call__(self, query='', max_results=10):
        """
        Fetches emails from the authenticated Gmail account based on the given query.

        Parameters:
        query (str): The query to filter emails. For example, "is:unread".
        max_results (int): The maximum number of email messages to fetch.

        Returns:
        list: A list of email messages.
        """
        self.authenticate()
        try:
            # Call the Gmail API
            
            gmail_messages = self.service.users().messages()
            results = gmail_messages.list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            message_data = ""
            for message in messages:
                
                msg = gmail_messages.get(userId='me', id=message['threadId'], format="full").execute()
                headers = msg['payload']['headers']
                
                sender = next(header['value'] for header in headers if header['name'] == 'From')
                subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                reply_to = next((header['value'] for header in headers if header['name'] == 'Reply-To'), subject)
                date_time = next(header['value'] for header in headers if header['name'] == 'Date')
                
                #part = msg['payload']['parts'][0]
                #data = part['body']['data']
                #decoded_data = base64.urlsafe_b64decode(data.encode('ASCII'))

                formatted_msg = f"\nsender:{sender} reply-to:{reply_to} subject: {subject} date_time:{date_time}"
                
                message_data += formatted_msg
                
            
            return message_data
        
        
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        
        finally:
            del self.service
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

```

```swarmauri/community/tools/concrete/SentimentAnalysisTool.py

from transformers import pipeline
from transformers import logging as hf_logging

from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

hf_logging.set_verbosity_error()

class SentimentAnalysisTool(ToolBase):
    def __init__(self):
        super().__init__("SentimentAnalysisTool", 
                         "Analyzes the sentiment of the given text.", 
                         parameters=[
                             Parameter("text", "string", "The text for sentiment analysis", True)
                         ])
        

    def __call__(self, text: str) -> str:
        try:
            self.analyzer = pipeline("sentiment-analysis")
            result = self.analyzer(text)
            return result[0]['label']
        except:
            raise
        finally:
            del self.analyzer

```

```swarmauri/community/tools/concrete/WebScrapingTool.py

import requests
from bs4 import BeautifulSoup
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class WebScrapingTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="URL of the link, website, webpage, etc... to scrape",
                required=True
            ),
            Parameter(
                name="selector",
                type="string",
                description="CSS selector to target specific elements",
                required=True
            )
        ]
        
        super().__init__(name="WebScrapingTool", 
                         description="This is a web scraping tool that you can utilize to scrape links, websites, webpages, etc... This tool uses python's requests and BeautifulSoup libraries to parse a URL using a CSS to target specific elements.", 
                         parameters=parameters)

    def __call__(self, url: str, selector: str) -> str:
        """
        Fetches content from the specified URL and extracts elements based on the provided CSS selector.
        
        Args:
            url (str): The URL of the webpage to scrape.
            selector (str): CSS selector to target specific elements in the webpage.

        Returns:
            str: Extracted text from the selector or an error message.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises HTTPError for bad requests (4xx or 5xx)

            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            elements = soup.select(selector)
            extracted_text = '\n'.join([element.text for element in elements])
            return extracted_text
        except requests.RequestException as e:
            return f"Request Exception: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

```

```swarmauri/community/tools/concrete/DownloadPdfTool.py

import requests
from typing import Dict
from pathlib import Path
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class DownloadPDFTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="The URL of the PDF file to download",
                required=True
            ),
            Parameter(
                name="destination",
                type="string",
                description="The path where the PDF file will be saved",
                required=True
            )
        ]
        
        super().__init__(name="DownloadPDFTool",
                         description="Downloads a PDF from a specified URL and saves it to a specified path.",
                         parameters=parameters)

    def __call__(self, url: str, destination: str) -> Dict[str, str]:
        """
        Download the PDF from the specified URL and saves it to the given destination path.

        Parameters:
        - url (str): The URL from where to download the PDF.
        - destination (str): The local file path where the PDF should be saved.
        
        Returns:
        - Dict[str, str]: A dictionary containing the result message and the destination path.
        """
        try:
            # Send a GET request to the specified URL
            response = requests.get(url, stream=True)

            # Raise an HTTPError if the status code is not 200 (OK)
            response.raise_for_status()

            # Ensure destination directory exists
            Path(destination).parent.mkdir(parents=True, exist_ok=True)

            # Open a file at the specified destination path and write the content of the response to it
            with open(Path(destination), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            return {
                "message": "PDF downloaded successfully.",
                "destination": destination
            }

        except requests.exceptions.RequestException as e:
            # Handle requests-related errors
            return {"error": f"Failed to download PDF: {e}"}
        except IOError as e:
            # Handle file I/O errors
            return {"error": f"Failed to save PDF: {e}"}

```

```swarmauri/community/tools/concrete/PaCMAP.py

import numpy as np
import pacmap  # Ensure pacmap is installed
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter
class PaCMAPTool(ToolBase):
    """
    A tool for applying the PaCMAP method for dimensionality reduction.
    """

    def __init__(self):
        parameters = [
            Parameter(
                name="X",
                type="object",
                description="X (np.ndarray): The high-dimensional data points to reduce.",
                required=True
            ),
            Parameter(
                name="n_neighbors",
                type="integer",
                description="The size of local neighborhood (in terms of number of neighboring data points) used for manifold approximation.",
                required=False
            ),
            Parameter(
                name="n_components",
                type="integer",
                description="The dimension of the space into which to embed the data.",
                required=True
            ),
            Parameter(
                name="n_iterations",
                type="integer",
                description="The number of iterations used for optimization.",
                required=False
            )
        ]
        
        super().__init__(name="PaCMAPTool", 
                         description="Applies PaCMAP for dimensionality reduction.", 
                         parameters=parameters)

    def __call__(self, **kwargs) -> np.ndarray:
        """
        Applies the PaCMAP algorithm on the provided dataset.

        Parameters:
        - kwargs: Additional keyword arguments for the PaCMAP algorithm.

        Returns:
        - np.ndarray: The reduced dimension data points.
        """
        # Set default values for any unspecified parameters
        X = kwargs.get('X')
        n_neighbors = kwargs.get('n_neighbors', 30)
        n_components = kwargs.get('n_components', 2)
        n_iterations = kwargs.get('n_iterations', 500)
        
        # Instantiate the PaCMAP instance with specified parameters
        embedder = pacmap.PaCMAP(n_neighbors=n_neighbors, n_components=n_components, 
                                 n_iters=n_iterations, **kwargs)
                                 
        # Fit the model and transform the data
        X_reduced = embedder.fit_transform(X)

        return X_reduced

```

```swarmauri/community/tools/concrete/ZapierHookTool.py

import json
import requests
from typing import Dict
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class ZapierHookTool(ToolBase):
    def __init__(self, auth_token, zap_id):
        parameters = [
            Parameter(
                name="payload",
                type="string",
                description="A Payload to send when triggering the Zapier webhook",
                required=True
            )
        ]
        super().__init__(name="ZapierTool", 
                         description="Tool to authenticate with Zapier and execute zaps.", 
                        parameters=parameters)
        self._auth_token = auth_token
        self._zap_id = zap_id

    def authenticate(self):
        """Set up the necessary headers for authentication."""
        self.headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json"
        }

    def execute_zap(self, payload: str):
        """Execute a zap with given payload.

        Args:
            zap_id (str): The unique identifier for the Zap to trigger.
            payload (dict): The data payload to send to the Zap.

        Returns:
            dict: The response from Zapier API.
        """
        self.authenticate()
        response = requests.post(f'https://hooks.zapier.com/hooks/catch/{self._zap_id}/',
                                     headers=self.headers, json={"data":payload})
        # Checking the HTTP response status for success or failure
        if response.status_code == 200:
            return json.dumps(response.json())
        else:
            response.raise_for_status()  # This will raise an error for non-200 responses

    def __call__(self, payload: str):
        """Enable the tool to be called with zap_id and payload directly."""
        return self.execute_zap(payload)

```

```swarmauri/community/retrievers/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/community/retrievers/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/community/retrievers/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/community/retrievers/concrete/RedisDocumentRetriever.py

from typing import List
from redisearch import Client, Query
from ....core.documents.IDocument import IDocument
from ....standard.document_stores.concrete.ConcreteDocument import ConcreteDocument
from ....standard.retrievers.base.DocumentRetrieverBase import DocumentRetrieverBase

class RedisDocumentRetriever(DocumentRetrieverBase):
    """
    A document retriever that fetches documents from a Redis store.
    """
    
    def __init__(self, redis_idx_name, redis_host, redis_port):
        """
        Initializes a new instance of RedisDocumentRetriever.

        Args:
            redis_client (Redis): An instance of the Redis client.
        """
        self._redis_client = None
        self._redis_idx_name = redis_idx_name
        self._redis_host = redis_host
        self._redis_port = redis_port

    @property
    def redis_client(self):
        """Lazily initialize and return the Redis client using a factory method."""
        if self._redis_client is None:
            self._redis_client = Client(self.redis_idx_name, host=self.redis_host, port=self.redis_port)
        return self._redis_client
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int, optional): The number of top relevant documents to retrieve. Defaults to 5.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        query_result = self.redis_client.search(Query(query).paging(0, top_k))
        
        documents = [
            ConcreteDocument(
                doc_id=doc.id,
                content=doc.text,  # Note: Adjust 'text' based on actual Redis document schema
                metadata=doc.__dict__  # Including full document fields and values in metadata
            )
            for doc in query_result.docs
        ]

        return documents


```

```swarmauri/community/document_stores/__init__.py



```

```swarmauri/community/document_stores/base/__init__.py



```

```swarmauri/community/document_stores/concrete/__init__.py



```

```swarmauri/community/document_stores/concrete/RedisDocumentStore.py

from typing import List, Optional
from ....standard.document_stores.base.DocumentStoreBase import DocumentStoreBase
from ....core.documents.IDocument import IDocument
import redis
import json
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


class RedisDocumentStore(DocumentStoreBase):
    def __init__(self, host, password, port, db):
        """Store connection details without initializing the Redis client."""
        self._host = host
        self._password = password
        self._port = port
        self._db = db
        self._redis_client = None  # Delayed initialization

    @property
    def redis_client(self):
        """Lazily initialize and return the Redis client using a factory method."""
        if self._redis_client is None:
            print('here')
            self._redis_client = redis.Redis(host=self._host, 
                                             password=self._password, 
                                             port=self._port, 
                                             db=self._db)
            print('there')
        return self._redis_client

    def add_document(self, document: IDocument) -> None:
        
        data = document.as_dict()
        doc_id = data['id'] 
        del data['id']
        self.redis_client.json().set(doc_id, '$', json.dumps(data))

    def add_documents(self, documents: List[IDocument]) -> None:
        with self.redis_client.pipeline() as pipe:
            for document in documents:
                pipe.set(document.doc_id, document)
            pipe.execute()

    def get_document(self, doc_id: str) -> Optional[IDocument]:
        result = self.redis_client.json().get(doc_id)
        if result:
            return json.loads(result)
        return None

    def get_all_documents(self) -> List[IDocument]:
        keys = self.redis_client.keys('*')
        documents = []
        for key in keys:
            document_data = self.redis_client.get(key)
            if document_data:
                documents.append(json.loads(document_data))
        return documents

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        self.add_document(updated_document)

    def delete_document(self, doc_id: str) -> None:
        self.redis_client.delete(doc_id)
    
    def __getstate__(self):
        """Return the object state for serialization, excluding the Redis client."""
        state = self.__dict__.copy()
        state['_redis_client'] = None  # Exclude Redis client from serialization
        return state

    def __setstate__(self, state):
        """Restore the object state after serialization, reinitializing the Redis client."""
        self.__dict__.update(state)

```

```swarmauri/community/vector_stores/ChromadbVectorStore.py

import os
from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
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

```

```swarmauri/community/vector_stores/__init__.py



```

```swarmauri/community/vector_stores/QdrantVectorStore.py

import os
import json
import pickle
import tempfile
from typing import List, Union
from qdrant_client import QdrantClient, models

from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.Doc2VecVectorizer import Doc2VecVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance


class QdrantVectorStore(VectorDocumentStoreRetrieveBase):
    """
    QdrantVectorStore is a concrete implementation that integrates functionality
    for saving, loading, storing, and retrieving vector documents, leveraging Qdrant as the backend.
    """

    def __init__(self, url: str, api_key: str, collection_name: str, vector_size: int):
        self.vectorizer = Doc2VecVectorizer(vector_size=vector_size)
        self.metric = CosineDistance()
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        exists = self.client.collection_exists(collection_name)
        
        if not exists:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )   


    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.
        
        Parameters:
            document (IDocument): The document to be added to the store.
        """
        try:
            embedding = document.embedding or self.vectorizer.fit_transform(document.content).data 
            self.client.upsert(self.collection_name, points=[
                models.PointStruct(
                    id=document.id,
                    vector=embedding,
                    payload=document.metadata
                )
            ])
            
        except:
            embedding = document.embedding or self.vectorizer.fit_transform(document.content).data 
            self.client.upsert(self.collection_name, points=[
                models.PointStruct(
                    id=document.id,
                    vector=embedding,
                    payload=document.metadata
                )
            ])
            
        

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.
        
        Parameters:
            documents (List[IDocument]): A list of documents to be added to the store.
        """
        self.vectorizer.fit_transform([doc.content for doc in documents])
        points = [
            models.PointStruct(
                id=doc.id,
                vector=doc.embedding or self.vectorizer.infer_vector(doc.content).data,
                payload=doc.metadata
            ) for doc in documents
        ]
        self.client.upsert(self.collection_name, points=points)

    def get_document(self, id: str) -> Union[IDocument, None]:
        """
        Retrieve a single document by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to retrieve.
        
        Returns:
            Union[IDocument, None]: The requested document if found; otherwise, None.
        """
        
        raise NotImplementedError('Get document not implemented, use retrieve().')

    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.
        
        Returns:
            List[IDocument]: A list of all documents in the store.
        """
        raise NotImplementedError('Get all documents not implemented, use retrieve().')

    def delete_document(self, id: str) -> None:
        """
        Delete a document from the document store by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to delete.
        """
        self.client.delete(self.collection_name, points_selector=[id])

    def update_document(self, id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.
        
        Parameters:
            id (str): The unique identifier of the document to update.
            updated_document (IDocument): The updated document instance.
        """
        self.client.upsert(self.collection_name, points=[                           
            models.PointStruct(
                id=updated_document.id,
                vector=updated_document.embedding,
                payload=updated_document.metadata
            )
        ])

    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store
        """
        self.documents = []
        self.client.delete(self.collection_name, points_selector=models.FilterSelector())

    def document_count(self) -> int:
        """
        Returns the number of documents in the store.
        """
        raise NotImplementedError('Get document not implemeneted, use retrieve().')

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        For the purpose of this example, this method performs a basic search.
        
        Args:
            query (str): The query string used for document retrieval. 
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        # This should be modified to a query to the Qdrant service for relevance search
        query_vector = self.vectorizer.infer_vector(query).data
        documents = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k)
        
        matching_documents = [
            doc.payload for doc in documents
        ]
        return matching_documents[:top_k]


```

```swarmauri/community/vector_stores/AnnoyVectorStore.py

import os
import json
import pickle
import tempfile
from typing import List, Union
from annoy import AnnoyIndex
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

from swarmauri.standard.vectorizers.concrete.Doc2VecVectorizer import Doc2VecVectorizer
#from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

class AnnoyVectorStore(SaveLoadStoreBase, VectorDocumentStoreRetrieveBase):
    """
    AnnoyVectorStore is a concrete implementation that integrates functionality
    for saving, loading, storing, and retrieving vector documents, leveraging Annoy as the backend.
    """

    def __init__(self, dimension: int, metric='euclidean', num_trees=10):
        self.dimension = dimension
        self.vectorizer = Doc2VecVectorizer()
        self.metric = metric
        self.num_trees = num_trees
        self.index = AnnoyIndex(dimension, metric)
        self.documents = []  # List of documents
        self.id_to_index = {}  # Mapping from document ID to index in Annoy
        SaveLoadStoreBase.__init__(self, self.vectorizer, [])

    def get_state(self) -> dict:
        """
        Retrieve the internal state of the vector store to be saved.
        
        Returns:
            dict: The internal state of the vector store.
        """
        return {
            'documents': [doc.to_dict() for doc in self.documents],
            'id_to_index': self.id_to_index
        }

    def set_state(self, state: dict) -> None:
        """
        Set the internal state of the vector store when loading.
        
        Parameters:
            state (dict): The state to set to the vector store.
        """
        self.documents = [Document.from_dict(doc_dict) for doc_dict in state.get('documents', [])]
        self.id_to_index = state['id_to_index']
        for idx, document in enumerate(self.documents):
            self.index.add_item(idx, document.content)
        self.index.build(self.num_trees)

    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.
        
        Parameters:
            document (IDocument): The document to be added to the store.
        """
        index = len(self.documents)
        self.documents.append(document)
        self.index.add_item(index, document.content)
        self.id_to_index[document.id] = index
        try:
            self.index.build(self.num_trees)
        except Exception as e:
            self._rebuild_index()

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.
        
        Parameters:
            documents (List[IDocument]): A list of documents to be added to the store.
        """
        start_idx = len(self.documents)
        self.documents.extend(documents)
        for i, doc in enumerate(documents):
            idx = start_idx + i
            self.index.add_item(idx, doc.content)
            self.id_to_index[doc.id] = idx
        try:
            self.index.build(self.num_trees)
        except Exception as e:
            self._rebuild_index()

    def get_document(self, id: str) -> Union[IDocument, None]:
        """
        Retrieve a single document by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to retrieve.
        
        Returns:
            Union[IDocument, None]: The requested document if found; otherwise, None.
        """
        index = self.id_to_index.get(id)
        if index is not None:
            return self.documents[index]
        return None

    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.
        
        Returns:
            List[IDocument]: A list of all documents in the store.
        """
        return self.documents

    def delete_document(self, id: str) -> None:
        """
        Delete a document from the document store by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to delete.
        """
        if id in self.id_to_index:
            index = self.id_to_index.pop(id)
            self.documents.pop(index)
            self._rebuild_index()

    def update_document(self, id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.
        
        Parameters:
            id (str): The unique identifier of the document to update.
            updated_document (IDocument): The updated document instance.
        """
        if id in self.id_to_index:
            index = self.id_to_index[id]
            self.documents[index] = updated_document
            self._rebuild_index()

    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store
        """
        self.documents = []
        self.doc_id_to_index = {}
        self.index = AnnoyIndex(self.dimension, self.metric)

    def document_count(self) -> int:
        """
        Returns the number of documents in the store.
        """
        return len(self.documents)

    def retrieve(self, query: List[float], top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (List[float]): The content of the document for retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        indices = self.index.get_nns_by_vector(query, top_k, include_distances=False)
        return [self.documents[idx] for idx in indices]

    def save_store(self, directory_path: str) -> None:
        """
        Saves the state of the vector store to the specified directory. This includes
        both the vectorizer's model and the stored documents or vectors.

        Parameters:
            directory_path (str): The directory path where the store's state will be saved.
        """
        state = self.get_state()
        os.makedirs(directory_path, exist_ok=True)
        state_file = os.path.join(directory_path, 'store_state.json')
        index_file = os.path.join(directory_path, 'annoy_index.ann')

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=4)
        self.index.save(index_file)

    def load_store(self, directory_path: str) -> None:
        """
        Loads the state of the vector store from the specified directory. This includes
        both the vectorizer's model and the stored documents or vectors.

        Parameters:
            directory_path (str): The directory path from where the store's state will be loaded.
        """
        state_file = os.path.join(directory_path, 'store_state.json')
        index_file = os.path.join(directory_path, 'annoy_index.ann')

        with open(state_file, 'r') as f:
            state = json.load(f)
        self.set_state(state)
        self.index.load(index_file)

    def save_parts(self, directory_path: str, chunk_size: int = 10485760) -> None:
        """
        Save the model in parts to handle large files by splitting them.
        """
        state = self.get_state()
        os.makedirs(directory_path, exist_ok=True)
        temp_state_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            pickle.dump(state, temp_state_file)
            temp_state_file.close()

            with open(temp_state_file.name, 'rb') as src:
                part_num = 0
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    with open(os.path.join(directory_path, f'state_part_{part_num}.pkl'), 'wb') as dest:
                        dest.write(chunk)
                    part_num += 1
        finally:
            os.remove(temp_state_file.name)

        index_file = os.path.join(directory_path, 'annoy_index.ann')
        self.index.save(index_file)

        with open(index_file, 'rb') as src:
            part_num = 0
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                with open(os.path.join(directory_path, f'index_part_{part_num}.ann'), 'wb') as dest:
                    dest.write(chunk)
                part_num += 1

    def load_parts(self, directory_path: str, state_file_pattern: str, index_file_pattern: str) -> None:
        """
        Load and combine model parts from a directory.
        """
        temp_state_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            with open(temp_state_file.name, 'ab') as dest:
                part_num = 0
                while True:
                    part_file_path = os.path.join(directory_path, state_file_pattern.format(part_num))
                    if not os.path.isfile(part_file_path):
                        break
                    with open(part_file_path, 'rb') as src:
                        chunk = src.read()
                        dest.write(chunk)
                    part_num += 1

            with open(temp_state_file.name, 'rb') as src:
                state = pickle.load(src)
            self.set_state(state)
        finally:
            os.remove(temp_state_file.name)

        index_file = os.path.join(directory_path, 'annoy_index.ann')
        self.index.load(index_file)

    def _rebuild_index(self):
        """
        Rebuild the Annoy index from the current documents.
        """
        self.index = AnnoyIndex(self.dimension, self.metric)
        for idx, document in enumerate(self.documents):
            self.index.add_item(idx, document.content)
        self.index.build(self.num_trees)

```