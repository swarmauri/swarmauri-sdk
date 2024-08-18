```swarmauri/README.md

# swarmaURI sdk

This repository includes core interfaces, standard ABCs, and standard concrete references of the SwarmaURI Framework.


## Core
- ABCs
- Utilities

## Standard
- Concrete Classes

## Community
- Concrete Classes that utilize third party plug-ins

## Experimental
- Tools in development



```

```swarmauri/__init__.py

__version__ = "0.4.1.dev1"
__long_desc__ = """
# swarmaURI sdk

This repository includes core interfaces, standard ABCs, and standard concrete references of the SwarmaURI Framework.


## Core 
- Core Interfaces

## Standard
- Base Classes
- Mixins
- Concrete Classes

## Community
- Concrete Classes that utilize third party plug-ins

## Experimental
- Components in development

# Features

- Polymorphism
- Discriminated Unions
- Serialization
- Intensional and Extensional Programming

"""

```

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

```swarmauri/core/README.md

# Core Library

The Core Library provides the foundational interfaces and abstract base classes necessary for developing scalable and flexible machine learning agents, models, and tools. It is designed to offer a standardized approach to implementing various components of machine learning systems, such as models, parsers, conversations, and vector stores.

## Features

- **Models Interface**: Define and interact with predictive models.
- **Agents Interface**: Build and manage intelligent agents for varied tasks.
- **Tools Interface**: Develop tools with standardized execution and configuration.
- **Parsers and Conversations**: Handle and parse text data, manage conversations states.
- **Vector Stores**: Interface for vector storage and similarity searches.
- **Document Stores**: Manage the storage and retrieval of documents.
- **Retrievers and Chunkers**: Efficiently retrieve relevant documents and chunk large text data.

## Getting Started

To start developing with the Core Library, include it as a module in your Python project. Ensure you have Python 3.6 or later installed.

```python
# Example of using an abstract model interface from the Core Library
from swarmauri.core.models.IModel import IModel

class MyModel(IModel):
    # Implement the abstract methods here
    pass
```

## Documentation

For more detailed documentation on each interface and available abstract classes, refer to the [Docs](/docs) directory within the library.

## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, please submit a pull request.

## License

See `LICENSE` for more information.


```

```swarmauri/core/__init__.py



```

```swarmauri/core/ComponentBase.py

from typing import (
    Optional, 
    List,
    Literal, 
    TypeVar, 
    Type, 
    Union, 
    Annotated, 
    Generic, 
    ClassVar, 
    Set,
    get_args)

from uuid import uuid4
from enum import Enum
import inspect
import hashlib
from pydantic import BaseModel, Field, field_validator
import logging
from swarmauri.core.typing import SubclassUnion

class ResourceTypes(Enum):
    UNIVERSAL_BASE = 'ComponentBase'
    AGENT = 'Agent'
    AGENT_FACTORY = 'AgentFactory'
    CHAIN = 'Chain'
    CHAIN_METHOD = 'ChainMethod'
    CHUNKER = 'Chunker'
    CONVERSATION = 'Conversation'
    DISTANCE = 'Distance'
    DOCUMENT_STORE = 'DocumentStore'
    DOCUMENT = 'Document'
    EMBEDDING = 'Embedding'
    EXCEPTION = 'Exception'
    LLM = 'LLM'
    MESSAGE = 'Message'
    METRIC = 'Metric'
    PARSER = 'Parser'
    PROMPT = 'Prompt'
    STATE = 'State'
    CHAINSTEP = 'ChainStep'
    SCHEMA_CONVERTER = 'SchemaConverter'
    SWARM = 'Swarm'
    TOOLKIT = 'Toolkit'
    TOOL = 'Tool'
    PARAMETER = 'Parameter'
    TRACE = 'Trace'
    UTIL = 'Util'
    VECTOR_STORE = 'VectorStore'
    VECTOR = 'Vector'

def generate_id() -> str:
    return str(uuid4())

class ComponentBase(BaseModel):
    name: Optional[str] = None
    id: str = Field(default_factory=generate_id)
    members: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    host: Optional[str] = None
    resource: str = Field(default="ComponentBase")
    version: str = "0.1.0"
    __swm_subclasses__: ClassVar[Set[Type['ComponentBase']]] = set()
    type: Literal['ComponentBase'] = 'ComponentBase'
    

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ComponentBase.__swm_register_subclass__(cls)
    
    # @classmethod
    # def __swm__get_subclasses__(cls) -> set:
    #     logging.debug('__swm__get_subclasses__ executed\n')
    #     def is_excluded_module(module_name: str) -> bool:
    #         return (module_name == 'builtins' or 
    #                 module_name == 'types')

    #     subclasses_dict = {cls.__name__: cls}
    #     for subclass in cls.__subclasses__():
    #         if not is_excluded_module(subclass.__module__):
    #             subclasses_dict.update({_s.__name__: _s for _s in subclass.__swm__get_subclasses__() 
    #                 if not is_excluded_module(_s.__module__)})

    #     return set(subclasses_dict.values())
    
    @classmethod
    def __swm_register_subclass__(cls, subclass):
        logging.debug('__swm_register_subclass__ executed\n')
        
        if 'type' in subclass.__annotations__:
            sub_type = subclass.__annotations__['type']
            if sub_type not in [subclass.__annotations__['type'] for subclass in cls.__swm_subclasses__]:
                cls.__swm_subclasses__.add(subclass)
        else:
            logging.warning(f'Subclass {subclass.__name__} does not have a type annotation')


        # [subclass.__swm_reset_class__()  for subclass in cls.__swm_subclasses__ 
        #  if hasattr(subclass, '__swm_reset_class__')]
    
    
    @classmethod
    def __swm_reset_class__(cls):
        logging.debug('__swm_reset_class__ executed\n')
        for each in cls.__fields__:
            logging.debug(each, cls.__fields__[each].discriminator)
            if (cls.__fields__[each].discriminator and each in cls.__annotations__
               ):
                if len(get_args(cls.__fields__[each].annotation)) > 0:
                    for x in range(0, len(get_args(cls.__fields__[each].annotation))):
                        if hasattr(get_args(cls.__fields__[each].annotation)[x], '__base__'):
                            if (hasattr(get_args(cls.__fields__[each].annotation)[x].__base__, '__swm_subclasses__') and
                            not get_args(cls.__fields__[each].annotation)[x].__base__.__name__ == 'ComponentBase'):

                                baseclass = get_args(cls.__fields__[each].annotation)[x].__base__
         
                                sc = SubclassUnion[baseclass]
                                
                                cls.__annotations__[each] = sc
                                cls.__fields__[each].annotation = sc

        
        # This is not necessary as the model_rebuild address forward_refs 
        # https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_post_init
        # cls.update_forward_refs() 
        cls.model_rebuild(force=True)


    @field_validator('type')
    def set_type(cls, v, values):
        if v == 'ComponentBase' and cls.__name__ != 'ComponentBase':
            return cls.__name__
        return v

    def __swm_class_hash__(self):
        sig_hash = hashlib.sha256()
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if callable(attr_value) and not attr_name.startswith("_"):
                sig = inspect.signature(attr_value)
                sig_hash.update(str(sig).encode())
        return sig_hash.hexdigest()

    @classmethod
    def swm_public_interfaces(cls):
        methods = []
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if (callable(attr_value) and not attr_name.startswith("_")) or isinstance(attr_value, property):
                methods.append(attr_name)
        return methods

    @classmethod
    def swm_ismethod_registered(cls, method_name: str):
        return method_name in cls.public_interfaces()

    @classmethod
    def swm_method_signature(cls, input_signature):
        for method_name in cls.public_interfaces():
            method = getattr(cls, method_name)
            if callable(method):
                sig = str(inspect.signature(method))
                if sig == input_signature:
                    return True
        return False

    @property
    def swm_path(self):
        if self.host and self.owner:
            return f"{self.host}/{self.owner}/{self.resource}/{self.name}/{self.id}"
        if self.resource and self.name:
            return f"/{self.resource}/{self.name}/{self.id}"
        return f"/{self.resource}/{self.id}"

    @property
    def swm_is_remote(self):
        return bool(self.host)

```

```swarmauri/core/typing.py

import logging
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Union, Annotated, Type


class SubclassUnion:

    @classmethod
    def __class_getitem__(cls, baseclass):
        subclasses = cls.__swm__get_subclasses__(baseclass)
        return Union[tuple(subclasses)]

    @classmethod
    def __swm__get_subclasses__(cls, baseclass) -> set:
        logging.debug('__swm__get_subclasses__ executed\n')
        def is_excluded_module(module_name: str) -> bool:
            return (module_name == 'builtins' or 
                    module_name == 'types')

        subclasses_dict = {baseclass.__name__: baseclass}
        for subclass in baseclass.__subclasses__():
            if not is_excluded_module(subclass.__module__):
                subclasses_dict.update({_s.__name__: _s for _s in cls.__swm__get_subclasses__(subclass) 
                    if not is_excluded_module(_s.__module__)})

        return set(subclasses_dict.values())

```

```swarmauri/core/llms/__init__.py



```

```swarmauri/core/llms/IFit.py

from abc import ABC, abstractmethod

class IFit(ABC):
    """
    Interface for training models.
    """

    @abstractmethod
    def fit(self, X_train, y_train, epochs: int, batch_size: int) -> None:
        """
        Train the model on the provided dataset.
        """
        pass

```

```swarmauri/core/llms/IPredict.py

from abc import ABC, abstractmethod

class IPredict(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining models.
    """

    @abstractmethod
    def predict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

```

```swarmauri/core/agent_apis/__init__.py

from .IAgentCommands import IAgentCommands
from .IAgentRouterCRUD import IAgentRouterCRUD

__all__ = ['IAgentCommands', 'IAgentRouterCRUD']

```

```swarmauri/core/agent_apis/IAgentCommands.py

from abc import ABC, abstractmethod
from typing import Callable, Any, List

class IAgentCommands(ABC):
    """
    Interface for the API object that enables a SwarmAgent to host various API routes.
    """


    @abstractmethod
    def invoke(self, request: Any) -> Any:
        """
        Handles invocation requests synchronously.
        
        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: The response payload.
        """
        pass

    @abstractmethod
    async def ainvoke(self, request: Any) -> Any:
        """
        Handles invocation requests asynchronously.
        
        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: The response payload.
        """
        pass

    @abstractmethod
    def batch(self, requests: List[Any]) -> List[Any]:
        """
        Handles batched invocation requests synchronously.
        
        Parameters:
            requests (List[Any]): A list of incoming request payloads.

        Returns:
            List[Any]: A list of responses.
        """
        pass

    @abstractmethod
    async def abatch(self, requests: List[Any]) -> List[Any]:
        """
        Handles batched invocation requests asynchronously.

        Parameters:
            requests (List[Any]): A list of incoming request payloads.

        Returns:
            List[Any]: A list of responses.
        """
        pass

    @abstractmethod
    def stream(self, request: Any) -> Any:
        """
        Handles streaming requests.

        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: A streaming response.
        """
        pass

    @abstractmethod
    def get_schema_config(self) -> dict:
        """
        Retrieves the schema configuration for the API.

        Returns:
            dict: The schema configuration.
        """
        pass

```

```swarmauri/core/agent_apis/IAgentRouterCRUD.py

from abc import ABC, abstractmethod
from typing import Callable, Any, Dict

class IAgentRouterCRUD(ABC):
    """
    Interface for managing API routes within a SwarmAgent.
    """
    
    @abstractmethod
    def create_route(self, path: str, method: str, handler: Callable[[Any], Any]) -> None:
        """
        Create a new route for the API.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method (e.g., 'GET', 'POST').
        - handler (Callable[[Any], Any]): The function that handles requests to this route.
        """
        pass
    
    @abstractmethod
    def read_route(self, path: str, method: str) -> Dict:
        """
        Retrieve information about a specific route.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        
        Returns:
        - Dict: Information about the route, including path, method, and handler.
        """
        pass
    
    @abstractmethod
    def update_route(self, path: str, method: str, new_handler: Callable[[Any], Any]) -> None:
        """
        Update the handler function for an existing route.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        - new_handler (Callable[[Any], Any]): The new function that handles requests to this route.
        """
        pass
    
    @abstractmethod
    def delete_route(self, path: str, method: str) -> None:
        """
        Delete a specific route from the API.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        """
        pass

```

```swarmauri/core/conversations/__init__.py



```

```swarmauri/core/conversations/IMaxSize.py

from abc import ABC, abstractmethod

class IMaxSize(ABC):
    pass

```

```swarmauri/core/conversations/IConversation.py

from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri.core.messages.IMessage import IMessage

class IConversation(ABC):
    """
    Interface for managing conversations, defining abstract methods for
    adding messages, retrieving the latest message, getting all messages, and clearing history.
    """

    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        pass

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history.
        """
        pass

    @abstractmethod
    def get_last(self) -> Optional[IMessage]:
        """
        Retrieves the latest message from the conversation history.
        """
        pass

    @abstractmethod
    def clear_history(self) -> None:
        """
        Clears the conversation history.
        """
        pass



```

```swarmauri/core/conversations/ISystemContext.py

from abc import ABC, abstractmethod

class ISystemContext(ABC):
    pass


```

```swarmauri/core/documents/__init__.py



```

```swarmauri/core/documents/IDocument.py

from abc import ABC

class IDocument(ABC):
   pass

```

```swarmauri/core/documents/IExperimentDocument.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from swarmauri.core.documents.IDocument import IDocument

class IExperimentDocument(IDocument, ABC):
    """
    Interface for an Experiment Document, extending the general IDocument interface
    with additional properties and methods specific to experimental data.
    """
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        Get the parameters used in the experiment.
        """
        pass

    @parameters.setter
    @abstractmethod
    def parameters(self, value: Dict[str, Any]) -> None:
        """
        Set the parameters used in the experiment.
        """
        pass

    @property
    @abstractmethod
    def results(self) -> Dict[str, Any]:
        """
        Get the results obtained from the experiment.
        """
        pass

    @results.setter
    @abstractmethod
    def results(self, value: Dict[str, Any]) -> None:
        """
        Set the results obtained from the experiment.
        """
        pass

    @property
    @abstractmethod
    def instruction(self) -> str:
        """
        An instructional or descriptive text about what the experiment aims to achieve or how.
        """
        pass

    @instruction.setter
    @abstractmethod
    def instruction(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def feature_set(self) -> List[Any]:
        """
        Description of the set of features or data used in the experiment.
        """
        pass

    @feature_set.setter
    @abstractmethod
    def feature_set(self, value: List[Any]) -> None:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """
        The version of the experiment, useful for tracking iterations and changes over time.
        """
        pass

    @version.setter
    @abstractmethod
    def version(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def artifacts(self) -> List[str]:
        """
        A list of paths or identifiers for any artifacts generated by the experiment,
        such as models, charts, or data dumps.
        """
        pass

    @artifacts.setter
    @abstractmethod
    def artifacts(self, value: List[str]) -> None:
        pass

    @property
    @abstractmethod
    def datetime_created(self) -> datetime:
        """
        Timestamp marking when the experiment was initiated or created.
        """
        pass

    @datetime_created.setter
    @abstractmethod
    def datetime_created(self, value: datetime) -> None:
        pass

    @property
    @abstractmethod
    def datetime_completed(self) -> Optional[datetime]:
        """
        Timestamp of when the experiment was completed. None if the experiment is still running.
        """
        pass

    @datetime_completed.setter
    @abstractmethod
    def datetime_completed(self, value: Optional[datetime]) -> None:
        pass


```

```swarmauri/core/messages/IMessage.py

from abc import ABC, abstractmethod

class IMessage(ABC):
    """
    An abstract interface representing a general message structure.

    This interface defines the basic attributes that all
    messages should have, including type, name, and content, 
    and requires subclasses to implement representation and formatting methods.
    """


```

```swarmauri/core/messages/__init__.py

from .IMessage import IMessage

```

```swarmauri/core/parsers/__init__.py



```

```swarmauri/core/parsers/IParser.py

from abc import ABC, abstractmethod
from typing import List, Union, Any
from swarmauri.core.documents.IDocument import IDocument

class IParser(ABC):
    """
    Abstract base class for parsers. It defines a public method to parse input data (str or Message) into documents,
    and relies on subclasses to implement the specific parsing logic through protected and private methods.
    """

    @abstractmethod
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.
        
        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass


```

```swarmauri/core/prompts/__init__.py



```

```swarmauri/core/prompts/IPrompt.py

from abc import ABC, abstractmethod
from typing import Optional, Any

class IPrompt(ABC):
    """
    A base abstract class representing a prompt system.

    Methods:
        __call__: Abstract method that subclasses must implement to enable the instance to be called directly.
    """

    @abstractmethod
    def __call__(self, **kwargs) -> str:
        """
        Abstract method that subclasses must implement to define the behavior of the prompt when called.

        """
        pass


```

```swarmauri/core/prompts/ITemplate.py

from typing import Dict, List, Any, Union
from abc import ABC, abstractmethod


class ITemplate(ABC):
    """
    Interface for template-based prompt generation within the SwarmAURI framework.
    Defines standard operations and attributes for managing and utilizing templates.
    """
    
    @abstractmethod
    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.

        Args:
            template (str): The new template string to be used for generating prompts.
        """
        pass

    @abstractmethod
    def set_variables(self, 
                      variables: Union[List[Dict[str, Any]], Dict[str, Any]] = {}) -> None:
        """
        Sets or updates the variables to be substituted into the template.

        Args:
            variables (List[Dict[str, str]]): A dictionary of variables where each key-value 
                                        pair corresponds to a placeholder name and its 
                                        replacement value in the template.
        """
        pass

    @abstractmethod
    def generate_prompt(self, **kwargs) -> str:
        """
        Generates a prompt string based on the current template and provided keyword arguments.

        Args:
            **kwargs: Keyword arguments containing variables for template substitution. 

        Returns:
            str: The generated prompt string with template variables replaced by their
                 corresponding values provided in `kwargs`.
        """
        pass

```

```swarmauri/core/prompts/IPromptMatrix.py

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any

class IPromptMatrix(ABC):

    @property
    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt matrix."""
        pass

    @abstractmethod
    def add_prompt_sequence(self, sequence: List[Optional[str]]) -> None:
        """Add a new prompt sequence to the matrix."""
        pass

    @abstractmethod
    def remove_prompt_sequence(self, index: int) -> None:
        """Remove a prompt sequence from the matrix by index."""
        pass

    @abstractmethod
    def get_prompt_sequence(self, index: int) -> List[Optional[str]]:
        """Get a prompt sequence from the matrix by index."""
        pass

    @abstractmethod
    def show(self) -> List[List[Optional[str]]]:
        """Show the entire prompt matrix."""
        pass

```

```swarmauri/core/agents/__init__.py



```

```swarmauri/core/agents/IAgentToolkit.py

from abc import ABC

class IAgentToolkit(ABC):
    pass

```

```swarmauri/core/agents/IAgentConversation.py

from abc import ABC, abstractmethod
from swarmauri.core.conversations.IConversation import IConversation

class IAgentConversation(ABC):
    pass

```

```swarmauri/core/agents/IAgentParser.py

from abc import ABC, abstractmethod
from swarmauri.core.parsers.IParser import IParser 

class IAgentParser(ABC):
    
    @property
    @abstractmethod
    def parser(self) -> IParser:
        pass

    @parser.setter
    @abstractmethod
    def parser(self) -> IParser:
        pass

```

```swarmauri/core/agents/IAgent.py

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

class IAgent(ABC):

    @abstractmethod
    def exec(self, input_data: Optional[Any], llm_kwargs: Optional[Dict]) -> Any:
        """
        Executive method that triggers the agent's action based on the input data.
        """
        pass
    

```

```swarmauri/core/agents/IAgentVectorStore.py

from abc import ABC

class IAgentVectorStore(ABC):
    pass

```

```swarmauri/core/agents/IAgentRetrieve.py

from abc import ABC

class IAgentRetrieve(ABC):
    pass

```

```swarmauri/core/agents/IAgentSystemContext.py

from abc import ABC, abstractmethod

class IAgentSystemContext(ABC):
    pass

```

```swarmauri/core/swarms/__init__.py



```

```swarmauri/core/swarms/ISwarm.py

from abc import ABC, abstractmethod
from typing import Any, List, Dict
from datetime import datetime
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.chains.ICallableChain import ICallableChain

class ISwarm(ABC):
    """
    Interface for a Swarm, representing a collective of agents capable of performing tasks, executing callable chains, and adaptable configurations.
    """

    # Abstract properties and setters
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the factory instance."""
        pass

    @id.setter
    @abstractmethod
    def id(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @name.setter
    @abstractmethod
    def name(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @type.setter
    @abstractmethod
    def type(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def date_created(self) -> datetime:
        pass

    @property
    @abstractmethod
    def last_modified(self) -> datetime:
        pass

    @last_modified.setter
    @abstractmethod
    def last_modified(self, value: datetime) -> None:
        pass

    def __hash__(self):
        """
        The __hash__ method allows objects of this class to be used in sets and as dictionary keys.
        __hash__ should return an integer and be defined based on immutable properties.
        This is generally implemented directly in concrete classes rather than in the interface,
        but it's declared here to indicate that implementing classes must provide it.
        """
        pass



```

```swarmauri/core/swarms/ISwarmComponent.py

from abc import ABC, abstractmethod

class ISwarmComponent(ABC):
    """
    Interface for defining a general component within a swarm system.
    """

    @abstractmethod
    def __init__(self, key: str, name: str):
        """
        Initializes a swarm component with a unique key and name.
        """
        pass

```

```swarmauri/core/swarms/ISwarmConfigurationExporter.py

from abc import ABC, abstractmethod
from typing import Dict
class ISwarmConfigurationExporter(ABC):

    @abstractmethod
    def to_dict(self) -> Dict:
        """
        Serializes the swarm configuration to a dictionary.

        Returns:
            Dict: The serialized configuration as a dictionary.
        """
        pass

    @abstractmethod
    def to_json(self) -> str:
        """
        Serializes the swarm configuration to a JSON string.

        Returns:
            str: The serialized configuration as a JSON string.
        """
        pass

    @abstractmethod
    def to_pickle(self) -> bytes:
        """
        Serializes the swarm configuration to a Pickle byte stream.

        Returns:
            bytes: The serialized configuration as a Pickle byte stream.
        """
        pass

```

```swarmauri/core/swarms/ISwarmFactory.py

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Type, Union
from swarmauri.core.swarms.ISwarm import ISwarm
from swarmauri.core.chains.ICallableChain import ICallableChain 
from swarmauri.core.agents.IAgent import IAgent 

class Step(NamedTuple):
    description: str
    callable: Callable  # Reference to the function to execute
    args: Optional[List[Any]] = None
    kwargs: Optional[Dict[str, Any]] = None

class CallableChainItem(NamedTuple):
    key: str  # Unique identifier for the item within the chain
    execution_context: Dict[str, Any]  # Execution context and metadata
    steps: List[Step]

class AgentDefinition(NamedTuple):
    type: str
    configuration: Dict[str, Any]
    capabilities: List[str]
    dependencies: List[str]
    execution_context: Dict[str, Any]

class FunctionParameter(NamedTuple):
    name: str
    type: Type
    default: Optional[Any] = None
    required: bool = True

class FunctionDefinition(NamedTuple):
    identifier: str
    parameters: List[FunctionParameter]
    return_type: Type
    execution_context: Dict[str, Any]
    callable_source: Callable
    
class ISwarmFactory(ABC):

    @abstractmethod
    def create_swarm(self, *args, **kwargs) -> ISwarm:
        """
        Creates and returns a new swarm instance configured with the provided arguments.
        """
        pass

    @abstractmethod
    def create_agent(self, agent_definition: AgentDefinition) -> IAgent:
        """
        Creates a new agent based on the provided enhanced agent definition.
        
        Args:
            agent_definition: An instance of AgentDefinition detailing the agent's setup.
        
        Returns:
            An instance or identifier of the newly created agent.
        """
        pass
    
    @abstractmethod
    def create_callable_chain(self, chain_definition: List[CallableChainItem]) -> ICallableChain:
        """
        Creates a new callable chain based on the provided definition.

        Args:
            chain_definition: Details required to build the chain, such as sequence of functions and arguments.

        Returns:
            ICallableChain: The constructed callable chain instance.
        """
        pass
    
    @abstractmethod
    def register_function(self, function_definition: FunctionDefinition) -> None:
        """
        Registers a function within the factory ecosystem, making it available for callable chains and agents.

        Args:
            function_definition: An instance of FunctionDefinition detailing the function's specification.
        """
        pass

    @abstractmethod
    def export_callable_chains(self, format_type: str = 'json') -> Union[dict, str, bytes]:
        """
        Exports configurations of all callable chains in the specified format.
        Supported formats: 'json', 'pickle'.

        Args:
            format_type (str): The format for exporting the configurations.

        Returns:
            Union[dict, str, bytes]: The callable chain configurations in the specified format.
        """
        pass

    @abstractmethod
    def load_callable_chains(self, chains_data, format_type: str = 'json'):
        """
        Loads callable chain configurations from given data.

        Args:
            chains_data (Union[dict, str, bytes]): Data containing callable chain configurations.
            format_type (str): The format of the provided chains data.
        """
        pass

    @abstractmethod
    def export_configuration(self, format_type: str = 'json') -> Union[dict, str, bytes]:
        """
        Exports the swarm's and agents' configurations in the specified format.
        Supported formats: 'json', 'pickle'. Default is 'json'.

        Args:
            format_type (str): The format for exporting the configurations.

        Returns:
            Union[dict, str, bytes]: The configurations in the specified format.
        """
        pass


```

```swarmauri/core/swarms/ISwarmAgentRegistration.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from swarmauri.core.agents.IAgent import IAgent

class ISwarmAgentRegistration(ABC):
    """
    Interface for registering agents with the swarm, designed to support CRUD operations on IAgent instances.
    """

    @id.setter
    @abstractmethod
    def registry(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def registry(self) -> List[IAgent]:
        pass

    @abstractmethod
    def register_agent(self, agent: IAgent) -> bool:
        """
        Register a new agent with the swarm.

        Parameters:
            agent (IAgent): An instance of IAgent representing the agent to register.

        Returns:
            bool: True if the registration succeeded; False otherwise.
        """
        pass

    @abstractmethod
    def update_agent(self, agent_id: str, updated_agent: IAgent) -> bool:
        """
        Update the details of an existing agent. This could include changing the agent's configuration,
        task assignment, or any other mutable attribute.

        Parameters:
            agent_id (str): The unique identifier for the agent.
            updated_agent (IAgent): An updated IAgent instance to replace the existing one.

        Returns:
            bool: True if the update was successful; False otherwise.
        """
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the swarm based on its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent to be removed.

        Returns:
            bool: True if the removal was successful; False otherwise.
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[IAgent]:
        """
        Retrieve an agent's instance from its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent of interest.

        Returns:
            Optional[IAgent]: The IAgent instance if found; None otherwise.
        """
        pass



```

```swarmauri/core/swarms/ISwarmChainCRUD.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISwarmChainCRUD(ABC):
    """
    Interface to provide CRUD operations for ICallableChain within swarms.
    """

    @abstractmethod
    def create_chain(self, chain_id: str, chain_definition: Dict[str, Any]) -> None:
        """
        Creates a callable chain with the provided definition.

        Parameters:
        - chain_id (str): A unique identifier for the callable chain.
        - chain_definition (Dict[str, Any]): The definition of the callable chain including steps and their configurations.
        """
        pass

    @abstractmethod
    def read_chain(self, chain_id: str) -> Dict[str, Any]:
        """
        Retrieves the definition of a callable chain by its identifier.

        Parameters:
        - chain_id (str): The unique identifier of the callable chain to be retrieved.

        Returns:
        - Dict[str, Any]: The definition of the callable chain.
        """
        pass

    @abstractmethod
    def update_chain(self, chain_id: str, new_definition: Dict[str, Any]) -> None:
        """
        Updates an existing callable chain with a new definition.

        Parameters:
        - chain_id (str): The unique identifier of the callable chain to be updated.
        - new_definition (Dict[str, Any]): The new definition of the callable chain including updated steps and configurations.
        """
        pass

    @abstractmethod
    def delete_chain(self, chain_id: str) -> None:
        """
        Removes a callable chain from the swarm.

        Parameters:
        - chain_id (str): The unique identifier of the callable chain to be removed.
        """
        pass

    @abstractmethod
    def list_chains(self) -> List[Dict[str, Any]]:
        """
        Lists all callable chains currently managed by the swarm.

        Returns:
        - List[Dict[str, Any]]: A list of callable chain definitions.
        """
        pass

```

```swarmauri/core/toolkits/__init__.py



```

```swarmauri/core/toolkits/IToolkit.py

from typing import Dict
from abc import ABC, abstractmethod
from swarmauri.core.tools.ITool import ITool

class IToolkit(ABC):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    @abstractmethod
    def add_tools(self, tools: Dict[str, ITool]):
        """
        An abstract method that should be implemented by subclasses to add multiple tools to the toolkit.
        """
        pass

    @abstractmethod
    def add_tool(self, tool: ITool):
        """
        An abstract method that should be implemented by subclasses to add a single tool to the toolkit.
        """
        pass

    @abstractmethod
    def remove_tool(self, tool_name: str):
        """
        An abstract method that should be implemented by subclasses to remove a tool from the toolkit by name.
        """
        pass

    @abstractmethod
    def get_tool_by_name(self, tool_name: str) -> ITool:
        """
        An abstract method that should be implemented by subclasses to retrieve a tool from the toolkit by name.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        An abstract method that should be implemented by subclasses to return the number of tools in the toolkit.
        """
        pass

```

```swarmauri/core/tools/__init__.py



```

```swarmauri/core/tools/ITool.py

from abc import ABC, abstractmethod

class ITool(ABC):
        
    @abstractmethod
    def call(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass



```

```swarmauri/core/tools/IParameter.py

from abc import ABC, abstractmethod
from typing import List, Union

class IParameter(ABC):
    """
    An abstract class to represent a parameter for a tool.
    """

    pass

```

```swarmauri/core/utils/__init__.py



```

```swarmauri/core/utils/ITransactional.py

from abc import ABC, abstractmethod

class ITransactional(ABC):

    @abstractmethod
    def begin_transaction(self):
        """
        Initiates a transaction for a series of vector store operations.
        """
        pass
    
    @abstractmethod
    def commit_transaction(self):
        """
        Commits the current transaction, making all operations within the transaction permanent.
        """
        pass
    
    @abstractmethod
    def abort_transaction(self):
        """
        Aborts the current transaction, reverting all operations performed within the transaction.
        """
        pass

```

```swarmauri/core/vector_stores/ISimiliarityQuery.py

from abc import ABC, abstractmethod
from typing import List, Dict

class ISimilarityQuery(ABC):
    
    @abstractmethod
    def search_by_similarity_threshold(self, query_vector: List[float], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Args:
            query_vector (List[float]): The high-dimensional query vector.
            similarity_threshold (float): The similarity threshold for filtering results.
            space_name (str, optional): The name of the vector space to search within.

        Returns:
            List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        pass

```

```swarmauri/core/vector_stores/IGradient.py

from abc import ABC, abstractmethod
from typing import List, Callable

class IGradient(ABC):
    """
    Interface for calculating the gradient of a scalar field.
    """

    @abstractmethod
    def calculate_gradient(self, scalar_field: Callable[[List[float]], float], point: List[float]) -> List[float]:
        """
        Calculate the gradient of a scalar field at a specific point.

        Parameters:
        - scalar_field (Callable[[List[float]], float]): The scalar field represented as a function
                                                         that takes a point and returns a scalar value.
        - point (List[float]): The point at which the gradient is to be calculated.

        Returns:
        - List[float]: The gradient vector at the specified point.
        """
        pass

```

```swarmauri/core/vector_stores/IAngleBetweenVectors.py

from abc import ABC, abstractmethod
from typing import List

class IAngleBetweenVectors(ABC):
    """
    Interface for calculating the angle between two vectors.
    """

    @abstractmethod
    def angle_between(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Method to calculate and return the angle in radians between two vectors.

        Parameters:
        - vector_a (List[float]): The first vector as a list of floats.
        - vector_b (List[float]): The second vector as a list of floats.

        Returns:
        - float: The angle between vector_a and vector_b in radians.

        Note: Implementations should handle the vectors' dimensionality and throw appropriate exceptions for incompatible vectors.
        """
        pass

```

```swarmauri/core/vector_stores/IDecompose.py

from abc import ABC, abstractmethod
from typing import Tuple, List
from swarmauri.core.vectors.IVector import IVector  # Assuming there's a base IVector interface for vector representations

class IDecompose(ABC):
    """
    Interface for decomposing a vector into components along specified basis vectors.
    This operation is essential in expressing a vector in different coordinate systems or reference frames.
    """

    @abstractmethod
    def decompose(self, vector: IVector, basis_vectors: List[IVector]) -> List[IVector]:
        """
        Decompose the given vector into components along the specified basis vectors.

        Parameters:
        - vector (IVector): The vector to be decomposed.
        - basis_vectors (List[IVector]): A list of basis vectors along which to decompose the given vector.

        Returns:
        - List[IVector]: A list of vectors, each representing the component of the decomposed vector along 
                         the corresponding basis vector in the `basis_vectors` list.
        """
        pass

```

```swarmauri/core/vector_stores/IDivergence.py

from abc import ABC, abstractmethod
from typing import List

class IDivergence(ABC):
    """
    Interface for calculating the divergence of a vector field.
    """

    @abstractmethod
    def calculate_divergence(self, vector_field: List[List[float]], point: List[float]) -> float:
        """
        Calculate the divergence of a vector field at a specific point.

        Parameters:
        - vector_field (List[List[float]]): A representation of the vector field as a list of vectors.
        - point (List[float]): The point at which the divergence is to be calculated.

        Returns:
        - float: The divergence value at the specified point.
        """
        pass

```

```swarmauri/core/vector_stores/IOrthogonalProject.py

from abc import ABC, abstractmethod
from typing import List

class IOrthogonalProject(ABC):
    """
    Interface for calculating the orthogonal projection of one vector onto another.
    """

    @abstractmethod
    def orthogonal_project(self, vector_a: List[float], vector_b: List[float]) -> List[float]:
        """
        Calculates the orthogonal projection of vector_a onto vector_b.
        
        Args:
            vector_a (List[float]): The vector to be projected.
            vector_b (List[float]): The vector onto which vector_a is orthogonally projected.
        
        Returns:
            List[float]: The orthogonal projection of vector_a onto vector_b.
        """
        pass

```

```swarmauri/core/vector_stores/IProject.py

from abc import ABC, abstractmethod
from typing import List

class IProject(ABC):
    """
    Interface for projecting one vector onto another.
    """

    @abstractmethod
    def project(self, vector_a: List[float], vector_b: List[float]) -> List[float]:
        """
        Projects vector_a onto vector_b.
        
        Args:
            vector_a (List[float]): The vector to be projected.
            vector_b (List[float]): The vector onto which vector_a is projected.
        
        Returns:
            List[float]: The projection of vector_a onto vector_b.
        """
        pass



```

```swarmauri/core/vector_stores/IReflect.py

from abc import ABC, abstractmethod
from typing import List

class IReflect(ABC):
    """
    Interface for reflecting a vector across a specified plane or axis.
    """

    @abstractmethod
    def reflect_vector(self, vector: List[float], normal: List[float]) -> List[float]:
        """
        Reflects a vector across a plane or axis defined by a normal vector.

        Parameters:
        - vector (List[float]): The vector to be reflected.
        - normal (List[float]): The normal vector of the plane across which the vector will be reflected.

        Returns:
        - List[float]: The reflected vector.
        """
        pass

```

```swarmauri/core/vector_stores/ISimilarity.py

from abc import ABC, abstractmethod
from typing import List, Tuple
from swarmauri.core.vectors.IVector import IVector

class ISimilarity(ABC):
    """
    Interface to define operations for computing similarity and distance between vectors.
    This interface is crucial for systems that need to perform similarity searches, clustering,
    or any operations where vector similarity plays a key role.
    """

    @abstractmethod
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors. The definition of similarity (e.g., cosine similarity)
        should be implemented in concrete classes.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        pass



```

```swarmauri/core/vector_stores/IVectorSpan.py

from abc import ABC, abstractmethod
from typing import List, Any

class IVectorSpan(ABC):
    """
    Interface for determining if a vector is within the span of a set of vectors.
    """

    @abstractmethod
    def in_span(self, vector: Any, basis_vectors: List[Any]) -> bool:
        """
        Checks if the given vector is in the span of the provided basis vectors.

        Parameters:
        - vector (Any): The vector to check.
        - basis_vectors (List[Any]): A list of vectors that might span the vector.

        Returns:
        - bool: True if the vector is in the span of the basis_vectors, False otherwise.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorArithmetic.py

from abc import ABC, abstractmethod
from typing import List

class IVectorArithmetic(ABC):
    @abstractmethod
    def add(self, vector1: List[float], vector2: List[float]) -> List[float]:
        """
        Vector addition of 'vector1' and 'vector2'.
        """
        pass
        
    @abstractmethod
    def subtract(self, vector1: List[float], vector2: List[float]) -> List[float]:
        """
        Vector subtraction of 'vector1' - 'vector2'.
        """
        pass
   
    @abstractmethod
    def multiply(self, vector: List[float], scalar: float) -> List[float]:
        """
        Scalar multiplication of 'vector' by 'scalar'.
        """
        pass
        
    @abstractmethod
    def divide(self, vector: List[float], scalar: float) -> List[float]:
        """
        Scalar division of 'vector' by 'scalar'.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorLinearCombination.py

from abc import ABC, abstractmethod
from typing import List, Any

class ILinearCombination(ABC):
    """
    Interface for creating a vector as a linear combination of a set of vectors.
    """

    @abstractmethod
    def linear_combination(self, coefficients: List[float], vectors: List[Any]) -> Any:
        """
        Computes the linear combination of the given vectors with the specified coefficients.

        Parameters:
        - coefficients (List[float]): A list of coefficients for the linear combination.
        - vectors (List[Any]): A list of vectors to be combined.

        Returns:
        - Any: The resulting vector from the linear combination.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorNorm.py

# core/vectors/IVectorNorm.py

from abc import ABC, abstractmethod
from typing import List, Union

class IVectorNorm(ABC):
    """
    Interface for calculating vector norms.
    Supports L1 norm, L2 norm, and Max norm calculations.
    """

    @abstractmethod
    def l1_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the L1 norm (Manhattan norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the L1 norm.

        Returns:
        - float: The L1 norm of the vector.
        """
        pass

    @abstractmethod
    def l2_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the L2 norm (Euclidean norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the L2 norm.

        Returns:
        - float: The L2 norm of the vector.
        """
        pass

    @abstractmethod
    def max_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the Max norm (infinity norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the Max norm.

        Returns:
        - float: The Max norm of the vector.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorRotate.py

from abc import ABC, abstractmethod
from typing import List

class IRotate(ABC):
    """
    Interface for rotating a vector.
    """
    
    @abstractmethod
    def rotate(self, vector: List[float], angle: float, axis: List[float] = None) -> List[float]:
        """
        Rotate the given vector by a specified angle around an axis (for 3D) or in a plane (for 2D).

        For 2D vectors, the axis parameter can be omitted.

        Args:
            vector (List[float]): The vector to rotate.
            angle (float): The angle of rotation in degrees.
            axis (List[float], optional): The axis of rotation (applicable in 3D).

        Returns:
            List[float]: The rotated vector.
        """
        pass


```

```swarmauri/core/vector_stores/IVectorBasisCheck.py

from abc import ABC, abstractmethod
from typing import List, Any

class IVectorBasisCheck(ABC):
    """
    Interface for checking if a given set of vectors forms a basis of the vector space.
    """

    @abstractmethod
    def is_basis(self, vectors: List[Any]) -> bool:
        """
        Determines whether the given set of vectors forms a basis for their vector space.

        Parameters:
        - vectors (List[Any]): A list of vectors to be checked.

        Returns:
        - bool: True if the vectors form a basis, False otherwise.
        """
        pass

```

```swarmauri/core/vector_stores/__init__.py



```

```swarmauri/core/vector_stores/IVectorStoreSaveLoad.py

from abc import ABC, abstractmethod

class IVectorStoreSaveLoad(ABC):
    """
    Interface to abstract the ability to save and load the state of a vector store.
    This includes saving/loading the vectorizer's model as well as the documents or vectors.
    """

    @abstractmethod
    def save_store(self, directory_path: str) -> None:
        """
        Saves the state of the vector store to the specified directory. This includes
        both the vectorizer's model and the stored documents or vectors.

        Parameters:
        - directory_path (str): The directory path where the store's state will be saved.
        """
        pass

    @abstractmethod
    def load_store(self, directory_path: str) -> None:
        """
        Loads the state of the vector store from the specified directory. This includes
        both the vectorizer's model and the stored documents or vectors.

        Parameters:
        - directory_path (str): The directory path from where the store's state will be loaded.
        """
        pass

    @abstractmethod
    def save_parts(self, directory_path: str, chunk_size: int=10485760) -> None:
        """
        Save the model in parts to handle large files by splitting them.

        """
        pass

    @abstractmethod
    def load_parts(self, directory_path: str, file_pattern: str) -> None:
        """
        Load and combine model parts from a directory.

        """
        pass


```

```swarmauri/core/vector_stores/IVectorStore.py

from abc import ABC, abstractmethod
from typing import List, Dict, Union
from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.documents.IDocument import IDocument

class IVectorStore(ABC):
    """
    Interface for a vector store responsible for storing, indexing, and retrieving documents.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Stores a single document in the vector store.

        Parameters:
        - document (IDocument): The document to store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Stores multiple documents in the vector store.

        Parameters:
        - documents (List[IDocument]): The list of documents to store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        """
        Retrieves a document by its ID.

        Parameters:
        - doc_id (str): The unique identifier for the document.

        Returns:
        - Union[IDocument, None]: The requested document, or None if not found.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieves all documents stored in the vector store.

        Returns:
        - List[IDocument]: A list of all documents.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Deletes a document from the vector store by its ID.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass

    @abstractmethod
    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store

        """
        pass


    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Updates a document in the vector store.

        Parameters:
        - doc_id (str): The unique identifier for the document to update.
        - updated_document (IDocument): The updated document object.

        Note: It's assumed that the updated_document will retain the same doc_id but may have different content or metadata.
        """
        pass

    @abstractmethod
    def document_count(self) -> int:
        pass 

```

```swarmauri/core/vector_stores/IVectorStoreRetrieve.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.documents.IDocument import IDocument

class IVectorStoreRetrieve(ABC):
    """
    Abstract base class for document retrieval operations.
    
    This class defines the interface for retrieving documents based on a query or other criteria.
    Implementations may use various indexing or search technologies to fulfill these retrievals.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the most relevant documents based on the given query.
        
        Parameters:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
            
        Returns:
            List[Document]: A list of the top_k most relevant documents.
        """
        pass



```

```swarmauri/core/document_stores/IDocumentStore.py

from abc import ABC, abstractmethod
from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument

class IDocumentStore(ABC):
    """
    Interface for a Document Store responsible for storing, indexing, and retrieving documents.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Stores a single document in the document store.

        Parameters:
        - document (IDocument): The document to store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Stores multiple documents in the document store.

        Parameters:
        - documents (List[IDocument]): The list of documents to store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        """
        Retrieves a document by its ID.

        Parameters:
        - doc_id (str): The unique identifier for the document.

        Returns:
        - Union[IDocument, None]: The requested document, or None if not found.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieves all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Deletes a document from the document store by its ID.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass


    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Updates a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier for the document to update.
        - updated_document (IDocument): The updated document object.

        Note: It's assumed that the updated_document will retain the same doc_id but may have different content or metadata.
        """
        pass

    @abstractmethod
    def document_count(self) -> int:
        pass

```

```swarmauri/core/document_stores/__init__.py



```

```swarmauri/core/document_stores/IDocumentRetrieve.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.documents.IDocument import IDocument

class IDocumentRetrieve(ABC):
    """
    Abstract base class for document retrieval operations.
    
    This class defines the interface for retrieving documents based on a query or other criteria.
    Implementations may use various indexing or search technologies to fulfill these retrievals.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the most relevant documents based on the given query.
        
        Parameters:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
            
        Returns:
            List[Document]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/core/chunkers/__init__.py



```

```swarmauri/core/chunkers/IChunker.py

from abc import ABC, abstractmethod
from typing import List, Union, Any

class IChunker(ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """

    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[Any]:
        pass

```

```swarmauri/core/vectors/IVectorMeta.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class IVectorMeta(ABC):
    """
    Interface for a high-dimensional data vector. This interface defines the
    basic structure and operations for interacting with vectors in various applications,
    such as machine learning, information retrieval, and similarity search.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Unique identifier for the vector. This ID can be used to reference the vector
        in a database or a vector store.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """
        Optional metadata associated with the vector. Metadata can include additional information
        useful for retrieval, categorization, or description of the vector data.
        """
        pass



```

```swarmauri/core/vectors/IVectorTransform.py

from abc import ABC, abstractmethod
from .IVector import IVector

class IVectorTransform(ABC):
    """
    Interface for performing various transformations on vectors.
    """

    @abstractmethod
    def translate(self, translation_vector: IVector) -> IVector:
        """
        Translate a vector by a given translation vector.
        """
        pass

    @abstractmethod
    def rotate(self, angle: float, axis: IVector) -> IVector:
        """
        Rotate a vector around a given axis by a certain angle.
        """
        pass

    @abstractmethod
    def reflect(self, plane_normal: IVector) -> IVector:
        """
        Reflect a vector across a plane defined by its normal vector.
        """
        pass

    @abstractmethod
    def scale(self, scale_factor: float) -> IVector:
        """
        Scale a vector by a given scale factor.
        """
        pass

    @abstractmethod
    def shear(self, shear_factor: float, direction: IVector) -> IVector:
        """
        Shear a vector along a given direction by a shear factor.
        """
        pass

    @abstractmethod
    def project(self, plane_normal: IVector) -> IVector:
        """
        Project a vector onto a plane defined by its normal vector.
        """
        pass

```

```swarmauri/core/vectors/IVector.py

from abc import ABC, abstractmethod

class IVector(ABC):
    """
    Interface for a high-dimensional data vector. This interface defines the
    basic structure and operations for interacting with vectors in various applications,
    such as machine learning, information retrieval, and similarity search.
    """

    pass

```

```swarmauri/core/vectors/__init__.py



```

```swarmauri/core/vectors/IVectorProduct.py

from abc import ABC, abstractmethod
from typing import List, Tuple

class IVectorProduct(ABC):
    """
    Interface for various vector products including dot product, cross product,
    and triple products (vector and scalar).
    """

    @abstractmethod
    def dot_product(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate the dot product of two vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.

        Returns:
        - float: The dot product of the two vectors.
        """
        pass

    @abstractmethod
    def cross_product(self, vector_a: List[float], vector_b: List[float]) -> List[float]:
        """
        Calculate the cross product of two vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.

        Returns:
        - List[float]: The cross product as a new vector.
        """
        pass

    @abstractmethod
    def vector_triple_product(self, vector_a: List[float], vector_b: List[float], vector_c: List[float]) -> List[float]:
        """
        Calculate the vector triple product of three vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.
        - vector_c (List[float]): The third vector.

        Returns:
        - List[float]: The result of the vector triple product as a new vector.
        """
        pass

    @abstractmethod
    def scalar_triple_product(self, vector_a: List[float], vector_b: List[float], vector_c: List[float]) -> float:
        """
        Calculate the scalar triple product of three vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.
        - vector_c (List[float]): The third vector.

        Returns:
        - float: The scalar value result of the scalar triple product.
        """
        pass

```

```swarmauri/core/swarm_apis/__init__.py



```

```swarmauri/core/swarm_apis/ISwarmAPI.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISwarmAPI(ABC):
    """
    Interface for managing the swarm's API endpoints.
    """
    
    @abstractmethod
    def dispatch_request(self, request_data: Dict[str, Any]) -> Any:
        """
        Dispatches an incoming user request to one or more suitable agents based on their capabilities.

        Parameters:
        - request_data (Dict[str, Any]): Data related to the incoming request.

        Returns:
        - Any: Response from processing the request.
        """
        pass

    @abstractmethod
    def broadcast_request(self, request_data: Dict[str, Any]) -> Any:
        pass

```

```swarmauri/core/swarm_apis/IAgentRegistrationAPI.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from swarmauri.core.agents.IAgent import IAgent

class IAgentRegistrationAPI(ABC):
    """
    Interface for registering agents with the swarm, designed to support CRUD operations on IAgent instances.
    """

    @abstractmethod
    def register_agent(self, agent: IAgent) -> bool:
        """
        Register a new agent with the swarm.

        Parameters:
            agent (IAgent): An instance of IAgent representing the agent to register.

        Returns:
            bool: True if the registration succeeded; False otherwise.
        """
        pass

    @abstractmethod
    def update_agent(self, agent_id: str, updated_agent: IAgent) -> bool:
        """
        Update the details of an existing agent. This could include changing the agent's configuration,
        task assignment, or any other mutable attribute.

        Parameters:
            agent_id (str): The unique identifier for the agent.
            updated_agent (IAgent): An updated IAgent instance to replace the existing one.

        Returns:
            bool: True if the update was successful; False otherwise.
        """
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the swarm based on its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent to be removed.

        Returns:
            bool: True if the removal was successful; False otherwise.
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[IAgent]:
        """
        Retrieve an agent's instance from its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent of interest.

        Returns:
            Optional[IAgent]: The IAgent instance if found; None otherwise.
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[IAgent]:
        """
        List all registered agents.

        Returns:
            List[IAgent]: A list containing instances of all registered IAgents.
        """
        pass

```

```swarmauri/core/embeddings/__init__.py

#

```

```swarmauri/core/embeddings/IVectorize.py

from abc import ABC, abstractmethod
from typing import List, Union, Any
from swarmauri.core.vectors.IVector import IVector

class IVectorize(ABC):
    """
    Interface for converting text to vectors. 
    Implementations of this interface transform input text into numerical 
    vectors that can be used in machine learning models, similarity calculations, 
    and other vector-based operations.
    """
    @abstractmethod
    def fit(self, data: Union[str, Any]) -> None:
        pass
    
    @abstractmethod
    def transform(self, data: Union[str, Any]) -> List[IVector]:
        pass

    @abstractmethod
    def fit_transform(self, data: Union[str, Any]) -> List[IVector]:
        pass

    @abstractmethod
    def infer_vector(self, data: Union[str, Any], *args, **kwargs) -> IVector:
        pass 

```

```swarmauri/core/embeddings/IFeature.py

from abc import ABC, abstractmethod
from typing import List, Any

class IFeature(ABC):

    @abstractmethod
    def extract_features(self) -> List[Any]:
        pass
    


```

```swarmauri/core/embeddings/ISaveModel.py

from abc import ABC, abstractmethod
from typing import Any

class ISaveModel(ABC):
    """
    Interface to abstract the ability to save and load models.
    """

    @abstractmethod
    def save_model(self, path: str) -> None:
        """
        Saves the model to the specified directory.

        Parameters:
        - path (str): The directory path where the model will be saved.
        """
        pass

    @abstractmethod
    def load_model(self, path: str) -> Any:
        """
        Loads a model from the specified directory.

        Parameters:
        - path (str): The directory path from where the model will be loaded.

        Returns:
        - Returns an instance of the loaded model.
        """
        pass

```

```swarmauri/core/tracing/__init__.py



```

```swarmauri/core/tracing/ITraceContext.py

from abc import ABC, abstractmethod
from typing import Any

class ITraceContext(ABC):
    """
    Interface for a trace context, representing a single trace instance.
    This context carries the state and metadata of the trace across different system components.
    """

    @abstractmethod
    def get_trace_id(self) -> str:
        """
        Retrieves the unique identifier for this trace.

        Returns:
            str: The unique trace identifier.
        """
        pass

    @abstractmethod
    def add_attribute(self, key: str, value: Any):
        """
        Adds or updates an attribute associated with this trace.

        Args:
            key (str): The attribute key or name.
            value (Any): The value of the attribute.
        """
        pass

```

```swarmauri/core/tracing/ITracer.py

from swarmauri.core.tracing.ITraceContext import ITraceContext
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class ITracer(ABC):
    """
    Interface for implementing distributed tracing across different components of the system.
    """

    @abstractmethod
    def start_trace(self, name: str, initial_attributes: Optional[Dict[str, Any]] = None) -> ITraceContext:
        """
        Starts a new trace with a given name and optional initial attributes.

        Args:
            name (str): Name of the trace, usually represents the operation being traced.
            initial_attributes (Optional[Dict[str, Any]]): Key-value pairs to be attached to the trace initially.

        Returns:
            ITraceContext: A context object representing this particular trace instance.
        """
        pass

    @abstractmethod
    def end_trace(self, trace_context: ITraceContext):
        """
        Marks the end of a trace, completing its lifecycle and recording its details.

        Args:
            trace_context (ITraceContext): The trace context to be ended.
        """
        pass

    @abstractmethod
    def annotate_trace(self, trace_context: ITraceContext, key: str, value: Any):
        """
        Adds an annotation to an existing trace, enriching it with more detailed information.

        Args:
            trace_context (ITraceContext): The trace context to annotate.
            key (str): The key or name of the annotation.
            value (Any): The value of the annotation.
        """
        pass

```

```swarmauri/core/tracing/IChainTracer.py

from abc import ABC, abstractmethod
from typing import Callable, List, Tuple, Dict, Any

class IChainTracer(ABC):
    """
    Interface for a tracer supporting method chaining through a list of tuples.
    Each tuple in the list contains: trace context, function, args, and kwargs.
    """

    @abstractmethod
    def process_chain(self, chain: List[Tuple[Any, Callable[..., Any], List[Any], Dict[str, Any]]]) -> "IChainTracer":
        """
        Processes a sequence of operations defined in a chain.

        Args:
            chain (List[Tuple[Any, Callable[..., Any], List[Any], Dict[str, Any]]]): A list where each tuple contains:
                - The trace context or reference required by the function.
                - The function (method of IChainTracer) to execute.
                - A list of positional arguments for the function.
                - A dictionary of keyword arguments for the function.

        Returns:
            IChainTracer: Returns self to allow further method chaining.
        """
        pass

```

```swarmauri/core/chains/ICallableChain.py

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple

CallableDefinition = Tuple[Callable, List[Any], dict]

class ICallableChain(ABC):
    @abstractmethod
    def __call__(self, *initial_args: Any, **initial_kwargs: Any) -> Any:
        """Executes the chain of callables."""
        pass

    @abstractmethod
    def add_callable(self, func: Callable, args: List[Any] = None, kwargs: dict = None) -> None:
        """Adds a new callable to the chain."""
        pass

```

```swarmauri/core/chains/__init__.py

from swarmauri.core.chains.ICallableChain import ICallableChain

```

```swarmauri/core/chains/IChain.py

from abc import ABC, abstractmethod
from typing import List, Any, Dict
from swarmauri.core.chains.IChainStep import IChainStep

class IChain(ABC):
    """
    Defines the interface for a Chain within a system, facilitating the organized
    execution of a sequence of tasks or operations. This interface is at the core of
    orchestrating operations that require coordination between multiple steps, potentially
    involving decision-making, branching, and conditional execution based on the outcomes
    of previous steps or external data.

    A chain can be thought of as a workflow or pipeline, where each step in the chain can
    perform an operation, transform data, or make decisions that influence the flow of
    execution.

    Implementors of this interface are responsible for managing the execution order,
    data flow between steps, and any dynamic adjustments to the execution based on
    runtime conditions.

    Methods:
        add_step: Adds a step to the chain.
        remove_step: Removes a step from the chain.
        execute: Executes the chain, potentially returning a result.
    """

    @abstractmethod
    def add_step(self, step: IChainStep, **kwargs) -> None:
        """
        Adds a new step to the chain. Steps are executed in the order they are added.
        Each step is represented by a Callable, which can be a function or method, with
        optional keyword arguments that specify execution aspects or data needed by the step.

        Parameters:
            step (IChainStep): The Callable representing the step to add to the chain.
            **kwargs: Optional keyword arguments that provide additional data or configuration
                      for the step when it is executed.
        """
        pass

    @abstractmethod
    def remove_step(self, step: IChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (IChainStep): The Callable representing the step to remove from the chain.
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Initiates the execution of the chain. This involves invoking each step in the order
        they have been added to the chain, passing control from one step to the next, and optionally
        aggregating or transforming results along the way.

        The execution process can incorporate branching, looping, or conditional logic based on the
        implementation, allowing for complex workflows to be represented and managed within the chain.

        Parameters:
            *args: Positional arguments passed to the first step in the chain. These can be data inputs
                   or other values required for the chain's execution.
            **kwargs: Keyword arguments that provide additional context, data inputs, or configuration
                      for the chain's execution. These can be passed to individual steps or influence
                      the execution flow of the chain.

        Returns:
            Any: The outcome of executing the chain. This could be a value produced by the final
                 step, a collection of outputs from multiple steps, or any other result type as
                 determined by the specific chain implementation.
        """
        pass

```

```swarmauri/core/chains/IChainFactory.py

from abc import ABC, abstractmethod
from typing import List, Any, Dict
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep

class IChainFactory(ABC):
    """
    Interface for creating and managing execution chains within the system.
    """

    @abstractmethod
    def create_chain(self, steps: List[IChainStep] = None) -> IChain:
        pass
    
    
    @abstractmethod
    def get_chain(self) -> IChain:
        pass
    
    @abstractmethod
    def set_chain(self, chain: IChain):
        pass
    
    @abstractmethod
    def reset_chain(self):
        pass
    
    @abstractmethod
    def get_chain_steps(self) -> List[IChainStep]:
        pass
    
    @abstractmethod
    def set_chain_steps(self, steps: List[IChainStep]):
        pass
    
    @abstractmethod
    def add_chain_step(self, step: IChainStep):
        pass
    
    @abstractmethod
    def remove_chain_step(self, key: str):
        pass
    
    @abstractmethod
    def get_configs(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def set_configs(self, **configs):
        pass
    
    @abstractmethod
    
    def get_config(self, key: str) -> Any:
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any):
        pass
    



```

```swarmauri/core/chains/IChainStep.py

from typing import List, Dict, Any, Callable

class IChainStep:
    """
    Represents a single step within an execution chain.
    """
    pass

```

```swarmauri/core/chains/IChainContextLoader.py

from abc import ABC, abstractmethod
from typing import Dict, Any

class IChainContextLoader(ABC):
    @abstractmethod
    def load_context(self, context_id: str) -> Dict[str, Any]:
        """Load the execution context by its identifier."""
        pass

```

```swarmauri/core/chains/IChainDependencyResolver.py

from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional
from swarmauri.standard.chains.concrete.ChainStep import ChainStep

class IChainDependencyResolver(ABC):
    @abstractmethod
    def build_dependencies(self) -> List[ChainStep]:
        """
        Builds the dependencies for a particular sequence in the matrix.

        Args:
            matrix (List[List[str]]): The prompt matrix.
            sequence_index (int): The index of the sequence to build dependencies for.

        Returns:
            Tuple containing indegrees and graph dicts.
        """
        pass

    @abstractmethod
    def resolve_dependencies(self, matrix: List[List[Optional[str]]], sequence_index: int) -> List[int]:
        """
        Resolves the execution order based on the provided dependencies.

        Args:
            indegrees (Dict[int, int]): The indegrees of each node.
            graph (Dict[int, List[int]]): The graph representing dependencies.

        Returns:
            List[int]: The resolved execution order.
        """
        pass

```

```swarmauri/core/chains/IChainContext.py

from abc import ABC, abstractmethod
from typing import Dict, Any

class IChainContext(ABC):
    
    @abstractmethod
    def update(self, **kwargs) -> None:
        pass

    def get_value(self, key: str) -> Any:
        pass

```

```swarmauri/core/distances/__init__.py



```

```swarmauri/core/distances/IDistanceSimilarity.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.vectors.IVector import IVector

class IDistanceSimilarity(ABC):
    """
    Interface for computing distances and similarities between high-dimensional data vectors. This interface
    abstracts the method for calculating the distance and similarity, allowing for the implementation of various 
    distance metrics such as Euclidean, Manhattan, Cosine similarity, etc.
    """

    @abstractmethod
    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed distance between vector_a and vector_b.
        """
        pass
    

    @abstractmethod
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> float:
        pass


    @abstractmethod
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors. The definition of similarity (e.g., cosine similarity)
        should be implemented in concrete classes.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        pass

    @abstractmethod
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> float:
        pass


```

```swarmauri/core/metrics/__init__.py



```

```swarmauri/core/metrics/IMetric.py

from typing import Any
from abc import ABC, abstractmethod

class IMetric(ABC):
    """
    Defines a general interface for metrics within the SwarmaURI system.
    Metrics can be anything from system performance measurements to
    machine learning model evaluation metrics.
    """

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        pass

```

```swarmauri/core/metrics/IMetricCalculate.py

from typing import Any
from abc import ABC, abstractmethod

class IMetricCalculate(ABC):

    @abstractmethod
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the metric based on the provided data.

        Args:
            *args: Variable length argument list that the metric calculation might require.
            **kwargs: Arbitrary keyword arguments that the metric calculation might require.
        """
        pass

    @abstractmethod
    def update(self, value) -> None:
        """
        Update the metric value based on new information.

        Args:
            value: The new information used to update the metric. This could be a new
            measurement or data point that affects the metric's current value.

        Note:
            This method is intended for internal use and should not be publicly accessible.
        """
        pass
        

```

```swarmauri/core/metrics/IMetricAggregate.py

from typing import List, Any
from abc import ABC, abstractmethod

class IMetricAggregate(ABC):

    @abstractmethod
    def add_measurement(self, measurement: Any) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset or clear the metric's current state, starting fresh as if no data had been processed.
        This is useful for metrics that might aggregate or average data over time and need to be reset.
        """
        pass

```

```swarmauri/core/metrics/IThreshold.py

from abc import ABC, abstractmethod

class IThreshold(ABC):
    pass


```

```swarmauri/core/experiment_stores/__init__.py

# core/experiment_stores/IExperimentStore.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from swarmauri.core.documents.IExperimentDocument import IExperimentDocument

class IExperimentStore(ABC):
    """
    Interface for an Experiment Store that manages experimental documents and supports
    operations related to experimenting, evaluating, testing, and benchmarking.
    """
    @abstractmethod
    def add_experiment(self, experiment: IExperimentDocument) -> None:
        """
        Stores a single experiment in the experiment store.

        Parameters:
        - experiment (IExperimentDocument): The experimental document to be stored.
        """
        pass

    @abstractmethod
    def add_experiments(self, experiments: List[IExperimentDocument]) -> None:
        """
        Stores multiple experiments in the experiment store.

        Parameters:
        - experiments (List[IExperimentDocument]): The list of experimental documents to be stored.
        """
        pass

    @abstractmethod
    def get_experiment(self, experiment_id: str) -> Union[IExperimentDocument, None]:
        """
        Retrieves an experimental document by its ID.

        Parameters:
        - id (str): The unique identifier of the experiment.

        Returns:
        - Union[IExperimentDocument, None]: The requested experimental document, or None if not found.
        """
        pass

    @abstractmethod
    def get_all_experiments(self) -> List[IExperimentDocument]:
        """
        Retrieves all experimental documents stored in the experiment store.

        Returns:
        - List[IExperimentDocument]: A list of all experimental documents.
        """
        pass

    @abstractmethod
    def update_experiment(self, experiment_id: str, updated_experiment: IExperimentDocument) -> None:
        """
        Updates an experimental document in the experiment store.

        Parameters:
        - id (str): The unique identifier of the experiment to update.
        - updated_experiment (IExperimentDocument): The updated experimental document.
        """
        pass

    @abstractmethod
    def delete_experiment(self, experiment_id: str) -> None:
        """
        Deletes an experimental document from the experiment store by its ID.

        Parameters:
        - id (str): The unique identifier of the experimental document to be deleted.
        """
        pass

    @abstractmethod
    def evaluate_experiments(self, evaluation_criteria: Dict[str, Any]) -> Any:
        """
        Evaluates the experiments stored in the experiment store based on given criteria and metrics.

        Parameters:
        - evaluation_criteria (Dict[str, Any]): The criteria and metrics to evaluate the experiments.

        Returns:
        - Any: The evaluation results, which may vary depending on the evaluation criteria.
        """
        pass

    @abstractmethod
    def benchmark_experiments(self, benchmarking_data: Dict[str, Any]) -> Any:
        """
        Benchmarks the experiments against each other or predefined standards.

        Parameters:
        - benchmarking_data (Dict[str, Any]): Data and parameters for benchmarking the experiments.

        Returns:
        - Any: The benchmark results, which may vary depending on the benchmarking methodology.
        """
        pass

```

```swarmauri/core/experiment_stores/IExperimentStore.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from swarmauri.core.documents.IExperimentDocument import IExperimentDocument

class IExperimentStore(ABC):
    """
    Interface for an Experiment Store that manages experimental documents and supports
    operations related to experimenting, evaluating, testing, and benchmarking.
    """
    @abstractmethod
    def add_experiment(self, experiment: IExperimentDocument) -> None:
        """
        Stores a single experiment in the experiment store.

        Parameters:
        - experiment (IExperimentDocument): The experimental document to be stored.
        """
        pass

    @abstractmethod
    def add_experiments(self, experiments: List[IExperimentDocument]) -> None:
        """
        Stores multiple experiments in the experiment store.

        Parameters:
        - experiments (List[IExperimentDocument]): The list of experimental documents to be stored.
        """
        pass

    @abstractmethod
    def get_experiment(self, experiment_id: str) -> Union[IExperimentDocument, None]:
        """
        Retrieves an experimental document by its ID.

        Parameters:
        - experiment_id (str): The unique identifier of the experiment.

        Returns:
        - Union[IExperimentDocument, None]: The requested experimental document, or None if not found.
        """
        pass

    @abstractmethod
    def get_all_experiments(self) -> List[IExperimentDocument]:
        """
        Retrieves all experimental documents stored in the experiment store.

        Returns:
        - List[IExperimentDocument]: A list of all experimental documents.
        """
        pass

    @abstractmethod
    def update_experiment(self, experiment_id: str, updated_experiment: IExperimentDocument) -> None:
        """
        Updates an experimental document in the experiment store.

        Parameters:
        - experiment_id (str): The unique identifier of the experiment to update.
        - updated_experiment (IExperimentDocument): The updated experimental document.
        """
        pass

    @abstractmethod
    def delete_experiment(self, experiment_id: str) -> None:
        """
        Deletes an experimental document from the experiment store by its ID.

        Parameters:
        - experiment_id (str): The unique identifier of the experimental document to be deleted.
        """
        pass

```

```swarmauri/core/agent_factories/IAgentFactory.py

from abc import ABC, abstractmethod
from typing import Type, Any
from datetime import datetime

class IAgentFactory(ABC):
    """
    Interface for Agent Factories, extended to include properties like ID, name, type,
    creation date, and last modification date.
    """

    @abstractmethod
    def create_agent(self, agent_type: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def register_agent(self, agent_type: str, constructor: Type[Any]) -> None:
        pass

    # Abstract properties and setters
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the factory instance."""
        pass

    @id.setter
    @abstractmethod
    def id(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the factory."""
        pass

    @name.setter
    @abstractmethod
    def name(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """Type of agents this factory produces."""
        pass

    @type.setter
    @abstractmethod
    def type(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def date_created(self) -> datetime:
        """The creation date of the factory instance."""
        pass

    @property
    @abstractmethod
    def last_modified(self) -> datetime:
        """Date when the factory was last modified."""
        pass

    @last_modified.setter
    @abstractmethod
    def last_modified(self, value: datetime) -> None:
        pass

    def __hash__(self):
        """
        The __hash__ method allows objects of this class to be used in sets and as dictionary keys.
        __hash__ should return an integer and be defined based on immutable properties.
        This is generally implemented directly in concrete classes rather than in the interface,
        but it's declared here to indicate that implementing classes must provide it.
        """
        pass

   

```

```swarmauri/core/agent_factories/__init__.py



```

```swarmauri/core/agent_factories/IExportConf.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class IExportConf(ABC):
    """
    Interface for exporting configurations related to agent factories.
    
    Implementing classes are expected to provide functionality for representing
    the factory's configuration as a dictionary, JSON string, or exporting to a file.
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the agent factory's configuration to a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the factory's configuration.
        """
        pass

    @abstractmethod
    def to_json(self) -> str:
        """
        Serializes the agent factory's configuration to a JSON string.
        
        Returns:
            str: A JSON string representation of the factory's configuration.
        """
        pass

    @abstractmethod
    def to_file(self, file_path: str) -> None:
        """
        Exports the agent factory's configuration to a file in a suitable format.
        
        Parameters:
            file_path (str): The path to the file where the configuration should be saved.
        """
        pass

```

```swarmauri/core/schema_converters/__init__.py



```

```swarmauri/core/schema_converters/ISchemaConvert.py

from abc import ABC, abstractmethod
from typing import Any, Dict
from swarmauri.core.tools.ITool import ITool

class ISchemaConvert(ABC):

    @abstractmethod
    def convert(self, tool: ITool) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the convert method.")


```

```swarmauri/experimental/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/RemoteUniversalBase.py

import requests
import hashlib
from functools import wraps
from uuid import uuid4
import inspect

def remote_local_transport(cls):
    original_init = cls.__init__
    def init_wrapper(self, *args, **kwargs):
        host = kwargs.pop('host', None)
        resource = kwargs.get('resource', cls.__name__)
        owner = kwargs.get('owner')
        name = kwargs.get('name')
        id = kwargs.get('id')
        #path = kwargs.get('path')
        if host:
            #self.is_remote = True
            self.host = host
            self.resource = resource
            self.owner = owner
            self.id = id
            #self.path = path
            url = f"{host}/{owner}/{resource}/{id}"
            data = {"class_name": cls.__name__, "owner": owner, "name": name, **kwargs}
            response = requests.post(url, json=data)
            if not response.ok:
                raise Exception(f"Failed to initialize remote {cls.__name__}: {response.text}")
        else:
            original_init(self, owner, name, **kwargs)  # Ensure proper passing of positional arguments

    setattr(cls, '__init__', init_wrapper)

    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("_"):
            setattr(cls, attr_name, method_wrapper(attr_value))
        elif isinstance(attr_value, property):
            prop_get = attr_value.fget and method_wrapper(attr_value.fget)
            prop_set = attr_value.fset and method_wrapper(attr_value.fset)
            prop_del = attr_value.fdel and method_wrapper(attr_value.fdel)
            setattr(cls, attr_name, property(prop_get, prop_set, prop_del, attr_value.__doc__))
    return cls


def method_wrapper(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        self = args[0]
        if getattr(self, 'host'):
            print('[x] Executing remote call...')
            url = f"{self.path}".lower()
            response = requests.post(url, json={"args": args[1:], "kwargs": kwargs})
            if response.ok:
                return response.json()
            else:
                raise Exception(f"Remote method call failed: {response.text}")
        else:
            return method(*args, **kwargs)
    return wrapper

class RemoteLocalMeta(type):
    def __new__(metacls, name, bases, class_dict):
        cls = super().__new__(metacls, name, bases, class_dict)
        if bases:  # This prevents BaseComponent itself from being decorated
            cls = remote_local_transport(cls)
        cls.class_hash = cls._calculate_class_hash()
        return cls

    def _calculate_class_hash(cls):
        sig_hash = hashlib.sha256()
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not attr_name.startswith("_"):
                sig = inspect.signature(attr_value)
                sig_hash.update(str(sig).encode())
        return sig_hash.hexdigest()
    

class BaseComponent(metaclass=RemoteLocalMeta):
    version = "1.0.0"  # Semantic versioning initialized here
    def __init__(self, owner, name, host=None, members=[], resource=None):
        self.id = uuid4()
        self.owner = owner
        self.name = name
        self.host = host  
        #self.is_remote = bool(self.host) 
        self.members = members
        self.resource = resource if resource else self.__class__.__name__
        self.path = f"{self.host if self.host else ''}/{self.owner}/{self.resource}/{self.id}"

    @property
    def is_remote(self):
        return bool(self.host)

    @classmethod
    def public_interfaces(cls):
        methods = []
        for attr_name in dir(cls):
            # Retrieve the attribute
            attr_value = getattr(cls, attr_name)
            # Check if it's callable or a property and not a private method
            if (callable(attr_value) and not attr_name.startswith("_")) or isinstance(attr_value, property):
                methods.append(attr_name)
        return methods

    @classmethod
    def is_method_registered(cls, method_name):
        """
        Checks if a public method with the given name is registered on the class.
        Args:
            method_name (str): The name of the method to check.
        Returns:
            bool: True if the method is registered, False otherwise.
        """
        return method_name in cls.public_interfaces()

    @classmethod
    def method_with_signature(cls, input_signature):
        """
        Checks if there is a method with the given signature available in the class.
        
        Args:
            input_signature (str): The string representation of the method signature to check.
        
        Returns:
            bool: True if a method with the input signature exists, False otherwise.
        """
        for method_name in cls.public_interfaces():
            method = getattr(cls, method_name)
            if callable(method):
                sig = str(inspect.signature(method))
                if sig == input_signature:
                    return True
        return False

```

```swarmauri/experimental/tools/LinkedInArticleTool.py

import requests
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class LinkedInArticleTool(ToolBase):
    """
    A tool to post articles on LinkedIn using the LinkedIn API.
    """
    def __init__(self, access_token):
        """
        Initializes the LinkedInArticleTool with the necessary access token.
        
        Args:
            access_token (str): The OAuth access token for authenticating with the LinkedIn API.
        """
        super().__init__(name="LinkedInArticleTool",
                         description="A tool for posting articles on LinkedIn.",
                         parameters=[
                             Parameter(name="title", type="string", description="The title of the article", required=True),
                             Parameter(name="text", type="string", description="The body text of the article", required=True),
                             Parameter(name="visibility", type="string", description="The visibility of the article", required=True, enum=["anyone", "connectionsOnly"])
                         ])
        self.access_token = access_token
        
    def __call__(self, title: str, text: str, visibility: str = "anyone") -> str:
        """
        Posts an article on LinkedIn.

        Args:
            title (str): The title of the article.
            text (str): The body text of the article.
            visibility (str): The visibility of the article, either "anyone" or "connectionsOnly".

        Returns:
            str: A message indicating the success or failure of the post operation.
        """
        # Construct the request URL and payload according to LinkedIn API documentation
        url = 'https://api.linkedin.com/v2/ugcPosts'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "author": "urn:li:person:YOUR_PERSON_ID_HERE",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": title
                            },
                            "originalUrl": "URL_OF_THE_ARTICLE_OR_IMAGE",
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
            }
        }
     
        # Make the POST request to LinkedIn's API
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return f"Article posted successfully: {response.json().get('id')}"
        else:
            return f"Failed to post the article. Status Code: {response.status_code} - {response.text}"

```

```swarmauri/experimental/tools/TwitterPostTool.py

from tweepy import Client

from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class TwitterPostTool(ToolBase):
    def __init__(self, bearer_token):
        # Initialize parameters necessary for posting a tweet
        parameters = [
            Parameter(
                name="status",
                type="string",
                description="The status message to post on Twitter",
                required=True
            )
        ]
        
        super().__init__(name="TwitterPostTool", description="Post a status update on Twitter", parameters=parameters)
        
        # Initialize Twitter API Client
        self.client = Client(bearer_token=bearer_token)

    def __call__(self, status: str) -> str:
        """
        Posts a status on Twitter.

        Args:
            status (str): The status message to post.

        Returns:
            str: A confirmation message including the tweet's URL if successful.
        """
        try:
            # Using Tweepy to send a tweet
            response = self.client.create_tweet(text=status)
            tweet_id = response.data['id']
            # Constructing URL to the tweet - Adjust the URL to match Twitter API v2 structure if needed
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            return f"Tweet successful: {tweet_url}"
        except Exception as e:
            return f"An error occurred: {e}"

```

```swarmauri/experimental/tools/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/tools/OutlookSendMailTool.py

import requests
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class OutlookSendMailTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="recipient",
                type="string",
                description="The email address of the recipient",
                required=True
            ),
            Parameter(
                name="subject",
                type="string",
                description="The subject of the email",
                required=True
            ),
            Parameter(
                name="body",
                type="string",
                description="The HTML body of the email",
                required=True
            )
        ]
        
        super().__init__(name="OutlookSendMailTool", 
                         description="Sends an email using the Outlook service.",
                         parameters=parameters)

        # Add your Microsoft Graph API credentials and endpoint URL here
        self.tenant_id = "YOUR_TENANT_ID"
        self.client_id = "YOUR_CLIENT_ID"
        self.client_secret = "YOUR_CLIENT_SECRET"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

    def get_access_token(self):
        data = {
            "client_id": self.client_id,
            "scope": " ".join(self.scope),
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json().get("access_token")

    def __call__(self, recipient, subject, body):
        access_token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient
                        }
                    }
                ]
            }
        }

        send_mail_endpoint = f"{self.graph_endpoint}/users/{self.client_id}/sendMail"
        response = requests.post(send_mail_endpoint, json=email_data, headers=headers)
        if response.status_code == 202:
            return "Email sent successfully"
        else:
            return f"Failed to send email, status code {response.status_code}"

```

```swarmauri/experimental/tools/CypherQueryTool.py

import json
from neo4j import GraphDatabase
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class CypherQueryTool(ToolBase):
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        
        # Define only the 'query' parameter since uri, user, and password are set at initialization
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="The Cypher query to execute.",
                required=True
            )
        ]
        
        super().__init__(name="CypherQueryTool",
                         description="Executes a Cypher query against a Neo4j database.",
                         parameters=parameters)

    def _get_connection(self):
        return GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def __call__(self, query) -> str:
        # Establish connection to the database
        driver = self._get_connection()
        session = driver.session()

        # Execute the query
        result = session.run(query)
        records = result.data()

        # Close the connection
        session.close()
        driver.close()

        # Convert records to JSON string, assuming it's JSON serializable
        return json.dumps(records)

```

```swarmauri/experimental/tools/FileDownloaderTool.py

import requests
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class FileDownloaderTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="The URL of the file to download",
                required=True
            )
        ]
        
        super().__init__(name="FileDownloaderTool",
                         description="Downloads a file from a specified URL into memory.",
                         parameters=parameters)
    
    def __call__(self, url: str) -> bytes:
        """
        Downloads a file from the given URL into memory.
        
        Parameters:
        - url (str): The URL of the file to download.
        
        Returns:
        - bytes: The content of the downloaded file.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the request resulted in an error
            return response.content
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download file from '{url}'. Error: {e}")

```

```swarmauri/experimental/tools/SQLite3QueryTool.py

import sqlite3
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class SQLite3QueryTool(ToolBase):
    def __init__(self, db_name: str):
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="SQL query to execute",
                required=True
            )
        ]
        super().__init__(name="SQLQueryTool", 
                         description="Executes an SQL query and returns the results.", 
                         parameters=parameters)
        self.db_name = db_name

    def __call__(self, query) -> str:
        """
        Execute the provided SQL query.

        Parameters:
        - query (str): The SQL query to execute.

        Returns:
        - str: The results of the SQL query as a string.
        """
        try:
            connection = sqlite3.connect(self.db_name)  # Connect to the specific database file
            cursor = connection.cursor()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            result = "\n".join(str(row) for row in rows)
        except Exception as e:
            result = f"Error executing query: {e}"
        finally:
            connection.close()
        
        return f"Query Result:\n{result}"

```

```swarmauri/experimental/conversations/__init__.py



```

```swarmauri/experimental/conversations/SemanticConversation.py

from abc import ABC, abstractmethod
from typing import Callable, Dict, Union
from ...core.messages.IMessage import IMessage
from ...core.conversations.IConversation import IConversation

class SemanticConversation(IConversation, ABC):
    """
    A concrete implementation of the Conversation class that includes semantic routing.
    Semantic routing involves analyzing the content of messages to understand their intent
    or category and then routing them to appropriate handlers based on that analysis.

    This class requires subclasses to implement the _analyze_message method for semantic analysis.
    """


    @abstractmethod
    def register_handler(self, category: str, handler: Callable[[IMessage], None]):
        """
        Registers a message handler for a specific semantic category.

        Args:
            category (str): The category of messages this handler should process.
            handler (Callable[[Message], None]): The function to call for messages of the specified category.
        """
        pass

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and routes it to the appropriate handler based on its semantic category.

        Args:
            message (Message): The message to be added and processed.
        """
        pass

    @abstractmethod
    def _analyze_message(self, message: IMessage) -> Union[str, None]:
        """
        Analyzes the content of a message to determine its semantic category.

        This method must be implemented by subclasses to provide specific logic for semantic analysis.

        Args:
            message (Message): The message to analyze.

        Returns:
            Union[str, None]: The semantic category of the message, if determined; otherwise, None.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the _analyze_message method to provide semantic analysis.")

    # Additional methods as needed for message retrieval, history management, etc., inherited from Conversation

```

```swarmauri/experimental/conversations/ConsensusBuildingConversation.py

from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages.IMessage import IMessage


class ConsensusBuildingMessage(IMessage):
    def __init__(self, sender_id: str, content: str, message_type: str):
        self._sender_id = sender_id
        self._content = content
        self._role = 'consensus_message'
        self._message_type = message_type

    @property
    def role(self) -> str:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    def as_dict(self) -> dict:
        return {
            "sender_id": self._sender_id,
            "content": self._content,
            "message_type": self._message_type
        }


class ConsensusBuildingConversation(IConversation):
    def __init__(self, topic: str, participants: list):
        self.topic = topic
        self.participants = participants  # List of agent IDs
        self._history = []  # Stores all messages exchanged in the conversation
        self.proposal_votes = {}  # Tracks votes for each proposal

    @property
    def history(self) -> list:
        return self._history

    def add_message(self, message: IMessage):
        if not isinstance(message, ConsensusBuildingMessage):
            raise ValueError("Only instances of ConsensusBuildingMessage are accepted")
        self._history.append(message)

    def get_last(self) -> IMessage:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self) -> None:
        self._history.clear()

    def as_dict(self) -> list:
        return [message.as_dict() for message in self._history]

    def initiate_consensus(self, initiator_id: str, proposal=None):
        """Starts the conversation with an initial proposal, if any."""
        initiate_message = ConsensusBuildingMessage(initiator_id, proposal, "InitiateConsensusMessage")
        self.add_message(initiate_message)

    def add_proposal(self, sender_id: str, proposal: str):
        """Adds a proposal to the conversation."""
        proposal_message = ConsensusBuildingMessage(sender_id, proposal, "ProposalMessage")
        self.add_message(proposal_message)

    def add_comment(self, sender_id: str, comment: str):
        """Adds a comment or feedback regarding a proposal."""
        comment_message = ConsensusBuildingMessage(sender_id, comment, "CommentMessage")
        self.add_message(comment_message)

    def vote(self, sender_id: str, vote: str):
        """Registers a vote for a given proposal."""
        vote_message = ConsensusBuildingMessage(sender_id, vote, "VoteMessage")
        self.add_message(vote_message)
        # Count the vote
        self.proposal_votes[vote] = self.proposal_votes.get(vote, 0) + 1

    def check_agreement(self):
        """
        Checks if there is a consensus on any proposal.
        A simple majority (>50% of the participants) is required for consensus.
        """
        consensus_threshold = len(self.participants) / 2  # Define consensus as a simple majority

        for proposal, votes in self.proposal_votes.items():
            if votes > consensus_threshold:
                # A consensus has been reached
                return True, f"Consensus reached on proposal: {proposal} with {votes} votes."

        # If no consensus is reached
        return False, "No consensus reached."

```

```swarmauri/experimental/conversations/ConsensusBuildingConversation.md

show an example implementation with a ConsensusBuildingConversation, 3 swarm agents with openaimodels that use gpt-4-0125-preview, and a prompttemplate that is used to start their consensus. the prompttemplate should trigger the first agent to make a proposal to solve a task.
To create a ConsensusBuildingConversation scenario with 3 Swarm Agents utilizing OpenAI models based on GPT-4 and initiating the conversation with a PromptTemplate to solve a task, let's structure it step-by-step. We'll start by defining the necessary components:

1. **ConsensusBuildingConversation** - Manages the flow of messages and consensus building among agents.
2. **Swarm Agents** - Three agents equipped with GPT-4-based models, OpenAIToolModel, to generate proposals and participate in consensus.
3. **PromptTemplate** - Used to kickstart the conversation with a specific task.

Here's an example implementation in Python:

```python
# File: OpenAIToolModel.py
from swarmauri.standard.models.base.ModelBase import ModelBase
from swarmauri.core.models.IPredict import IPredict
from openai import OpenAI

class OpenAIToolModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "gpt-4-0125-preview"):
        super().__init__(model_name)
        self.client = OpenAI(api_key=api_key)

    def predict(self, prompt: str) -> str:
        response = self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].text.strip()

# File: swarmauri/standard/prompts/concrete/PromptTemplate.py (already provided in the defined implementation)
from ..base.PromptBase import PromptBase

class PromptTemplate(PromptBase):
    def __init__(self, template: str = "", variables: Dict[str, str] = {}):
        super().__init__(template, variables)

    def __call__(self, variables: Dict[str, str] = {}):
        formatted_prompt = self.template.format(**variables)
        return formatted_prompt

# File: ConsensusBuildingConversation.py (provided in the example)
# Implementation of `ConsensusBuildingConversation` with method `initiate_consensus` to start the conversation

# Define Swarm Agents with OpenAIToolModel
class SwarmAgent:
    def __init__(self, model):
        self.model = model

    def contribute_to_conversation(self, prompt):
        proposal = self.model.predict(prompt)
        return proposal

# Set up PromptTemplate for initiating the consensus
task_description = "Solve the problem of efficiently distributing vaccines in a fair manner."
prompt_template = PromptTemplate(template="How should we approach: {task}?", variables={"task": task_description})

# Initialize OpenAI Models for each Agent (fake API key for demonstration)
api_key = "your_openai_api_key"
agent1 = SwarmAgent(OpenAIToolModel(api_key))
agent2 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant1"))
agent3 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant2"))

# Start the conversation with a task
initiating_prompt = prompt_template()
print(f"Initiating Prompt: {initiating_prompt}")

# Agent 1 makes the first proposal
first_proposal = agent1.contribute_to_conversation(initiating_prompt)
print(f"Agent 1 proposes: {first_proposal}")

# From here, you could continue the flow where Agent 2 and 3 provide feedback, additional proposals,
# and the conversation is steered towards building consensus as per `ConsensusBuildingConversation` logic.

```

In this example:
- We initialize three agents with the `OpenAIToolModel`, configured to use a GPT-4 model (assuming the `gpt-4-0125-preview` identifier and variants are placeholders for actual GPT-4 model identifiers).
- A `PromptTemplate` is defined and used to kickstart the conversation by generating an initiating prompt.
- Agent 1 reads the initiating prompt and makes the first proposal towards solving the task.
- Next steps (not fully implemented) involve other agents reacting to the proposal, contributing their ideas, and the group collectively moving towards a consensus.

This example provides a starting point. The actual consensus logic, including how proposals are voted on and a consensus is reached, would need to be implemented within the `ConsensusBuildingConversation` logic using methods such as `add_proposal`, `add_comment`, and `check_agreement`.

?  show the rest of the consensusbuildingconversation
Building upon the initial setup, we'll now flesh out the rest of the `ConsensusBuildingConversation` to demonstrate how agents might engage in a consensus-driven discussion, leveraging their unique capabilities or viewpoints generated by their respective GPT-4 models. This extension will include methods for agents to add proposals, comments, and votes, along with the mechanism to check for and reach consensus.

### Step 1: Expansion of ConsensusBuildingMessage and Conversation Classes

We'll start with expanding the `ConsensusBuildingMessage` type for various message kinds, and then work on the conversation logic to incorporate consensus mechanisms.

```python
# Considering ConsensusBuildingMessage and SharedConversation classes are defined,
# let's elaborate on different message types: Proposal and Comment.

class ConsensusBuildingMessage:
    def __init__(self, sender_id: str, content: str, message_type: str = "proposal"):
        self.sender_id = sender_id
        self.content = content
        self.type = message_type  # can be 'proposal', 'comment', or 'vote'
    
    def __str__(self):
        return f"[{self.type.upper()} by {self.sender_id}]: {self.content}"
```

### Step 2: Adding Proposals, Comments, and Votes

Now, let's implement functionalities for agents to add proposals, comments, and how the conversation tracks votes to reach a consensus.

```python
class ConsensusBuildingConversation:
    def __init__(self):
        self.messages = []
        self.votes = {}

    def add_message(self, message: ConsensusBuildingMessage):
        print(str(message))
        self.messages.append(message)
        if message.type == "vote":
            self.votes[message.content] = self.votes.get(message.content, 0) + 1

    def initiate_consensus(self, task_description):
        initiate_message = ConsensusBuildingMessage("admin", task_description, "task")
        self.add_message(initiate_message)

    def add_proposal(self, agent_id, proposal):
        proposal_message = ConsensusBuildingMessage(agent_id, proposal, "proposal")
        self.add_message(proposal_message)

    def add_comment(self, agent_id, comment):
        comment_message = ConsensusBuildingMessage(agent_id, comment, "comment")
        self.add_message(comment_message)

    def vote(self, agent_id, proposal):
        vote_message = ConsensusBuildingMessage(agent_id, proposal, "vote")
        self.add_message(vote_message)

    def check_agreement(self):
        consensus_threshold = 2  # For simplicity, consensus is reached if at least two votes match
        for proposal, count in self.votes.items():
            if count >= consensus_threshold:
                return True, proposal
        return False, ""
```

### Step 3: Running the Consensus-Building Process

Finally, you can simulate agents engaging in the conversation, proposing ideas, commenting, and eventually voting on proposals.

```python
# Initialize the conversation process
conversation = ConsensusBuildingConversation()
task = "Enhancing the efficiency of urban transportation systems."
conversation.initiate_consensus(task)

# Simulate agents contributing to the conversation
conversation.add_proposal("Agent1", "Proposal 1: Implement a dynamic routing system for public transportation.")
conversation.add_comment("Agent2", "Comment: Support Proposal 1 with smart traffic management.")
conversation.add_proposal("Agent3", "Proposal 2: Increase investment in bike-sharing infrastructure.")

# Voting on the proposals
conversation.vote("Agent1", "Proposal 1")
conversation.vote("Agent2", "Proposal 1")
conversation.vote("Agent3", "Proposal 2")

# Check and declare consensus
consensus_reached, consensus_proposal = conversation.check_agreement()
if consensus_reached:
    print(f"Consensus Reached on: {consensus_proposal}")
else:
    print("No Consensus Reached.")
```

This code simulates the process where three agents discuss a task, propose strategies, comment on proposals, and vote to decide on the best approach. A consensus is reported if at least two agents agree on a specific proposal.

This illustrative example focuses on the mechanics of the conversation and consensus process among agents using pre-defined roles and behaviors. In a real-world application, the agents’ contributions would be dynamically generated responses from the GPT-4 AI model based on the prompt provided, accounting for more complex interactions and decision-making processes.

?  show an example implementation with a ConsensusBuildingConversation, 3 swarm agents with openaimodels that use gpt-4-0125-preview, and a prompttemplate that is used to start their consensus. the prompttemplate should trigger the first agent to make a proposal to solve a task. show the complete conversation flow from first proposal to voting to reaching consensus.
To illustrate a complete flow from proposal generation to consensus within a simulated environment using 3 swarm agents, each equipped with an OpenAI GPT-4 model, and a PromptTemplate to kick-start their conversation, we'll set up a structured example. This example will encompass initiating discussions, generating proposals based on the first prompt, allowing agents to respond, and finally voting to reach consensus on how to proceed. 

Let's begin:

### 1. Defining the Base Setup

First, we define our setup, assuming the `OpenAIToolModel`, `PromptTemplate`, `ConsensusBuildingConversation`, and `ConsensusBuildingMessage` are implemented as previously described.

### 2. Initializing the Environment

```python
api_key = "your_openai_api_key"

# Defining three agents with their respective OpenAI models focused on a "gpt-4-0125-preview" and its variants
agent1 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview"))
agent2 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant1"))
agent3 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant2"))

# The task to be solved, initiating the conversation
task_description = "Devise an innovative strategy to improve global literacy rates."
prompt_template = PromptTemplate(template="Initial approach to address: {task}?", variables={"task": task_description})

# Creating the conversation object
conversation = ConsensusBuildingConversation(topic="Global Literacy Strategy", participants=["agent1", "agent2", "agent3"])
```

### 3. Conducting the Conversation

Agent 1 kicks off the conversation:

```python
initiating_prompt = prompt_template()
print(f"Agent 1 Initiating: {initiating_prompt}")

# Agent 1 makes the first proposal based on received prompt
first_proposal = agent1.contribute_to_conversation(initiating_prompt)
conversation.initiate_consensus(initiating_prompt)
conversation.add_proposal("agent1", first_proposal)

# Assume Agent 2 and 3 generate their responses based on the initial proposal
response_agent2 = agent2.contribute_to_conversation("Commenting on the first proposal: " + first_proposal)
conversation.add_comment("agent2", response_agent2)

response_agent3 = agent3.contribute_to_conversation("Suggest an alternative strategy to " + first_proposal)
conversation.add_proposal("agent3", response_agent3)
```

### 4. Voting Phase and Checking for Consensus

After discussion, it's time to vote on the proposed strategies. For simplicity, let's simulate the voting:

```python
# Voting - let's say Agent 2 supports Agent 1's initial proposal, and Agent 3 remains with its own.
conversation.vote("agent2", "Proposal from agent1")
conversation.vote("agent3", "Proposal from agent3")

# Agent 1 votes for its own proposal to push the example towards consensus
conversation.vote("agent1", "Proposal from agent1")
```

### 5. Reaching Consensus

We check whether the consensus has been reached following the votes.

```python
is_agreement, agreement_message = conversation.check_agreement()

if is_agreement:
    print(f"Consensus Reached: {agreement_message}")
else:
    print("The agents could not reach a consensus.")
```

### Notes:

- The actual text for proposals and comments generated will be based on GPT-4 responses to prompts crafted from the conversation context, which can include the initial task and responses from other agents.
- To fully implement this scenario, you'd need access to the OpenAI API with the specified GPT-4 model versions or adjust the model identifiers according to available versions.
- Voting logic in this example is simplified for clarity. In practice, each agent's decision-making process to vote could also be informed by additional GPT-4 generated insights or predefined logic.

This example outlines how swarm intelligence could function in a collaborative task-solving context, demonstrating the concept of consensus-building in multi-agent systems using AI-driven decision-making.

?  we need a mechanism for talking to the agent's exec function so that we can get the agent's vote. additionally we need a function so that we can parse the agent's vote and determine which proposal the agent is voting for
To facilitate the agents' ability to vote and parse these votes effectively, we will enhance our agent setup with a mechanism to communicate votes and a function to parse these votes to understand which proposal an agent is voting for. This involves two key enhancements:

1. **Adding Voting Capability to the Agent's `exec` Function**: The `exec` function will be extended to process input for making a proposal, commenting, or voting. Based on the context or the content of the input, the agent will decide whether to propose a new solution, comment on existing proposals, or vote for the best proposal.

2. **Vote Parsing Function**: A function to parse the agent's response to extract the vote. This function will analyze the agent's text response to determine which proposal the agent supports.

Here's how these enhancements can be implemented:

### Updating the Swarm Agent

The `SwarmAgent` class is extended to include a decision-making capability for voting. This example does not directly integrate OpenAI's GPT-4 because of the complexity and access requirements. However, it demonstrates how you might structure these capabilities.

```python
class SwarmAgent:
    def __init__(self, model, agent_id):
        self.model = model
        self.agent_id = agent_id

    def exec(self, context):
        """
        Process the given context and decide on making a proposal, comment, or casting a vote.
        """
        # Example: Decide based on context (This should be replaced with actual model invocation)
        if "proposal" in context:
            response = self.model.predict(context)
            return response
        elif "vote" in context:
            # Simulate decision making for voting
            vote = self.decide_vote(context)
            return vote
        else:
            return "I need more information."

    def decide_vote(self, context):
        """
        Simulate an analysis to decide on voting - in practice, this could involve analyzing proposals with the model.
        """
        # Dummy logic for demonstration - replace with genuine analysis based on model prediction or explicit logic
        if "Proposal from agent1" in context:
            return "Proposal from agent1"
        else:
            return "Undecided"

    def contribute_to_conversation(self, prompt):
        proposal = self.exec(prompt)
        return proposal
```

### Implementing Vote Parsing

A function is created to parse the explicit vote from an agent's response. This function identifies which proposal the agent supports based on its text response.

```python
def parse_agent_vote(agent_response):
    """
    Parses the agent's text response to extract the vote.

    Parameters:
    agent_response (str): The agent's response text from which to extract the vote.

    Returns:
    str: The extracted vote indicating the supported proposal.
    """
    # Example parsing logic
    if "Proposal from agent1" in agent_response:
        return "Proposal from agent1"
    elif "Proposal from agent2" in agent_response:
        return "Proposal from agent2"
    elif "Proposal from agent3" in agent_response:
        return "Proposal from agent3"
    return "Undecided"
```

### Example Usage

Assuming the conversation and proposals have been initiated and it’s time to vote:

```python
# Assuming the context for voting includes all proposals
voting_context = "Please vote on the proposals: Proposal from agent1, Proposal from agent2, Proposal from agent3"

# Each agent votes
for agent in [agent1, agent2, agent3]:
    agent_vote = agent.exec(voting_context)
    parsed_vote = parse_agent_vote(agent_vote)
    # Add the parsed vote to the conversation
    conversation.vote(agent.agent_id, parsed_vote)

# Check for consensus
is_agreement, agreement_message = conversation.check_agreement()
print(f"Consensus Reached: {is_agreement}, with agreement on: {agreement_message}" if is_agreement else "No consensus reached.")
```

This structure and mechanisms allow agents to make informed decisions based on the context provided, such as proposals made by other agents, and provide a manageable way to parse these decisions to understand voting preferences better. In a real-world scenario, the decision-making process (`decide_vote`) and vote parsing should be enhanced to intelligently analyze the conversation context and proposals to determine the agent's stance accurately.

```

```swarmauri/experimental/conversations/SharedConversation.py

import inspect
from threading import Lock
from typing import Optional, Dict, List, Tuple
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class SharedConversation(ConversationBase):
    """
    A thread-safe conversation class that supports individual system contexts for each SwarmAgent.
    """
    def __init__(self):
        super().__init__()
        self._lock = Lock()  # A lock to ensure thread safety
        self._agent_system_contexts: Dict[str, SystemMessage] = {}  # Store system contexts for each agent
        self._history: List[Tuple[str, IMessage]] = []  # Stores tuples of (sender_id, IMessage)


    @property
    def history(self):
        history = []
        for each in self._history:
            history.append((each[0], each[1]))
        return history

    def add_message(self, message: IMessage, sender_id: str):
        with self._lock:
            self._history.append((sender_id, message))

    def reset_messages(self) -> None:
        self._history = []
        

    def _get_caller_name(self) -> Optional[str]:
        for frame_info in inspect.stack():
            # Check each frame for an instance with a 'name' attribute in its local variables
            local_variables = frame_info.frame.f_locals
            for var_name, var_value in local_variables.items():
                if hasattr(var_value, 'name'):
                    # Found an instance with a 'name' attribute. Return its value.
                    return getattr(var_value, 'name')
        # No suitable caller found
        return None

    def as_dict(self) -> List[Dict]:
        caller_name = self._get_caller_name()
        history = []

        with self._lock:
            # If Caller is not one of the agents, then give history
            if caller_name not in self._agent_system_contexts.keys():
                for sender_id, message in self._history:
                    history.append((sender_id, message.as_dict()))
                
                
            else:
                system_context = self.get_system_context(caller_name)
                #print(caller_name, system_context, type(system_context))
                if type(system_context) == str:
                    history.append(SystemMessage(system_context).as_dict())
                else:
                    history.append(system_context.as_dict())
                    
                for sender_id, message in self._history:
                    #print(caller_name, sender_id, message, type(message))
                    if sender_id == caller_name:
                        if message.__class__.__name__ == 'AgentMessage' or 'FunctionMessage':
                            # The caller is the sender; treat as AgentMessage
                            history.append(message.as_dict())
                            
                            # Print to see content that is empty.
                            #if not message.content:
                                #print('\n\t\t\t=>', message, message.content)
                    else:
                        if message.content:
                            # The caller is not the sender; treat as HumanMessage
                            history.append(HumanMessage(message.content).as_dict())
        return history
    
    def get_last(self) -> IMessage:
        with self._lock:
            return super().get_last()


    def clear_history(self):
        with self._lock:
            super().clear_history()


        

    def set_system_context(self, agent_id: str, context: SystemMessage):
        """
        Sets the system context for a specific agent.

        Args:
            agent_id (str): Unique identifier for the agent.
            context (SystemMessage): The context message to be set for the agent.
        """
        with self._lock:
            self._agent_system_contexts[agent_id] = context

    def get_system_context(self, agent_id: str) -> Optional[SystemMessage]:
        """
        Retrieves the system context for a specific agent.

        Args:
            agent_id (str): Unique identifier for the agent.

        Returns:
            Optional[SystemMessage]: The context message of the agent, or None if not found.
        """
        return self._agent_system_contexts.get(agent_id, None)

```

```swarmauri/experimental/models/__init__.py



```

```swarmauri/experimental/models/SageMaker.py

import json
import boto3
from ...core.models.IModel import IModel


class AWSSageMakerModel(IModel):
    def __init__(self, access_key: str, secret_access_key: str, region_name: str, model_name: str):
        """
        Initialize the AWS SageMaker model with AWS credentials, region, and the model name.

        Parameters:
        - access_key (str): AWS access key ID.
        - secret_access_key (str): AWS secret access key.
        - region_name (str): The region where the SageMaker model is deployed.
        - model_name (str): The name of the SageMaker model.
        """
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.client = boto3.client('sagemaker-runtime',
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_access_key,
                                   region_name=region_name)
        super().__init__(model_name)

    def predict(self, payload: str, content_type: str='application/json') -> dict:
        """
        Generate predictions using the AWS SageMaker model.

        Parameters:
        - payload (str): Input data in JSON format.
        - content_type (str): The MIME type of the input data (default: 'application/json').
        
        Returns:
        - dict: The predictions returned by the model.
        """
        endpoint_name = self.model_name  # Assuming the model name is also the endpoint name
        response = self.client.invoke_endpoint(EndpointName=endpoint_name,
                                               Body=payload,
                                               ContentType=content_type)
        result = json.loads(response['Body'].read().decode())
        return result

```

```swarmauri/experimental/models/HierarchicalAttentionModel.py

import tensorflow as tf
from swarmauri.core.models.IModel import IModel
from typing import Any

class HierarchicalAttentionModel(IModel):
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None  # This will hold the TensorFlow model with attention

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str) -> None:
        self._model_name = value

    def load_model(self) -> None:
        """
        Here, we define and compile the TensorFlow model described earlier.
        """
        # The following code is adapted from the attention model example provided earlier
        vocab_size = 10000  # Size of the vocabulary
        embedding_dim = 256  # Dimension of the embedding layer
        sentence_length = 100  # Max length of a sentence
        num_sentences = 10  # Number of sentences in a document
        units = 128  # Dimensionality of the output space of GRU
        
        # Word-level attention layer
        word_input = tf.keras.layers.Input(shape=(sentence_length,), dtype='int32')
        embedded_word = tf.keras.layers.Embedding(vocab_size, embedding_dim)(word_input)
        word_gru = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(units, return_sequences=True))(embedded_word)
        word_attention_layer = tf.keras.layers.Attention(use_scale=True, return_attention_scores=True)
        word_attention_output, word_attention_weights = word_attention_layer([word_gru, word_gru], return_attention_scores=True)
        word_encoder_with_attention = tf.keras.Model(inputs=word_input, outputs=[word_attention_output, word_attention_weights])
        
        # Sentence-level attention layer
        sentence_input = tf.keras.layers.Input(shape=(num_sentences, sentence_length), dtype='int32')
        sentence_encoder_with_attention = tf.keras.layers.TimeDistributed(word_encoder_with_attention)(sentence_input)
        sentence_gru = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(units, return_sequences=True))(sentence_encoder_with_attention[0])
        sentence_attention_layer = tf.keras.layers.Attention(use_scale=True, return_attention_scores=True)
        sentence_attention_output, sentence_attention_weights = sentence_attention_layer([sentence_gru, sentence_gru], return_attention_scores=True)
        doc_representation = tf.keras.layers.Dense(units, activation='tanh')(sentence_attention_output)
        
        # Classifier
        classifier = tf.keras.layers.Dense(1, activation='sigmoid')(doc_representation)
        
        # The model
        self._model = tf.keras.Model(inputs=sentence_input, outputs=[classifier, sentence_attention_weights])
        self._model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def predict(self, input_data: Any) -> Any:
        """
        Predict method to use the loaded model for making predictions.

        This example assumes `input_data` is preprocessed appropriately for the model's expected input.
        """
        if self._model is None:
            raise ValueError("Model is not loaded. Call `load_model` before prediction.")
            
        # Predicting with the model
        predictions, attention_weights = self._model.predict(input_data)
        
        # Additional logic to handle and package the predictions and attention weights could be added here
        
        return predictions, attention_weights

```

```swarmauri/experimental/utils/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/utils/get_last_frame.py

import inspect

def child_function(arg):
    # Get the stack frame of the caller
    caller_frame = inspect.currentframe().f_back
    # Get the name of the caller function
    caller_name = caller_frame.f_code.co_name
    # Inspect the arguments of the caller function
    args, _, _, values = inspect.getargvalues(caller_frame)
    # Assuming the caller has only one argument for simplicity
    arg_name = args[0]
    arg_value = values[arg_name]
    print(f"Caller Name: {caller_name}, Argument Name: {arg_name}, Argument Value: {arg_value}")

def caller_function(l):
    child_function(l)

# Example usage
caller_function("Hello")



```

```swarmauri/experimental/utils/save_schema.py

import inspect
import random

class Storage:
    def __init__(self):
        self.logs = []

    def log(self, log_data):
        self.logs.append(log_data)

    def print_logs(self):
        for log in self.logs:
            print(log)

class Loggable:
    def __init__(self, name, storage):
        self.name = name
        self.storage = storage

    def log_call(self, *args, **kwargs):
        # Inspect the call stack to get the caller's details
        caller_frame = inspect.stack()[2]
        caller_name = inspect.currentframe().f_back.f_code.co_name
        #caller_name = caller_frame.function
        module = inspect.getmodule(caller_frame[0])
        module_name = module.__name__ if module else 'N/A'

        # Log all relevant details
        log_data = {
            'caller_name': caller_name,
            'module_name': module_name,
            'called_name': self.name,
            'called_function': caller_frame[3], # The function in which log_call was invoked
            'args': args,
            'kwargs': kwargs
        }
        self.storage.log(log_data)

class Caller(Loggable):
    def __init__(self, name, storage, others):
        super().__init__(name, storage)
        self.others = others

    def __call__(self, *args, **kwargs):
        if len(self.storage.logs)<10:
            self.log_call(*args, **kwargs)
            # Randomly call another without causing recursive calls
            if args:  # Ensures it's not the first call without actual target
                next_caller_name = random.choice([name for name in self.others if name != self.name])
                self.others[next_caller_name](self.name)

# Initialize storage and callers
storage = Storage()
others = {}

# Creating callers
alice = Caller('Alice', storage, others)
bob = Caller('Bob', storage, others)
charlie = Caller('Charlie', storage, others)
dan = Caller('Dan', storage, others)

others['Alice'] = alice
others['Bob'] = bob
others['Charlie'] = charlie
others['Dan'] = dan

# Simulate the calls
dan(1, taco=23)

# Print the logs
storage.print_logs()


```

```swarmauri/experimental/utils/ISerializable.md

Creating a system that allows for the serialization of object interactions, along with enabling replay and modification of replay schemas in Python, involves several key steps. This process includes capturing the execution state, serializing it, and then providing mechanisms for replay and modification. Here's how you could implement such a system:

### Step 1: Define Serializable Representations
For each class that participates in the interaction, define a method to serialize its state to a dictionary or a similar serializable format. Additionally, include a method to instantiate an object from this serialized state.

```python
class Serializable:
    def serialize(self):
        raise NotImplementedError("Serialization method not implemented")
    
    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError("Deserialization method not implemented")
```

Implement these methods in your classes. For example:

```python
class ToolAgent(Serializable):
    def serialize(self):
        # Simplified example, adapt according to actual attributes
        return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

    @classmethod
    def deserialize(cls, data):
        # This method should instantiate the object based on the serialized state.
        # Example assumes the presence of model_name in the serialized state.
        model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
        return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration
```

### Step 2: Capture Executions
Capture executions and interactions by logging or emitting events, including serialized object states and method invocations.

```python
import json

def capture_execution(obj, method_name, args, kwargs):
    # Serialize object state before execution
    pre_exec_state = obj.serialize()

    # Invoke the method
    result = getattr(obj, method_name)(*args, **kwargs)

    # Serialize object state after execution and return value
    post_exec_state = obj.serialize()
    return_value = json.dumps(result) if isinstance(result, dict) else str(result)

    return {
        "object": obj.__class__.__name__,
        "method": method_name,
        "pre_exec_state": pre_exec_state,
        "post_exec_state": post_exec_state,
        "args": args,
        "kwargs": kwargs,
        "return": return_value
    }
```

### Step 3: Serialize Execution Flow
Aggregate captured execution states and interactions into a serializable format (e.g., a list of dictionaries). You can write this data to a file or database.

```python
execution_flow = []
# Example: capturing execution of a single method call
execution_snapshot = capture_execution(agent, "exec", [user_input], {})
execution_flow.append(execution_snapshot)

with open('execution_flow.json', 'w') as f:
    json.dump(execution_flow, f)
```

### Step 4: Replay Functionality
Create functionality to read the serialized execution flow and replay it. This involves deserializing object states and invoking methods according to the captured flow.

```python
def replay_execution_flow(execution_flow):
    for action in execution_flow:
        obj = globals()[action["object"]].deserialize(action["pre_exec_state"])
        getattr(obj, action["method"])(*action["args"], **action["kwargs"])
        print(f"Replayed {action['object']}.{action['method']} with args {action['args']} and kwargs {action['kwargs']}")
```

### Step 5: Modification and Customization
To enable modification of the replay schema, you can provide an interface or utility that allows users to edit the `execution_flow.json` either manually or through a GUI. This might include changing method arguments, reordering actions, or swapping objects.

This example outlines a basic framework and would need to be expanded and adapted to match the specific requirements and complexities of your application, especially for more complex interactions and state management.

```

```swarmauri/experimental/utils/ISerializable.py


# class Serializable:
#     def serialize(self):
#         raise NotImplementedError("Serialization method not implemented")
    
#     @classmethod
#     def deserialize(cls, data):
#         raise NotImplementedError("Deserialization method not implemented")
        
        
# class ToolAgent(Serializable):
#     def serialize(self):
#         # Simplified example, adapt according to actual attributes
#         return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

#     @classmethod
#     def deserialize(cls, data):
#         # This method should instantiate the object based on the serialized state.
#         # Example assumes the presence of model_name in the serialized state.
#         model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
#         return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration

```

```swarmauri/experimental/utils/log_prompt_response.py

import sqlite3
from functools import wraps

def log_prompt_response(db_path):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extracting the 'message' parameter from args which is assumed to be the first argument
            message = args[0]  
            response = await func(*args, **kwargs)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS prompts_responses
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             prompt TEXT, 
                             response TEXT)''')
            
            # Insert a new record
            cursor.execute('''INSERT INTO prompts_responses (prompt, response) 
                            VALUES (?, ?)''', (message, response))
            conn.commit()
            conn.close()
            return response
        
        return wrapper
    return decorator

```

```swarmauri/experimental/docs/replay.md

Creating a system that allows for the serialization of object interactions, along with enabling replay and modification of replay schemas in Python, involves several key steps. This process includes capturing the execution state, serializing it, and then providing mechanisms for replay and modification. Here's how you could implement such a system:

### Step 1: Define Serializable Representations
For each class that participates in the interaction, define a method to serialize its state to a dictionary or a similar serializable format. Additionally, include a method to instantiate an object from this serialized state.

```python
class Serializable:
    def serialize(self):
        raise NotImplementedError("Serialization method not implemented")
    
    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError("Deserialization method not implemented")
```

Implement these methods in your classes. For example:

```python
class ToolAgent(Serializable):
    def serialize(self):
        # Simplified example, adapt according to actual attributes
        return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

    @classmethod
    def deserialize(cls, data):
        # This method should instantiate the object based on the serialized state.
        # Example assumes the presence of model_name in the serialized state.
        model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
        return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration
```

### Step 2: Capture Executions
Capture executions and interactions by logging or emitting events, including serialized object states and method invocations.

```python
import json

def capture_execution(obj, method_name, args, kwargs):
    # Serialize object state before execution
    pre_exec_state = obj.serialize()

    # Invoke the method
    result = getattr(obj, method_name)(*args, **kwargs)

    # Serialize object state after execution and return value
    post_exec_state = obj.serialize()
    return_value = json.dumps(result) if isinstance(result, dict) else str(result)

    return {
        "object": obj.__class__.__name__,
        "method": method_name,
        "pre_exec_state": pre_exec_state,
        "post_exec_state": post_exec_state,
        "args": args,
        "kwargs": kwargs,
        "return": return_value
    }
```

### Step 3: Serialize Execution Flow
Aggregate captured execution states and interactions into a serializable format (e.g., a list of dictionaries). You can write this data to a file or database.

```python
execution_flow = []
# Example: capturing execution of a single method call
execution_snapshot = capture_execution(agent, "exec", [user_input], {})
execution_flow.append(execution_snapshot)

with open('execution_flow.json', 'w') as f:
    json.dump(execution_flow, f)
```

### Step 4: Replay Functionality
Create functionality to read the serialized execution flow and replay it. This involves deserializing object states and invoking methods according to the captured flow.

```python
def replay_execution_flow(execution_flow):
    for action in execution_flow:
        obj = globals()[action["object"]].deserialize(action["pre_exec_state"])
        getattr(obj, action["method"])(*action["args"], **action["kwargs"])
        print(f"Replayed {action['object']}.{action['method']} with args {action['args']} and kwargs {action['kwargs']}")
```

### Step 5: Modification and Customization
To enable modification of the replay schema, you can provide an interface or utility that allows users to edit the `execution_flow.json` either manually or through a GUI. This might include changing method arguments, reordering actions, or swapping objects.

This example outlines a basic framework and would need to be expanded and adapted to match the specific requirements and complexities of your application, especially for more complex interactions and state management.

---

To capture everything, including object instantiation like `api_key`, `conversation`, `model`, `tools`, and method calls (`exec`) in a fully comprehensive manner, we need to adopt an approach that not only captures method invocations but also objects as they are created and manipulated. This comprehensive capture and replay mechanism would involve the following stages:

### Stage 1: Capture

1. **Object Creation**: Capture the creation of all relevant objects along with their initial states and construction parameters.
2. **Method Calls**: Capture method invocations, including input parameters and return values.
3. **State Changes**: Optionally capture state changes to objects over time.

To implement this, we can use either decorators or a base class pattern that all relevent classes inherit from, which automates capturing information about object creation, method calls, and state.

#### Decorator for Capturing Method Calls and Object Creation

```python
import json
import functools

capture_log = []

def capture(cls):
    class Wrapper:
        def __init__(self, *args, **kwargs):
            capture_log.append({
                "type": "creation",
                "class_name": cls.__name__,
                "init_args": args,
                "init_kwargs": kwargs
            })
            self._instance = cls(*args, **kwargs)
        
        def __getattr__(self, name):
            attr = getattr(self._instance, name)
            if callable(attr):
                @functools.wraps(attr)
                def wrapper(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    capture_log.append({
                        "type": "method_call",
                        "class_name": cls.__name__,
                        "method_name": name,
                        "method_args": args,
                        "method_kwargs": kwargs,
                        "return_value": result
                    })
                    return result
                return wrapper
            return attr
    return Wrapper

def save_capture_log(filepath="execution_log.json"):
    with open(filepath, "w") as f:
        json.dump(capture_log, f, indent=4)
```

#### Applying the Decorator

Apply the `@capture` decorator to classes you want to monitor.

```python
@capture
class ToolAgent:
    # Your implementation
    
@capture
class OpenAIToolModel:
    # Your implementation

@capture
class Toolkit:
    # Your implementation

# Note: You may use different or additional capturing mechanisms for objects that don't fit well with this approach.
```

### Stage 2: Replay

Replaying involves reading the `execution_log.json`, recreating objects according to the log, and then calling the logged methods with their original parameters.

#### Basic Replay Function

```python
def replay_from_log(filepath="execution_log.json"):
    with open(filepath, "r") as f:
        execution_log = json.load(f)

    for action in execution_log:
        if action["type"] == "creation":
            cls = globals()[action["class_name"]]
            obj = cls(*action["init_args"], **action["init_kwargs"])
            # Additional logic to store a reference to this object for future method calls
        elif action["type"] == "method_call":
            # Logic to invoke method on previously created object
```

This solution outlines a mechanism to capture and replay execution flow, focusing on simplicity and adaptability. Depending on your specific requirements (e.g., handling static methods, managing object relationships), you may need to extend or modify this logic. Additionally, consider security implications when dynamically instantiating classes and executing methods, especially with inputs from external sources.

```

```swarmauri/experimental/parsers/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/parsers/PDFToTextParser.py

import fitz  # PyMuPDF
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.ConcreteDocument import ConcreteDocument

class PDFtoTextParser(IParser):
    """
    A parser to extract text from PDF files.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses a PDF file and extracts its text content as Document instances.

        Parameters:
        - data (Union[str, Any]): The path to the PDF file.

        Returns:
        - List[IDocument]: A list with a single IDocument instance containing the extracted text.
        """
        # Ensure data is a valid str path to a PDF file
        if not isinstance(data, str):
            raise ValueError("PDFtoTextParser expects a file path in str format.")

        try:
            # Open the PDF file
            doc = fitz.open(data)
            text = ""

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            # Create a document with the extracted text
            document = ConcreteDocument(doc_id=str(hash(data)), content=text, metadata={"source": data})
            return [document]
        
        except Exception as e:
            print(f"An error occurred while parsing the PDF: {e}")
            return []


```

```swarmauri/experimental/vector_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/vector_stores/Word2VecDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from gensim.models import Word2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
import gensim.downloader as api

class Word2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        """
        Initializes the Word2VecDocumentStore.

        Parameters:
        - word2vec_model_path (Optional[str]): File path to a pre-trained Word2Vec model. 
                                               Leave None to use Gensim's pre-trained model.
        - pre_trained (bool): If True, loads a pre-trained Word2Vec model. If False, an uninitialized model is used that requires further training.
        """
        self.model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: EmbeddedDocument) -> None:
        # Check if the document already has an embedding, if not generate one using _average_word_vectors
        if not hasattr(document, 'embedding') or document.embedding is None:
            words = document.content.split()  # Simple tokenization, consider using a better tokenizer
            embedding = self._average_word_vectors(words)
            document.embedding = embedding
            print(document.embedding)
        self.documents.append(document)
        
    def add_documents(self, documents: List[EmbeddedDocument]) -> None:
        self.documents.extend(documents)
        
    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: EmbeddedDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

    def _average_word_vectors(self, words: List[str]) -> np.ndarray:
        """
        Generate document vector by averaging its word vectors.
        """
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        print(word_vectors)
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)

    def retrieve(self, query: str, top_k: int = 5) -> List[EmbeddedDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self._average_word_vectors(query.split())
        print('query_vector', query_vector)
        # Compute similarity scores between the query and each document's stored embedding
        similarities = self.metric.similarities(SimpleVector(query_vector), [SimpleVector(doc.embedding) for doc in self.documents if doc.embedding])
        print('similarities', similarities)
        # Retrieve indices of top_k most similar documents
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        print('top_k_indices', top_k_indices)
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/vector_stores/TriplesDocumentStore.py

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

```

```swarmauri/experimental/tracing/RemoteTrace.py

from __future__ import ITraceContext

import requests
import json
import uuid
from datetime import datetime

from swarmauri.core.tracing.ITracer import ITracer
from swarmauri.core.tracing.ITraceContext import ITraceContext

# Implementing the RemoteTraceContext class
class RemoteTraceContext(ITraceContext):
    def __init__(self, trace_id: str, name: str):
        self.trace_id = trace_id
        self.name = name
        self.start_time = datetime.now()
        self.attributes = {}
        self.annotations = {}

    def get_trace_id(self) -> str:
        return self.trace_id

    def add_attribute(self, key: str, value):
        self.attributes[key] = value
        
    def add_annotation(self, key: str, value):
        self.annotations[key] = value

# Implementing the RemoteAPITracer class
class RemoteAPITracer(ITracer):
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint

    def start_trace(self, name: str, initial_attributes=None) -> 'RemoteTraceContext':
        trace_id = str(uuid.uuid4())
        context = RemoteTraceContext(trace_id, name)
        if initial_attributes:
            for key, value in initial_attributes.items():
                context.add_attribute(key, value)
        return context

    def end_trace(self, trace_context: 'RemoteTraceContext'):
        trace_context.end_time = datetime.now()
        # Pretending to serialize the context information to JSON
        trace_data = {
            "trace_id": trace_context.get_trace_id(),
            "name": trace_context.name,
            "start_time": str(trace_context.start_time),
            "end_time": str(trace_context.end_time),
            "attributes": trace_context.attributes,
            "annotations": trace_context.annotations
        }
        json_data = json.dumps(trace_data)
        # POST the serialized data to the remote REST API
        response = requests.post(self.api_endpoint, json=json_data)
        if not response.ok:
            raise Exception(f"Failed to send trace data to {self.api_endpoint}. Status code: {response.status_code}")

    def annotate_trace(self, trace_context: 'RemoteTraceContext', key: str, value):
        trace_context.add_annotation(key, value)

```

```swarmauri/experimental/tracing/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/chains/TypeAgnosticCallableChain.py

from typing import Any, Callable, List, Dict, Optional, Tuple, Union

CallableDefinition = Tuple[Callable, List[Any], Dict[str, Any], Union[str, Callable, None]]

class TypeAgnosticCallableChain:
    def __init__(self, callables: Optional[List[CallableDefinition]] = None):
        self.callables = callables if callables is not None else []

    @staticmethod
    def _ignore_previous(_previous_result, *args, **kwargs):
        return args, kwargs

    @staticmethod
    def _use_first_arg(previous_result, *args, **kwargs):
        return [previous_result] + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_first(previous_result, *args, **kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result) + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_only(previous_result, *_args, **_kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result), {}

    @staticmethod
    def _add_previous_kwargs_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**kwargs, **previous_result}

    @staticmethod
    def _add_previous_kwargs_no_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**previous_result, **kwargs}

    @staticmethod
    def _use_all_args_all_kwargs_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {}
        combined_kwargs.update(kwargs)
        return combined_args, combined_kwargs

    @staticmethod
    def _use_all_args_all_kwargs_no_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = kwargs if isinstance(kwargs, dict) else {}
        combined_kwargs = {**combined_kwargs, **(previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {})}
        return combined_args, combined_kwargs

    def add_callable(self, func: Callable, args: List[Any] = None, kwargs: Dict[str, Any] = None, input_handler: Union[str, Callable, None] = None) -> None:
        if isinstance(input_handler, str):
            # Map the string to the corresponding static method
            input_handler_method = getattr(self, f"_{input_handler}", None)
            if input_handler_method is None:
                raise ValueError(f"Unknown input handler name: {input_handler}")
            input_handler = input_handler_method
        elif input_handler is None:
            input_handler = self._ignore_previous
        self.callables.append((func, args or [], kwargs or {}, input_handler))

    def __call__(self, *initial_args, **initial_kwargs) -> Any:
        result = None
        for func, args, kwargs, input_handler in self.callables:
            if isinstance(input_handler, str):
                # Map the string to the corresponding static method
                input_handler_method = getattr(self, f"_{input_handler}", None)
                if input_handler_method is None:
                    raise ValueError(f"Unknown input handler name: {input_handler}")
                input_handler = input_handler_method
            elif input_handler is None:
                input_handler = self._ignore_previous
                
            args, kwargs = input_handler(result, *args, **kwargs) if result is not None else (args, kwargs)
            result = func(*args, **kwargs)
        return result

    def __or__(self, other: "TypeAgnosticCallableChain") -> "TypeAgnosticCallableChain":
        if not isinstance(other, TypeAgnosticCallableChain):
            raise TypeError("Operand must be an instance of TypeAgnosticCallableChain")
        
        new_chain = TypeAgnosticCallableChain(self.callables + other.callables)
        return new_chain

```

```swarmauri/experimental/chains/__init__.py

#

```

```swarmauri/experimental/chains/IChainScheduler.py

from abc import ABC, abstractmethod
from swarmauri.core.chains.IChain import IChain

class IChainScheduler(ABC):
    @abstractmethod
    def schedule_chain(self, chain: IChain, schedule: str) -> None:
        """Schedule the execution of the given chain."""
        pass

```

```swarmauri/experimental/chains/IChainFormatter.py

from abc import ABC, abstractmethod
from typing import Any
from swarmauri.core.chains.IChainStep import IChainStep

class IChainFormatter(ABC):
    @abstractmethod
    def format_output(self, step: IChainStep, output: Any) -> str:
        """Format the output of a specific chain step."""
        pass

```

```swarmauri/experimental/chains/IChainNotification.py

from abc import ABC, abstractmethod

class IChainNotifier(ABC):
    @abstractmethod
    def send_notification(self, message: str) -> None:
        """Send a notification message based on chain execution results."""
        pass

```

```swarmauri/experimental/chains/IChainPersistence.py

from abc import ABC, abstractmethod
from typing import Dict, Any
from swarmauri.core.chains.IChain import IChain

class IChainPersistence(ABC):
    @abstractmethod
    def save_state(self, chain: IChain, state: Dict[str, Any]) -> None:
        """Save the state of the given chain."""
        pass

    @abstractmethod
    def load_state(self, chain_id: str) -> Dict[str, Any]:
        """Load the state of a chain by its identifier."""
        pass

```

```swarmauri/experimental/embeddings/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/embeddings/SpatialDocEmbedding.py

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



```

```swarmauri/experimental/document_stores/TriplesDocumentStore.py

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

```

```swarmauri/experimental/document_stores/Word2VecDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from gensim.models import Word2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
import gensim.downloader as api

class Word2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        """
        Initializes the Word2VecDocumentStore.

        Parameters:
        - word2vec_model_path (Optional[str]): File path to a pre-trained Word2Vec model. 
                                               Leave None to use Gensim's pre-trained model.
        - pre_trained (bool): If True, loads a pre-trained Word2Vec model. If False, an uninitialized model is used that requires further training.
        """
        self.model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: EmbeddedDocument) -> None:
        # Check if the document already has an embedding, if not generate one using _average_word_vectors
        if not hasattr(document, 'embedding') or document.embedding is None:
            words = document.content.split()  # Simple tokenization, consider using a better tokenizer
            embedding = self._average_word_vectors(words)
            document.embedding = embedding
            print(document.embedding)
        self.documents.append(document)
        
    def add_documents(self, documents: List[EmbeddedDocument]) -> None:
        self.documents.extend(documents)
        
    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: EmbeddedDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

    def _average_word_vectors(self, words: List[str]) -> np.ndarray:
        """
        Generate document vector by averaging its word vectors.
        """
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        print(word_vectors)
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)

    def retrieve(self, query: str, top_k: int = 5) -> List[EmbeddedDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self._average_word_vectors(query.split())
        print('query_vector', query_vector)
        # Compute similarity scores between the query and each document's stored embedding
        similarities = self.metric.similarities(SimpleVector(query_vector), [SimpleVector(doc.embedding) for doc in self.documents if doc.embedding])
        print('similarities', similarities)
        # Retrieve indices of top_k most similar documents
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        print('top_k_indices', top_k_indices)
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/document_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/distances/CanberraDistance.py

import numpy as np
from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class CanberraDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Canberra distance metric.
    This class now processes IVector instances instead of raw lists.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Canberra distance between two IVector instances.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Canberra distance between the vectors.
        """
        # Extract data from IVector
        data_a = np.array(vector_a.data)
        data_b = np.array(vector_b.data)

        # Checking dimensions match
        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        # Computing Canberra distance
        distance = np.sum(np.abs(data_a - data_b) / (np.abs(data_a) + np.abs(data_b)))
        # Handling the case where both vectors have a zero value for the same dimension
        distance = np.nan_to_num(distance)
        return distance
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute similarity using the Canberra distance. Since this distance metric isn't
        directly interpretable as a similarity, a transformation is applied to map the distance
        to a similarity score.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        # One way to derive a similarity from distance is through inversion or transformation.
        # Here we use an exponential decay based on the computed distance. This is a placeholder
        # that assumes closer vectors (smaller distance) are more similar.
        distance = self.distance(vector_a, vector_b)

        # Transform the distance into a similarity score
        similarity = np.exp(-distance)

        return similarity
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/ChebyshevDistance.py

from typing import List
from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity

class ChebyshevDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Chebyshev distance metric.
    Chebyshev distance is the maximum absolute distance between two vectors' elements.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Chebyshev distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Chebyshev distance between vector_a and vector_b.
        """
        max_distance = 0
        for a, b in zip(vector_a.data, vector_b.data):
            max_distance = max(max_distance, abs(a - b))
        return max_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the similarity between two vectors based on the Chebyshev distance.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: The similarity score between the two vectors.
        """

        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/HaversineDistance.py

from typing import List
from math import radians, cos, sin, sqrt, atan2
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class HaversineDistance(IDistanceSimilarity):
    """
    Concrete implementation of IDistanceSimiliarity interface using the Haversine formula.
    
    Haversine formula determines the great-circle distance between two points on a sphere given their 
    longitudes and latitudes. This implementation is particularly useful for geo-spatial data.
    """ 

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Haversine distance between two geo-spatial points.

        Args:
            vector_a (IVector): The first point in the format [latitude, longitude].
            vector_b (IVector): The second point in the same format [latitude, longitude].

        Returns:
            float: The Haversine distance between vector_a and vector_b in kilometers.
        """
        # Earth radius in kilometers
        R = 6371.0

        lat1, lon1 = map(radians, vector_a.data)
        lat2, lon2 = map(radians, vector_b.data)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")

```

```swarmauri/experimental/distances/ManhattanDistance.py

from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class ManhattanDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Manhattan distance.
    
    The Manhattan distance between two points is the sum of the absolute differences of their Cartesian coordinates.
    This is also known as L1 distance.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Manhattan distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The Manhattan distance between vector_a and vector_b.
        """
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must have the same dimensionality.")
        
        return sum(abs(a - b) for a, b in zip(vector_a.data, vector_b.data))

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        The similarity based on Manhattan distance can be inversely related to the distance for some applications,
        but this method intentionally returns NotImplementedError to signal that Manhattan distance is typically
        not directly converted to similarity in the conventional sense used in this context.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            NotImplementedError: This is intended as this distance metric doesn't directly offer a similarity measure.
        """
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity measure.")
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity measure.")

```

```swarmauri/experimental/distances/MinkowskiDistance.py

from typing import List
from scipy.spatial.distance import minkowski
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class MinkowskiDistance(IDistanceSimilarity):
    """
    Implementation of the IDistanceSimiliarity interface using the Minkowski distance metric.
    Minkowski distance is a generalized metric form that includes Euclidean distance,
    Manhattan distance, and others depending on the order (p) parameter.

    The class provides methods to compute the Minkowski distance between two vectors.
    """

    def __init__(self, p: int = 2):
        """
        Initializes the MinkowskiDistance calculator with the specified order.

        Parameters:
        - p (int): The order of the Minkowski distance. p=2 corresponds to the Euclidean distance,
                   while p=1 corresponds to the Manhattan distance. Default is 2.
        """
        self.p = p

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Minkowski distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Minkowski distance between vector_a and vector_b.
        """
        # Check if both vectors have the same dimensionality
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must have the same dimensionality.")

        # Extract data from IVector instances
        data_a = vector_a.data
        data_b = vector_b.data

        # Calculate and return the Minkowski distance
        return minkowski(data_a, data_b, p=self.p)

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors based on the Minkowski distance.
        The similarity is inversely related to the distance.

        Args:
            vector_a (IVector): The first vector to compare for similarity.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        dist = self.distance(vector_a, vector_b)
        return 1 / (1 + dist)  # An example similarity score
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/ScannVectorStore.py

import numpy as np
import scann
from typing import List, Dict, Union

from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.core.vector_stores.ISimiliarityQuery import ISimilarityQuery
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector


class ScannVectorStore(IVectorStore, ISimilarityQuery):
    """
    A vector store that utilizes ScaNN (Scalable Nearest Neighbors) for efficient similarity searches.
    """

    def __init__(self, dimension: int, num_leaves: int = 100, num_leaves_to_search: int = 10, reordering_num_neighbors: int = 100):
        """
        Initialize the ScaNN vector store with given parameters.

        Parameters:
        - dimension (int): The dimensionality of the vectors being stored.
        - num_leaves (int): The number of leaves for the ScaNN partitioning tree.
        - num_leaves_to_search (int): The number of leaves to search for query time. Must be <= num_leaves.
        - reordering_num_neighbors (int): The number of neighbors to re-rank based on the exact distance after searching leaves.
        """
        self.dimension = dimension
        self.num_leaves = num_leaves
        self.num_leaves_to_search = num_leaves_to_search
        self.reordering_num_neighbors = reordering_num_neighbors

        self.searcher = None  # Placeholder for the ScaNN searcher initialized during building
        self.dataset_vectors = []
        self.id_to_metadata = {}

    def _build_scann_searcher(self):
        """Build the ScaNN searcher based on current dataset vectors."""
        self.searcher = scann.ScannBuilder(np.array(self.dataset_vectors, dtype=np.float32), num_neighbors=self.reordering_num_neighbors, distance_measure="dot_product").tree(
            num_leaves=self.num_leaves, num_leaves_to_search=self.num_leaves_to_search, training_sample_size=25000
        ).score_ah(
            dimensions_per_block=2
        ).reorder(self.reordering_num_neighbors).build()

    def add_vector(self, vector_id: str, vector: Union[np.ndarray, List[float]], metadata: Dict = None) -> None:
        """
        Adds a vector along with its identifier and optional metadata to the store.

        Args:
            vector_id (str): Unique identifier for the vector.
            vector (Union[np.ndarray, List[float]]): The high-dimensional vector to be stored.
            metadata (Dict, optional): Optional metadata related to the vector.
        """
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector, dtype=np.float32)
        
        if self.searcher is None:
            self.dataset_vectors.append(vector)
        else:
            raise Exception("Cannot add vectors after building the index. Rebuild the index to include new vectors.")

        if metadata is None:
            metadata = {}
        self.id_to_metadata[vector_id] = metadata

    def build_index(self):
        """Builds or rebuilds the ScaNN searcher to reflect the current dataset vectors."""
        self._build_scann_searcher()

    def get_vector(self, vector_id: str) -> Union[IVector, None]:
        """
        Retrieve a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector.

        Returns:
            Union[IVector, None]: The vector associated with the given id, or None if not found.
        """
        if vector_id in self.id_to_metadata:
            metadata = self.id_to_metadata[vector_id]
            return SimpleVector(data=metadata.get('vector'), metadata=metadata)
        return None

    def delete_vector(self, vector_id: str) -> None:
        """
        Deletes a vector from the ScannVectorStore and marks the index for rebuilding.
        Note: For simplicity, this function assumes vectors are uniquely identifiable by their metadata.

        Args:
            vector_id (str): The unique identifier for the vector to be deleted.
        """
        if vector_id in self.id_to_metadata:
            # Identify index of the vector to be deleted
            vector = self.id_to_metadata[vector_id]['vector']
            index = self.dataset_vectors.index(vector)

            # Remove vector and its metadata
            del self.dataset_vectors[index]
            del self.id_to_metadata[vector_id]

            # Since vector order is important for matching ids, rebuild the searcher to reflect deletion
            self.searcher = None
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")

    def update_vector(self, vector_id: str, new_vector: Union[np.ndarray, List[float]], new_metadata: Dict = None) -> None:
        """
        Updates an existing vector in the ScannVectorStore and marks the index for rebuilding.

        Args:
            vector_id (str): The unique identifier for the vector to be updated.
            new_vector (Union[np.ndarray, List[float]]): The updated vector.
            new_metadata (Dict, optional): Optional updated metadata for the vector.
        """
        # Ensure new_vector is numpy array for consistency
        if not isinstance(new_vector, np.ndarray):
            new_vector = np.array(new_vector, dtype=np.float32)

        if vector_id in self.id_to_metadata:
            # Update operation follows delete then add strategy because vector order matters in ScaNN
            self.delete_vector(vector_id)
            self.add_vector(vector_id, new_vector, new_metadata)
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")



    def search_by_similarity_threshold(self, query_vector: Union[np.ndarray, List[float]], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Args:
            query_vector (Union[np.ndarray, List[float]]): The high-dimensional query vector.
            similarity_threshold (float): The similarity threshold for filtering results.
            space_name (str, optional): The name of the vector space to search within. Not used in this implementation.

        Returns:
            List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector, dtype=np.float32)
        
        if self.searcher is None:
            self._build_scann_searcher()
        
        _, indices = self.searcher.search(query_vector, final_num_neighbors=self.reordering_num_neighbors)
        results = [{"id": str(idx), "metadata": self.id_to_metadata.get(str(idx), {})} for idx in indices if idx < similarity_threshold]
        return results

```

```swarmauri/experimental/distances/SorensenDiceDistance.py

import numpy as np
from typing import List
from collections import Counter

from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SorensenDiceDistance(IDistanceSimilarity):
    """
    Implementing a concrete Vector Store class for calculating Sörensen-Dice Index Distance.
    The Sörensen-Dice Index, or Dice's coefficient, is a measure of the similarity between two sets.
    """

    def distance(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Compute the Sörensen-Dice distance between two vectors.
        
        Args:
            vector_a (List[float]): The first vector in the comparison.
            vector_b (List[float]): The second vector in the comparison.
        
        Returns:
            float: The computed Sörensen-Dice distance between vector_a and vector_b.
        """
        # Convert vectors to binary sets
        set_a = set([i for i, val in enumerate(vector_a) if val])
        set_b = set([i for i, val in enumerate(vector_b) if val])
        
        # Calculate the intersection size
        intersection_size = len(set_a.intersection(set_b))
        
        # Sorensen-Dice Index calculation
        try:
            sorensen_dice_index = (2 * intersection_size) / (len(set_a) + len(set_b))
        except ZeroDivisionError:
            sorensen_dice_index = 0.0
        
        # Distance is inverse of similarity for Sörensen-Dice
        distance = 1 - sorensen_dice_index
        
        return distance
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarity(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")

```

```swarmauri/experimental/distances/SquaredEuclideanDistance.py

from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SquaredEuclideanDistance(IDistanceSimilarity):
    """
    A concrete class for computing the squared Euclidean distance between two vectors.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the squared Euclidean distance between vectors `vector_a` and `vector_b`.

        Parameters:
        - vector_a (IVector): The first vector in the comparison.
        - vector_b (IVector): The second vector in the comparison.

        Returns:
        - float: The computed squared Euclidean distance between vector_a and vector_b.
        """
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must be of the same dimensionality.")

        squared_distance = sum((a - b) ** 2 for a, b in zip(vector_a.data, vector_b.data))
        return squared_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Squared Euclidean distance is not used for calculating similarity.
        
        Parameters:
        - vector_a (IVector): The first vector.
        - vector_b (IVector): The second vector.

        Raises:
        - NotImplementedError: Indicates that similarity calculation is not implemented.
        """
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")
        
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")

```

```swarmauri/experimental/distances/SSASimilarity.py

from typing import Set, List, Dict
from ....core.vector_stores.ISimilarity import ISimilarity
from ....core.vectors.IVector import IVector


class SSASimilarity(ISimilarity):
    """
    Implements the State Similarity in Arity (SSA) similarity measure to
    compare states (sets of variables) for their similarity.
    """

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Calculate the SSA similarity between two documents by comparing their metadata,
        assumed to represent states as sets of variables.

        Args:
        - vector_a (IDocument): The first document.
        - vector_b (IDocument): The second document to compare with the first document.

        Returns:
        - float: The SSA similarity measure between vector_a and vector_b, ranging from 0 to 1
                 where 0 represents no similarity and 1 represents identical states.
        """
        state_a = set(vector_a.metadata.keys())
        state_b = set(vector_b.metadata.keys())

        return self.calculate_ssa(state_a, state_b)

    @staticmethod
    def calculate_ssa(state_a: Set[str], state_b: Set[str]) -> float:
        """
        Calculate the State Similarity in Arity (SSA) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.

        Returns:6
        - float: The SSA similarity measure, ranging from 0 (no similarity) to 1 (identical states).
        """
        # Calculate the intersection (shared variables) between the two states
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the union (total unique variables) of the two states
        total_variables = state_a.union(state_b)
        
        # Calculate the SSA measure as the ratio of shared to total variables
        ssa = len(shared_variables) / len(total_variables) if total_variables else 1
        
        return ssa

```

```swarmauri/experimental/distances/SSIVSimilarity.py

from typing import List, Dict, Set
from ....core.vector_stores.ISimilarity import ISimilarity

class SSIVSimilarity(ISimilarity):
    """
    Concrete class that implements ISimilarity interface using
    State Similarity of Important Variables (SSIV) as the similarity measure.
    """

    def similarity(self, state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the SSIV between two states represented by sets of variables.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        """
        return self.calculate_ssiv(state_a, state_b, importance_a, importance_b)

    @staticmethod
    def calculate_ssiv(state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the State Similarity of Important Variables (SSIV) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        
        Note: It is assumed that the importance weights are non-negative.
        """
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the summed importance of shared variables
        shared_importance_sum = sum(importance_a[var] for var in shared_variables) + sum(importance_b[var] for var in shared_variables)
        
        # Calculate the total importance of all variables in both states
        total_importance_sum = sum(importance_a.values()) + sum(importance_b.values())
        
        # Calculate and return the SSIV
        ssiv = (2 * shared_importance_sum) / total_importance_sum if total_importance_sum != 0 else 0
        return ssiv


```

```swarmauri/experimental/distances/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/apis/README.md

Endpoints
- Openwebui
- Gradio
- Streamlit
- Fastapi apis
- Fastapi jinja2
- Celery
- Flowise

```

```swarmauri/experimental/apis/CeleryAgentCommands.py

from celery import Celery
from swarmauri.core.agent_apis.IAgentCommands import IAgentCommands
from typing import Callable, Any, Dict

class CeleryAgentCommands(IAgentCommands):
    def __init__(self, broker_url: str, backend_url: str):
        """
        Initializes the Celery application with the specified broker and backend URLs.
        """
        self.app = Celery('swarmauri_agent_tasks', broker=broker_url, backend=backend_url)

    def register_command(self, command_name: str, function: Callable[..., Any], *args, **kwargs) -> None:
        """
        Registers a new command as a Celery task.
        """
        self.app.task(name=command_name, bind=True)(function)

    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """
        Executes a registered command by name asynchronously.
        """
        result = self.app.send_task(command_name, args=args, kwargs=kwargs)
        return result.get()

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        Fetches the status of a command execution via its task ID.
        """
        async_result = self.app.AsyncResult(task_id)
        return {"status": async_result.status, "result": async_result.result if async_result.ready() else None}

    def revoke_command(self, task_id: str) -> None:
        """
        Revokes or terminates a command execution by its task ID.
        """
        self.app.control.revoke(task_id, terminate=True)

```

```swarmauri/experimental/vectors/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/README.md

# Standard Library

The Standard Library extends the Core Library with concrete implementations of models, agents, tools, parsers, and more. It aims to provide ready-to-use components that can be easily integrated into machine learning projects.

## Features

- **Predefined Models and Agents**: Implements standard models and agents ready for use.
- **Toolkit**: A collection of tools for various tasks (e.g., weather information, math operations).
- **Parsers Implementations**: Various parsers for text data, including HTML and CSV parsers.
- **Conversations and Chunkers**: Manage conversation histories and chunk text data.
- **Vectorizers**: Transform text data into vector representations.
- **Document Stores and Vector Stores**: Concrete implementations for storing and retrieving data.

## Getting Started

To make the best use of the Standard Library, first ensure that the Core Library is set up in your project as the Standard Library builds upon it.

```python
# Example usage of a concrete model from the Standard Library
from swarmauri.standard.models.concrete import OpenAIModel

# Initialize the model with necessary configuration
model = OpenAIModel(api_key="your_api_key_here")
```

## Documentation

For more detailed guides and API documentation, check the [Docs](/docs) directory within the library. You'll find examples, configuration options, and best practices for utilizing the provided components.

## Contributing

Your contributions can help the Standard Library grow! Whether it's adding new tools, improving models, or writing documentation, we appreciate your help. Please send a pull request with your contributions.

## License

Please see the `LICENSE` file in the repository for details.

```

```swarmauri/standard/__init__.py



```

```swarmauri/standard/llms/__init__.py



```

```swarmauri/standard/llms/base/__init__.py



```

```swarmauri/standard/llms/base/LLMBase.py

from abc import ABC, abstractmethod
from typing import Any, Union, Optional, List, Literal
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.llms.IPredict import IPredict

class LLMBase(IPredict, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] =  Field(default=ResourceTypes.LLM.value, frozen=True)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['LLMBase'] = 'LLMBase'

    @model_validator(mode='after')
    @classmethod
    def _validate_name_in_allowed_models(cls, values):
        name = values.name
        allowed_models = values.allowed_models
        if name and name not in allowed_models:
            raise ValueError(f"Model name {name} is not allowed. Choose from {allowed_models}")
        return values
        
    def predict(self, *args, **kwargs):
        raise NotImplementedError('Predict not implemented in subclass yet.')
        

```

```swarmauri/standard/llms/concrete/__init__.py



```

```swarmauri/standard/llms/concrete/OpenAIModel.py

import json
from typing import List, Dict, Literal
from openai import OpenAI
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class OpenAIModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gpt-4o', 
    'gpt-4o-2024-05-13',
    'gpt-4-turbo', 
    'gpt-4-turbo-2024-04-09',
    'gpt-4-turbo-preview',
    'gpt-4-0125-preview',
    'gpt-4-1106-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-4-32k',
    'gpt-4-32k-0613',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613',
    'gpt-3.5-turbo-16k-0613',
    'gpt-3.5-turbo-16k',
    'gpt-3.5-turbo']
    name: str = "gpt-3.5-turbo-16k"
    type: Literal['OpenAIModel'] = 'OpenAIModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256, 
        enable_json=False, 
        stop: List[str] = None):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        
        Returns:
        - The generated message content.
        """
        formatted_messages = self._format_messages(conversation.history)
        client = OpenAI(api_key=self.api_key)
        
        if enable_json:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        
        result = json.loads(response.model_dump_json())
        message_content = result['choices'][0]['message']['content']
        conversation.add_message(AgentMessage(content=message_content))
        
        return conversation

```

```swarmauri/standard/llms/concrete/OpenAIImageGenerator.py

import json
from typing import List, Literal
from openai import OpenAI
from swarmauri.core.llms.base.LLMBase import LLMBase

class OpenAIImageGenerator(LLMBase):
    api_key: str
    allowed_models: List[str] = ['dall-e']
    name: str = "dall-e"
    type: Literal['OpenAIImageGenerator'] = 'OpenAIImageGenerator'

    def predict(self, 
        prompt: str, 
        size: str = "1024x1024", 
        quality: str = "standard", 
        n: int = 1) -> str:
        """
        Generates an image based on the given prompt and other parameters.

        Parameters:
        - prompt (str): A description of the image you want to generate.
        - **kwargs: Additional parameters that the image generation endpoint might use.

        Returns:
        - str: A URL or identifier for the generated image.
        """
        try:
            client =  OpenAI(api_key=self.api_key)
            response = client.images.generate(
                model=self.name,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            result = response.json()
            return result
        
        except Exception as e:
            return str(e)

```

```swarmauri/standard/llms/concrete/OpenAIToolModel.py

import json
import logging
from typing import List, Literal, Dict, Any
from openai import OpenAI
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.OpenAISchemaConverter import OpenAISchemaConverter

class OpenAIToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gpt-4o', 
    'gpt-4o-2024-05-13',
    'gpt-4-turbo', 
    'gpt-4-turbo-2024-04-09',
    'gpt-4-turbo-preview',
    'gpt-4-0125-preview',
    'gpt-4-1106-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613']
    name: str = "gpt-3.5-turbo-0125"
    type: Literal['OpenAIToolModel'] = 'OpenAIToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [OpenAISchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = OpenAI(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(f"tool_response: {tool_response}")
        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_result,
                    }
                )
        logging.info(f'messages: {messages}')
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation

```

```swarmauri/standard/llms/concrete/GroqModel.py

import json
from typing import List, Optional, Dict, Literal
from groq import Groq
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class GroqModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "gemma-7b-it"
    type: Literal['GroqModel'] = 'GroqModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        temperature: float = 0.7, 
        max_tokens: int = 256, 
        top_p: float = 1.0, 
        enable_json: bool = False, 
        stop: Optional[List[str]] = None) -> str:

        formatted_messages = self._format_messages(conversation.history)

        client = Groq(api_key=self.api_key)
        stop = stop or []
        
        response_format = {"type": "json_object"} if enable_json else None
        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            response_format=response_format,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop
        )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

```

```swarmauri/standard/llms/concrete/GroqToolModel.py

from groq import Groq
import json
from typing import List, Literal, Dict, Any
import logging
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.GroqSchemaConverter import GroqSchemaConverter

class GroqToolModel(LLMBase):
    """
    Provider Documentation: https://console.groq.com/docs/tool-use#models
    """
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "gemma-7b-it"
    type: Literal['GroqToolModel'] = 'GroqToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GroqSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = Groq(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(tool_response)

        agent_message = AgentMessage(content=tool_response.choices[0].message.content) 
                                     #tool_calls=tool_response.choices[0].message.tool_calls)
        conversation.add_message(agent_message)


        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(content=func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message)
            
        logging.info(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        logging.info(agent_response)
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        return conversation

```

```swarmauri/standard/llms/concrete/MistralModel.py

import json
from typing import List, Literal, Dict
from mistralai.client import MistralClient
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class MistralModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['open-mistral-7b', 
    'open-mixtral-8x7b', 
    'open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-medium-latest',
    'mistral-large-latest',
    'codestral'
    ]
    name: str = "open-mixtral-8x7b"
    type: Literal['MistralModel'] = 'MistralModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        temperature: int = 0.7, 
        max_tokens: int = 256, 
        top_p: int = 1,
        enable_json: bool=False, 
        safe_prompt: bool=False):
        
        formatted_messages = self._format_messages(conversation.history)

        client =  MistralClient(api_key=self.api_key)        
        if enable_json:
            response = client.chat(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt
            )
        else:
            response = client.chat(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,                
                safe_prompt=safe_prompt
            )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

```

```swarmauri/standard/llms/concrete/MistralToolModel.py

import json
import logging
from typing import List, Literal, Dict, Any
from mistralai.client import MistralClient
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.MistralSchemaConverter import MistralSchemaConverter

class MistralToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-large-latest',
    ]
    name: str = "open-mixtral-8x22b"
    type: Literal['MistralToolModel'] = 'MistralToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [MistralSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'tool_call_id']
        #message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024, 
        safe_prompt: bool = False):

        client =  MistralClient(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"
            
        tool_response = client.chat(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                logging.info(type(tool_call.function.arguments))
                logging.info(tool_call.function.arguments)
                
                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_result,
                    }
                )
        logging.info(f"messages: {messages}")

        agent_response = client.chat(
            model=self.name,
            messages=messages
        )
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")      
        return conversation

```

```swarmauri/standard/llms/concrete/CohereModel.py

import json
import logging
from typing import List, Dict, Literal
import cohere
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class CohereModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['command-light',
    'command', 
    'command-r',
    'command-r-plus']
    name: str = "command-light"
    type: Literal['CohereModel'] = 'CohereModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str,str]]:
        """
        Cohere utilizes the following roles: CHATBOT, SYSTEM, TOOL, USER
        """
        message_properties = ['content', 'role']

        messages = [message.model_dump(include=message_properties) for message in messages]
        for message in messages:
            message['message'] = message.pop('content')
            if message.get('role') == 'assistant':
                message['role'] = 'chatbot'
            message['role'] = message['role'].upper()
        logging.info(messages)
        return messages


    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256):
        # Get next message
        next_message = conversation.history[-1].content

        # Format chat_history
        messages = self._format_messages(conversation.history[:-1])


        client = cohere.Client(api_key=self.api_key)
        response = client.chat(
            model=self.name,
            chat_history=messages,
            message=next_message,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_truncation='OFF',
            connectors=[]
        )
        
        result = json.loads(response.json())
        message_content = result['text']
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

```

```swarmauri/standard/llms/concrete/GeminiProModel.py

import json
from typing import List, Dict, Literal
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class GeminiProModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gemini-1.5-pro-latest']
    name: str = "gemini-1.5-pro-latest"
    type: Literal['GeminiProModel'] = 'GeminiProModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        # Remove system instruction from messages
        message_properties = ['content', 'role']
        sanitized_messages = [message.model_dump(include=message_properties) for message in messages 
            if message.role != 'system']

        for message in sanitized_messages:
            if message['role'] == 'assistant':
                message['role'] = 'model'

            # update content naming
            message['parts'] = message.pop('content')

        return sanitized_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == 'system':
                system_context = message.content
        return system_context
    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
            }

        safety_settings = [
          {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
        ]


        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)


        next_message = formatted_messages.pop()

        client = genai.GenerativeModel(model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_context)

        convo = client.start_chat(
            history=formatted_messages,
            )

        convo.send_message(next_message['parts'])

        message_content = convo.last.text
        conversation.add_message(AgentMessage(content=message_content))
        return conversation


```

```swarmauri/standard/llms/concrete/AnthropicModel.py

import json
from typing import List, Dict, Literal
import anthropic
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class AnthropicModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['claude-3-opus-20240229', 
    'claude-3-sonnet-20240229', 
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0',
    'claude-instant-1.2']
    name: str = "claude-3-haiku-20240307"
    type: Literal['AnthropicModel'] = 'AnthropicModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
       # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [message.model_dump(include=message_properties) for message in messages if message.role != 'system']
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == 'system':
                system_context = message.content
        return system_context

    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256):

        # Create client
        client = anthropic.Anthropic(api_key=self.api_key)
        
        # Get system_context from last message with system context in it
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        if system_context:
            response = client.messages.create(
                model=self.name,
                messages=formatted_messages,
                system=system_context,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            response = client.messages.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        message_content = response.content[0].text
        conversation.add_message(AgentMessage(content=message_content))
        
        return conversation


```

```swarmauri/standard/llms/concrete/CohereToolModel.py

import logging
import json
from typing import List, Literal
from typing import List, Dict, Any, Literal
import cohere
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.CohereSchemaConverter import CohereSchemaConverter

class CohereToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['command-r',
    'command-r-plus']
    name: str = "command-r"
    type: Literal['CohereToolModel'] = 'CohereToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        temperature=0.3,
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = cohere.Client(api_key=self.api_key)
        preamble = "" # 🚧  Placeholder for implementation logic

        logging.info(f"_schema_convert_tools: {self._schema_convert_tools(toolkit.tools)}")
        logging.info(f"message: {formatted_messages[-1]}")
        logging.info(f"formatted_messages: {formatted_messages}")

        tool_response = client.chat(
            model=self.name, 
            message=formatted_messages[-1]['content'], 
            chat_history=formatted_messages[:-1],
            force_single_step=True,
            tools=self._schema_convert_tools(toolkit.tools)
        )

        logging.info(f"tool_response: {tool_response}")
        logging.info(tool_response.text) 
        tool_results = []
        for tool_call in tool_response.tool_calls:
            logging.info(f"tool_call: {tool_call}")
            func_name = tool_call.name
            func_call = toolkit.get_tool_by_name(func_name)
            func_args = tool_call.parameters
            func_results = func_call(**func_args)
            tool_results.append({"call": tool_call, "outputs": [{'result': func_results}]}) # 🚧 Placeholder for variable key-names

        logging.info(f"tool_results: {tool_results}")
        agent_response = client.chat(
            model=self.name,
            message=formatted_messages[-1]['content'],
            chat_history=formatted_messages[:-1],
            tools=self._schema_convert_tools(toolkit.tools),
            force_single_step=True,
            tool_results=tool_results,
            temperature=temperature
        )

        logging.info(f"agent_response: {agent_response}")
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f"conversation: {conversation}")
        return conversation


```

```swarmauri/standard/llms/concrete/AnthropicToolModel.py

import json
from typing import List, Dict, Literal, Any
import logging
import anthropic
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.AnthropicSchemaConverter import AnthropicSchemaConverter

class AnthropicToolModel(LLMBase):
    """
    Provider resources: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    """
    api_key: str
    allowed_models: List[str] = ['claude-3-haiku-20240307',
    'claude-3-opus-20240229',
    'claude-3-sonnet-20240229']
    name: str = "claude-3-haiku-20240307"
    type: Literal['AnthropicToolModel'] = 'AnthropicToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        schema_result = [AnthropicSchemaConverter().convert(tools[tool]) for tool in tools]
        logging.info(schema_result)
        return schema_result

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = anthropic.Anthropic(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = {"type":"auto"}

        tool_response = client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )


        logging.info(f"tool_response: {tool_response}")
        tool_text_response = None
        if tool_response.content[0].type =='text':
            tool_text_response = tool_response.content[0].text
            logging.info(f"tool_text_response: {tool_text_response}")

        for tool_call in tool_response.content:
            if tool_call.type == 'tool_use':
                func_name = tool_call.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.input
                func_result = func_call(**func_args)


        if tool_text_response:
            agent_response = f"{tool_text_response} {func_result}"
        else:
            agent_response = f"{func_result}"

        agent_message = AgentMessage(content=agent_response)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation

```

```swarmauri/standard/llms/concrete/GeminiToolModel.py

import logging
import json
from typing import List, Literal, Dict, Any
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.GeminiSchemaConverter import GeminiSchemaConverter
import google.generativeai as genai

class GeminiToolModel(LLMBase):
    """
    3rd Party's Resources: https://ai.google.dev/api/python/google/generativeai/protos/
    """
    api_key: str
    allowed_models: List[str] = ['gemini-1.5-pro-latest']
    name: str = "gemini-1.5-pro-latest"
    type: Literal['GeminiToolModel'] = 'GeminiToolModel'

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GeminiSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        # Remove system instruction from messages
        message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        sanitized_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages 
            if message.role != 'system']

        for message in sanitized_messages:
            if message['role'] == 'assistant':
                message['role'] = 'model'

            if message['role'] == 'tool':
                message['role'] == 'user'

            # update content naming
            message['parts'] = message.pop('content')

        return sanitized_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        temperature=0.7, 
        max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
            }

        safety_settings = [
          {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
        ]

        tool_config = {
              "function_calling_config": {
                "mode": "ANY"
              },
            }

        client = genai.GenerativeModel(model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            tool_config=tool_config)

        formatted_messages = self._format_messages(conversation.history)
        logging.info(f'formatted_messages: {formatted_messages}')

        tool_response = client.generate_content(
            formatted_messages,
            tools=self._schema_convert_tools(toolkit.tools),
        )
        logging.info(f'tool_response: {tool_response}')

        formatted_messages.append(tool_response.candidates[0].content)


        logging.info(f"tool_response.candidates[0].content: {tool_response.candidates[0].content}")




        tool_calls = tool_response.candidates[0].content.parts

        tool_results = {}
        for tool_call in tool_calls:
            func_name = tool_call.function_call.name
            func_args = tool_call.function_call.args
            logging.info(f"func_name: {func_name}")
            logging.info(f"func_args: {func_args}")

            func_call = toolkit.get_tool_by_name(func_name)
            func_result = func_call(**func_args)
            logging.info(f"func_result: {func_result}")
            tool_results[func_name] = func_result

        formatted_messages.append(genai.protos.Content(role="function",
            parts=[
                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                    name=fn,
                    response={
                        "result": val,  # Return the API response to Gemini
                    },
                )) for fn, val in tool_results.items()]
            ))

        logging.info(f'formatted_messages: {formatted_messages}')

        agent_response = client.generate_content(formatted_messages)

        logging.info(f'agent_response: {agent_response}')
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f'conversation: {conversation}')
        return conversation

```

```swarmauri/standard/llms/concrete/PerplexityModel.py

import json
from typing import List, Dict, Literal, Optional
import requests
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class PerplexityModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama-3-sonar-small-32k-chat',
        'llama-3-sonar-small-32k-online',
        'llama-3-sonar-large-32k-chat',
        'llama-3-sonar-large-32k-online',
        'llama-3-8b-instruct',
        'llama-3-70b-instruct',
        'mixtral-8x7b-instruct']
    name: str = "mixtral-8x7b-instruct"
    type: Literal['PerplexityModel'] = 'PerplexityModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256, 
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None
        ):


        if top_p and top_k:
            raise ValueError('Do not set top_p and top_k')


        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": True,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)
        message_content = response.text
        conversation.add_message(AgentMessage(content=message_content))
        return conversation





```

```swarmauri/standard/agents/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/base/__init__.py



```

```swarmauri/standard/agents/base/AgentToolMixin.py

from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase
from swarmauri.core.agents.IAgentToolkit import IAgentToolkit

class AgentToolMixin(IAgentToolkit, BaseModel):
    toolkit: SubclassUnion[ToolkitBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    

```

```swarmauri/standard/agents/base/AgentBase.py

from typing import Any, Optional, Dict, Union, Literal
from pydantic import ConfigDict, Field, field_validator
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.standard.llms.base.LLMBase import LLMBase

class AgentBase(IAgent, ComponentBase):
    llm: SubclassUnion[LLMBase]
    resource: ResourceTypes =  Field(default=ResourceTypes.AGENT.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['AgentBase'] = 'AgentBase'

    def exec(self, input_str: Optional[Union[str, IMessage]] = "", llm_kwargs: Optional[Dict] = {}) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')

```

```swarmauri/standard/agents/base/AgentVectorStoreMixin.py

from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentVectorStore import IAgentVectorStore
from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase

class AgentVectorStoreMixin(IAgentVectorStore, BaseModel):
    vector_store: SubclassUnion[VectorStoreBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

```

```swarmauri/standard/agents/base/AgentRetrieveMixin.py

from abc import ABC
from typing import List
from pydantic import BaseModel, ConfigDict, field_validator, Field
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.core.agents.IAgentRetrieve import IAgentRetrieve

class AgentRetrieveMixin(IAgentRetrieve, BaseModel):
    last_retrieved: List[Document] = Field(default_factory=list)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)



```

```swarmauri/standard/agents/base/AgentSystemContextMixin.py

from typing import Union
from pydantic import BaseModel, field_validator

from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.core.agents.IAgentSystemContext import IAgentSystemContext


class AgentSystemContextMixin(IAgentSystemContext, BaseModel):
    system_context:  Union[SystemMessage, str]

    @field_validator('system_context', mode='before')
    def set_system_context(cls, value: Union[str, SystemMessage]) -> SystemMessage:
        if isinstance(value, str):
            return SystemMessage(content=value)
        return value

```

```swarmauri/standard/agents/base/AgentConversationMixin.py

from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class AgentConversationMixin(IAgentConversation, BaseModel):
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

```

```swarmauri/standard/agents/concrete/__init__.py



```

```swarmauri/standard/agents/concrete/ToolAgent.py

from pydantic import ConfigDict
from typing import Any, Optional, Union, Dict, Literal
import json
import logging
from swarmauri.core.messages import IMessage

from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.agents.base.AgentToolMixin import AgentToolMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class ToolAgent(AgentToolMixin, AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    toolkit: SubclassUnion[Toolkit]
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolAgent'] = 'ToolAgent'
    
    def exec(self, 
        input_data: Optional[Union[str, IMessage]] = "",  
        llm_kwargs: Optional[Dict] = {}) -> Any:

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(content=input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        self.conversation.add_message(human_message)

        #predict a response        
        self.conversation = self.llm.predict(
            conversation=self.conversation, 
            toolkit=self.toolkit, 
            **llm_kwargs)

        logging.info(self.conversation.get_last().content)

        return self.conversation.get_last().content

```

```swarmauri/standard/agents/concrete/SimpleConversationAgent.py

from typing import Any, Optional, Dict, Literal

from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri.core.typing import SubclassUnion # 🚧  Placeholder
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase # 🚧  Placeholder

class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    type: Literal['SimpleConversationAgent'] = 'SimpleConversationAgent'
    
    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        if input_str:
            human_message = HumanMessage(content=input_str)
            self.conversation.add_message(human_message)
        
        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content

```

```swarmauri/standard/agents/concrete/RagAgent.py

from typing import Any, Optional, Union, Dict, Literal
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentRetrieveMixin import AgentRetrieveMixin
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.agents.base.AgentVectorStoreMixin import AgentVectorStoreMixin
from swarmauri.standard.agents.base.AgentSystemContextMixin import AgentSystemContextMixin

from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase

class RagAgent(AgentRetrieveMixin, 
               AgentVectorStoreMixin, 
               AgentSystemContextMixin, 
               AgentConversationMixin, 
               AgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase]
    vector_store: SubclassUnion[VectorStoreBase]
    system_context:  Union[SystemMessage, str]
    type: Literal['RagAgent'] = 'RagAgent'
    
    def _create_preamble_context(self):
        substr = self.system_context.content
        substr += '\n\n'
        substr += '\n'.join([doc.content for doc in self.last_retrieved])
        return substr

    def _create_post_context(self):
        substr = '\n'.join([doc.content for doc in self.last_retrieved])
        substr += '\n\n'
        substr += self.system_context.content
        return substr

    def exec(self, 
             input_data: Optional[Union[str, IMessage]] = "", 
             top_k: int = 5, 
             preamble: bool = True,
             fixed: bool = False,
             llm_kwargs: Optional[Dict] = {}
             ) -> Any:
        try:
            # Check if the input is a string, then wrap it in a HumanMessage
            if isinstance(input_data, str):
                human_message = HumanMessage(content=input_data)
            elif isinstance(input_data, IMessage):
                human_message = input_data
            else:
                raise TypeError("Input data must be a string or an instance of Message.")
            
            # Add the human message to the conversation
            self.conversation.add_message(human_message)

            # Retrieval and set new substr for system context
            if top_k > 0 and len(self.vector_store.documents) > 0:
                self.last_retrieved = self.vector_store.retrieve(query=input_data, top_k=top_k)

                if preamble:
                    substr = self._create_preamble_context()
                else:
                    substr = self._create_post_context()

            else:
                if fixed:
                    if preamble:
                        substr = self._create_preamble_context()
                    else:
                        substr = self._create_post_context()
                else:
                    substr = self.system_context.content
                    self.last_retrieved = []
                
            # Use substr to set system context
            system_context = SystemMessage(content=substr)
            self.conversation.system_context = system_context
            

            # Retrieve the conversation history and predict a response
            if llm_kwargs:
                self.llm.predict(conversation=self.conversation, **llm_kwargs)
            else:
                self.llm.predict(conversation=self.conversation)
                
            return self.conversation.get_last().content

        except Exception as e:
            print(f"RagAgent error: {e}")
            raise e

```

```swarmauri/standard/agents/concrete/QAAgent.py

from typing import Any, Optional, Dict, Literal

from swarmauri.standard.conversations.concrete.MaxSizeConversation import MaxSizeConversation
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.agents.base.AgentBase import AgentBase

class QAAgent(AgentBase):
    conversation: MaxSizeConversation = MaxSizeConversation(max_size=2)
    type: Literal['QAAgent'] = 'QAAgent'
    
    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        
        self.conversation.add_message(HumanMessage(content=input_str))
        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        
        return self.conversation.get_last().content

```

```swarmauri/standard/utils/__init__.py



```

```swarmauri/standard/utils/load_documents_from_json.py

import json
from typing import List
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument

def load_documents_from_json_file(json_file_path):
    documents = []
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    documents = [
        EmbeddedDocument(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]

    return documents

def load_documents_from_json(json):
    documents = []
    data = json.loads(json)
    documents = [
        EmbeddedDocument(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]
    return documents


```

```swarmauri/standard/utils/get_class_hash.py

import hashlib
import inspect

def get_class_hash(cls):
    """
    Generates a unique hash value for a given class.

    This function uses the built-in `hashlib` and `inspect` modules to create a hash value based on the class' methods
    and properties. The members of the class are first sorted to ensure a consistent order, and then the hash object is
    updated with each member's name and signature.

    Parameters:
    - cls (type): The class object to calculate the hash for.

    Returns:
    - str: The generated hexadecimal hash value.
    """
    hash_obj = hashlib.sha256()

    # Get the list of methods and properties of the class
    members = inspect.getmembers(cls, predicate=inspect.isfunction)
    members += inspect.getmembers(cls, predicate=inspect.isdatadescriptor)

    # Sort members to ensure consistent order
    members.sort()

    # Update the hash with each member's name and signature
    for name, member in members:
        hash_obj.update(name.encode('utf-8'))
        if inspect.isfunction(member):
            sig = inspect.signature(member)
            hash_obj.update(str(sig).encode('utf-8'))

    # Return the hexadecimal digest of the hash
    return hash_obj.hexdigest()


```

```swarmauri/standard/utils/sql_log.py

import sqlite3
from datetime import datetime
import asyncio


def sql_log(self, db_path: str, conversation_id, model_name, prompt, response, start_datetime, end_datetime):
    try:
        duration = (end_datetime - start_datetime).total_seconds()
        start_datetime = start_datetime.isoformat()
        end_datetime = end_datetime.isoformat()
        conversation_id = conversation_id
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        conversation_id TEXT, 
                        model_name TEXT, 
                        prompt TEXT, 
                        response TEXT, 
                        start_datetime TEXT, 
                        end_datetime TEXT,
                        duration NUMERIC)''')
        cursor.execute('''INSERT INTO conversations (
                        conversation_id, 
                        model_name, 
                        prompt, 
                        response, 
                        start_datetime, 
                        end_datetime,
                        duration) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (conversation_id, 
                        model_name, 
                        prompt, 
                        response, 
                        start_datetime, 
                        end_datetime, 
                        duration))
        conn.commit()
        conn.close()
    except:
        raise



def sql_log_decorator(func):
    async def wrapper(self, *args, **kwargs):
        start_datetime = datetime.now()
        try:
            # Execute the function
            result = await func(self, *args, **kwargs)
        except Exception as e:
            # Handle errors within the decorated function
            self.agent.conversation._history.pop(0)
            print(f"chatbot_function error: {e}")
            return "", [], kwargs['history']  

        end_datetime = datetime.now()
        
        # SQL logging
        # Unpacking the history and other required parameters from kwargs if they were used
        history = kwargs.get('history', [])
        message = kwargs.get('message', '')
        response = result[1]  # Assuming the response is the second item in the returned tuple
        model_name = kwargs.get('model_name', '')
        conversation_id = str(self.agent.conversation.id)
        sql_log(conversation_id, model_name, message, response, start_datetime, end_datetime)
        return result
    return wrapper


class SqlLogMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if callable(value) and not key.startswith('__'):
                dct[key] = sql_log(value)
        return super().__new__(cls, name, bases, dct)

```

```swarmauri/standard/utils/memoize.py

def memoize(func):
    cache = {}
    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return memoized_func
    
class MemoizingMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if callable(value) and not key.startswith('__'):
                dct[key] = memoize(value)
        return super().__new__(cls, name, bases, dct)


```

```swarmauri/standard/utils/apply_metaclass.py

def apply_metaclass_to_cls(cls, metaclass):
    # Create a new class using the metaclass, with the same name, bases, and attributes as the original class
    new_class = metaclass(cls.__name__, cls.__bases__, dict(cls.__dict__))
    return new_class


```

```swarmauri/standard/utils/decorate.py

def decorate_cls(cls, decorator_fn):
    import types
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if isinstance(attr, types.FunctionType):
            setattr(cls, attr_name, decorator_fn(attr))
    return cls

def decorate_instance(instance, decorator_fn):
    import types
    for attr_name in dir(instance):
        attr = getattr(instance, attr_name)
        if isinstance(attr, types.MethodType):
            setattr(instance, attr_name, decorator_fn(attr.__func__).__get__(instance))

def decorate_instance_method(instance, method_name, decorator_fn):
    # Get the method from the instance
    original_method = getattr(instance, method_name)
    
    # Decorate the method
    decorated_method = decorator_fn(original_method)
    
    # Rebind the decorated method to the instance
    setattr(instance, method_name, decorated_method.__get__(instance, instance.__class__))

```

```swarmauri/standard/utils/json_validator.py

# swarmauri/standard/utils/json_validator.py
import json
import jsonschema
from jsonschema import validate

def load_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)

def validate_json(data: dict, schema_file: str) -> bool:
    schema = load_json_file(schema_file)
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print(f"JSON validation error: {err.message}")
        return False
    return True

```

```swarmauri/standard/conversations/__init__.py



```

```swarmauri/standard/conversations/base/__init__.py



```

```swarmauri/standard/conversations/base/ConversationSystemContextMixin.py

from abc import ABC
from typing import Optional, Literal
from pydantic import BaseModel
from swarmauri.core.conversations.ISystemContext import ISystemContext
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class ConversationSystemContextMixin(ISystemContext, BaseModel):
    system_context: Optional[SystemMessage]


```

```swarmauri/standard/conversations/base/ConversationBase.py

from typing import List, Union, Literal
from pydantic import Field, PrivateAttr, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.conversations.IConversation import IConversation

class ConversationBase(IConversation, ComponentBase):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    _history: List[SubclassUnion[MessageBase]] = PrivateAttr(default_factory=list)
    resource: ResourceTypes =  Field(default=ResourceTypes.CONVERSATION.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ConversationBase'] = 'ConversationBase'

    @property
    def history(self) -> List[SubclassUnion[MessageBase]]:
        """
        Provides read-only access to the conversation history.
        """
        return self._history
    
    def add_message(self, message: SubclassUnion[MessageBase]):
        self._history.append(message)

    def get_last(self) -> Union[SubclassUnion[MessageBase], None]:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self):
        self._history.clear()


```

```swarmauri/standard/conversations/concrete/__init__.py



```

```swarmauri/standard/conversations/concrete/MaxSizeConversation.py

from typing import Literal
from pydantic import Field
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize

class MaxSizeConversation(IMaxSize, ConversationBase):
    max_size: int = Field(default=2, gt=1)
    type: Literal['MaxSizeConversation'] = 'MaxSizeConversation'

    def add_message(self, message: IMessage):
        """Adds a message and ensures the conversation does not exceed the max size."""
        super().add_message(message)
        self._enforce_max_size_limit()

    def _enforce_max_size_limit(self):
        """
        Enforces the maximum size limit of the conversation history.
        If the current history size exceeds the maximum size, the oldest messages are removed.
        We pop two messages (one for the user's prompt, one for the assistant's response)
        """
        while len(self._history) > self.max_size:
            
            self._history.pop(0)
            self._history.pop(0)

```

```swarmauri/standard/conversations/concrete/MaxSystemContextConversation.py

from typing import Optional, Union, List, Literal
from pydantic import Field, ConfigDict, field_validator
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.conversations.base.ConversationSystemContextMixin import ConversationSystemContextMixin
from swarmauri.standard.messages.concrete import SystemMessage, AgentMessage, HumanMessage
from swarmauri.standard.exceptions.concrete import IndexErrorWithContext

class MaxSystemContextConversation(IMaxSize, ConversationSystemContextMixin, ConversationBase):
    system_context: Optional[SystemMessage] = SystemMessage(content="")
    max_size: int = Field(default=2, gt=1)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['MaxSystemContextConversation'] = 'MaxSystemContextConversation'
    
    @field_validator('system_context', mode='before')
    def set_system_context(cls, value: Union[str, SystemMessage]) -> SystemMessage:
        if isinstance(value, str):
            return SystemMessage(content=value)
        return value
    
    @property
    def history(self) -> List[IMessage]:
        """
        Get the conversation history, ensuring it starts with a 'user' message and alternates correctly between 'user' and 'assistant' roles.
        The maximum number of messages returned does not exceed max_size + 1.
        """
        res = []  # Start with an empty list to build the proper history

        # Attempt to find the first 'user' message in the history.
        user_start_index = -1
        for index, message in enumerate(self._history):
            if isinstance(message, HumanMessage):  # Identify user message
                user_start_index = index
                break

        # If no 'user' message is found, just return the system context.
        if user_start_index == -1:
            return [self.system_context]

        # Build history from the first 'user' message ensuring alternating roles.
        res.append(self.system_context)
        alternating = True
        count = 0 
        for message in self._history[user_start_index:]:
            if count >= self.max_size: # max size
                break
            if alternating and isinstance(message, HumanMessage) or not alternating and isinstance(message, AgentMessage):
                res.append(message)
                alternating = not alternating
                count += 1
            elif not alternating and isinstance(message, HumanMessage):
                # If we find two 'user' messages in a row when expecting an 'assistant' message, we skip this 'user' message.
                continue
            else:
                # If there is no valid alternate message to append, break the loop
                break

        return res

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        elif isinstance(message, IMessage):
            self._history.append(message)
        else:
            raise ValueError(f"Must use a subclass of IMessage")
        self._enforce_max_size_limit()
        
    def _enforce_max_size_limit(self):
        """
        Remove messages from the beginning of the conversation history if the limit is exceeded.
        We add one to max_size to account for the system context message
        """
        try:
            while len(self._history) > self.max_size + 1:
                self._history.pop(0)
                self._history.pop(0)
        except IndexError as e:
            raise IndexErrorWithContext(e)


```

```swarmauri/standard/conversations/concrete/SessionCacheConversation.py

from typing import Optional, Union, List, Literal
from pydantic import Field, ConfigDict
from collections import deque
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.conversations.base.ConversationSystemContextMixin import ConversationSystemContextMixin
from swarmauri.standard.messages.concrete import SystemMessage, AgentMessage, HumanMessage, FunctionMessage
from swarmauri.standard.exceptions.concrete import IndexErrorWithContext


class SessionCacheConversation(IMaxSize, ConversationSystemContextMixin, ConversationBase):
    max_size: int = Field(default=2, gt=1)
    system_context: Optional[SystemMessage] = None
    session_max_size: int = Field(default=-1)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['SessionCacheConversation'] = 'SessionCacheConversation'

    def __init__(self, **data):
        super().__init__(**data)
        if self.session_max_size == -1:
            self.session_max_size = self.max_size

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        This only allows system context to be set through the system context method.
        We are forcing the SystemContext to be a preamble only.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        if not self._history and not isinstance(message, HumanMessage):
            raise ValueError("The first message in the history must be an HumanMessage.")
        if self._history and isinstance(self._history[-1], HumanMessage) and isinstance(message, HumanMessage):
            raise ValueError("Cannot have two repeating HumanMessages.")
        
        super().add_message(message)


    def session_to_dict(self) -> List[dict]:
        """
        Converts session messages to a list of dictionaries.
        """
        included_fields = {"role", "content"}
        return [message.dict(include=included_fields) for message in self.session]
    
    @property
    def session(self) -> List[IMessage]:
        return self._history[-self.session_max_size:]

    @property
    def history(self):
        res = []
        if not self._history or self.max_size == 0:
            if self.system_context:
                return [self.system_context]
            else:
                return []

        # Initialize alternating with the expectation to start with HumanMessage
        alternating = True
        count = 0

        for message in self._history[-self.max_size:]:
            if isinstance(message, HumanMessage) and alternating:
                res.append(message)
                alternating = not alternating  # Switch to expecting AgentMessage
                count += 1
            elif isinstance(message, AgentMessage) and not alternating:
                res.append(message)
                alternating = not alternating  # Switch to expecting HumanMessage
                count += 1

            if count >= self.max_size:
                break
                
        if self.system_context:
            res = [self.system_context] + res
            
        return res



```

```swarmauri/standard/conversations/concrete/Conversation.py

from typing import Literal
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class Conversation(ConversationBase):
    """
    Concrete implementation of ConversationBase, managing conversation history and operations.
    """    
    type: Literal['Conversation'] = 'Conversation'

```

```swarmauri/standard/documents/__init__.py

from .concrete import *
from .base import *

```

```swarmauri/standard/documents/base/__init__.py



```

```swarmauri/standard/documents/base/DocumentBase.py

from typing import Dict, Optional, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.vectors.concrete.Vector import Vector


class DocumentBase(IDocument, ComponentBase):
    content: str
    metadata: Dict = {}
    embedding: Optional[Vector] = None
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.DOCUMENT.value, frozen=True)
    type: Literal['DocumentBase'] = 'DocumentBase'

```

```swarmauri/standard/documents/concrete/__init__.py

from .Document import Document

```

```swarmauri/standard/documents/concrete/Document.py

from typing import Literal
from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class Document(DocumentBase):
    type: Literal['Document'] = 'Document'

```

```swarmauri/standard/messages/__init__.py



```

```swarmauri/standard/messages/base/__init__.py



```

```swarmauri/standard/messages/base/MessageBase.py

from typing import Optional, Tuple, Literal
from pydantic import PrivateAttr, ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.messages.IMessage import IMessage

class MessageBase(IMessage, ComponentBase):
    content: str
    role: str
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.MESSAGE.value, frozen=True)
    type: Literal['MessageBase'] = 'MessageBase'


```

```swarmauri/standard/messages/concrete/__init__.py

from .HumanMessage import HumanMessage
from .AgentMessage import AgentMessage
from .FunctionMessage import FunctionMessage
from .SystemMessage import SystemMessage

```

```swarmauri/standard/messages/concrete/AgentMessage.py

from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class AgentMessage(MessageBase):
    content: Optional[str] = None
    role: str = Field(default='assistant')
    #tool_calls: Optional[Any] = None
    name: Optional[str] = None
    type: Literal['AgentMessage'] = 'AgentMessage'
    usage: Optional[Any] = None # 🚧 Placeholder for CompletionUsage(input_tokens, output_tokens, completion time, etc)

```

```swarmauri/standard/messages/concrete/HumanMessage.py

from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class HumanMessage(MessageBase):
    content: str
    role: str = Field(default='user')
    name: Optional[str] = None
    type: Literal['HumanMessage'] = 'HumanMessage'    

```

```swarmauri/standard/messages/concrete/FunctionMessage.py

from typing import Literal, Optional, Any
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class FunctionMessage(MessageBase):
    content: str
    role: str = Field(default='tool')
    tool_call_id: str
    name: str
    type: Literal['FunctionMessage'] = 'FunctionMessage'
    usage: Optional[Any] = None # 🚧 Placeholder for CompletionUsage(input_tokens, output_tokens, completion time, etc)

```

```swarmauri/standard/messages/concrete/SystemMessage.py

from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class SystemMessage(MessageBase):
    content: str
    role: str = Field(default='system')
    type: Literal['SystemMessage'] = 'SystemMessage'

```

```swarmauri/standard/parsers/__init__.py



```

```swarmauri/standard/parsers/base/__init__.py



```

```swarmauri/standard/parsers/base/ParserBase.py

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Any, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.documents.IDocument import IDocument

class ParserBase(ComponentBase, ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.PARSER.value)
    type: Literal['ParserBase'] = 'ParserBase'
    
    @abstractmethod
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.
        
        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass


```

```swarmauri/standard/parsers/concrete/__init__.py



```

```swarmauri/standard/parsers/concrete/CSVParser.py

import csv
from io import StringIO
from typing import List, Union, Any, Literal
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class CSVParser(ParserBase):
    """
    Concrete implementation of IParser for parsing CSV formatted text into Document instances.

    The parser can handle input as a CSV formatted string or from a file, with each row
    represented as a separate Document. Assumes the first row is the header which will
    be used as keys for document metadata.
    """
    type: Literal['CSVParser'] = 'CSVParser'
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given CSV data into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The input data to parse, either as a CSV string or file path.

        Returns:
        - List[IDocument]: A list of documents parsed from the CSV data.
        """
        # Prepare an in-memory string buffer if the data is provided as a string
        if isinstance(data, str):
            data_stream = StringIO(data)
        else:
            raise ValueError("Data provided is not a valid CSV string")

        # Create a list to hold the parsed documents
        documents: List[IDocument] = []

        # Read CSV content row by row
        reader = csv.DictReader(data_stream)
        for row in reader:
            # Each row represents a document, where the column headers are metadata fields
            document = Document(doc_id=row.get('id', None), 
                                        content=row.get('content', ''), 
                                        metadata=row)
            documents.append(document)

        return documents

```

```swarmauri/standard/parsers/concrete/EntityRecognitionParser.py

import spacy
from typing import List, Union, Any, Literal
from pydantic import PrivateAttr
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class EntityRecognitionParser(ParserBase):
    """
    EntityRecognitionParser leverages NER capabilities to parse text and 
    extract entities with their respective tags such as PERSON, LOCATION, ORGANIZATION, etc.
    """
    _nlp: Any = PrivateAttr()
    type: Literal['EntityRecognitionParser'] = 'EntityRecognitionParser'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load a SpaCy model. The small model is used for demonstration; larger models provide improved accuracy.
        self._nlp = spacy.load("en_core_web_sm")
    
    def parse(self, text: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input text, identifies entities, and returns a list of documents with entities tagged.

        Parameters:
        - text (Union[str, Any]): The input text to be parsed and analyzed for entities.

        Returns:
        - List[IDocument]: A list of IDocument instances representing the identified entities in the text.
        """
        # Ensure the input is a string type before processing
        if not isinstance(text, str):
            text = str(text)
        
        # Apply the NER model
        doc = self._nlp(text)

        # Compile identified entities into documents
        entities_docs = []
        for ent in doc.ents:
            # Create a document for each entity with metadata carrying entity type
            entity_doc = Document(doc_id=ent.text, content=ent.text, metadata={"entity_type": ent.label_})
            entities_docs.append(entity_doc)
        
        return entities_docs

```

```swarmauri/standard/parsers/concrete/HTMLTagStripParser.py

import html
import re
from typing import Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class HTMLTagStripParser(ParserBase):
    """
    A concrete parser that removes HTML tags and unescapes HTML content,
    leaving plain text.
    """
    type: Literal['HTMLTagStripParser'] = 'HTMLTagStripParser'

    def parse(self, data: str):
        """
        Strips HTML tags from input data and unescapes HTML content.
        
        Args:
            data (str): The HTML content to be parsed.
        
        Returns:
            List[IDocument]: A list containing a single IDocument instance of the stripped text.
        """

        # Ensure that input is a string
        if not isinstance(data, str):
            raise ValueError("HTMLTagStripParser expects input data to be of type str.")
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', data)  # Matches anything in < > and replaces it with empty string
        
        # Unescape HTML entities
        text = html.unescape(text)

        # Wrap the cleaned text into a Document and return it in a list
        document = Document(content=text, metadata={"original_length": len(data)})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/KeywordExtractorParser.py

import yake
from typing import List, Union, Any, Literal
from pydantic import ConfigDict, PrivateAttr
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class KeywordExtractorParser(ParserBase):
    """
    Extracts keywords from text using the YAKE keyword extraction library.
    """
    lang: str = 'en'
    num_keywords: int = 10
    _kw_extractor: yake.KeywordExtractor = PrivateAttr(default=None)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['KeywordExtractorParser'] = 'KeywordExtractorParser'
    
    def __init__(self, **data):
        super().__init__(**data)
        self._kw_extractor = yake.KeywordExtractor(lan=self.lang,
                                                   n=3, 
                                                   dedupLim=0.9, 
                                                   dedupFunc='seqm', 
                                                   windowsSize=1, 
                                                   top=self.num_keywords, 
                                                   features=None)
    

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Extract keywords from input text and return as list of Document instances containing keyword information.

        Parameters:
        - data (Union[str, Any]): The input text from which to extract keywords.

        Returns:
        - List[Document]: A list of Document instances, each containing information about an extracted keyword.
        """
        # Ensure data is in string format for analysis
        text = str(data) if not isinstance(data, str) else data

        # Extract keywords using YAKE
        keywords = self._kw_extractor.extract_keywords(text)

        # Create Document instances for each keyword
        documents = [Document(content=keyword, metadata={"score": score}) for index, (keyword, score) in enumerate(keywords)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/MarkdownParser.py

import re
from typing import List, Tuple, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase


class MarkdownParser(ParserBase):
    """
    A concrete implementation of the IParser interface that parses Markdown text.
    
    This parser takes Markdown formatted text, converts it to HTML using Python's
    markdown library, and then uses BeautifulSoup to extract plain text content. The
    resulting plain text is then wrapped into Document instances.
    """
    rules: List[Tuple[str, str]] = [
            (r'###### (.*)', r'<h6>\1</h6>'),
            (r'##### (.*)', r'<h5>\1</h5>'),
            (r'#### (.*)', r'<h4>\1</h4>'),
            (r'### (.*)', r'<h3>\1</h3>'),
            (r'## (.*)', r'<h2>\1</h2>'),
            (r'# (.*)', r'<h1>\1</h1>'),
            (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),
            (r'\*(.*?)\*', r'<em>\1</em>'),
            (r'!\[(.*?)\]\((.*?)\)', r'<img alt="\1" src="\2" />'),
            (r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>'),
            (r'\n\n', r'<p>'),
            (r'\n', r'<br>'),
        ]
    type: Literal['MarkdownParser'] = 'MarkdownParser'

    def parse(self, data: str) -> List[Document]:
        documents = []
        for pattern, repl in self.rules:
            data = re.sub(pattern, repl, data)
        documents.append( Document(content=data, metadata={} ))
        
        return documents

```

```swarmauri/standard/parsers/concrete/OpenAPISpecParser.py

import yaml
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class OpenAPISpecParser(ParserBase):
    """
    A parser that processes OpenAPI Specification files (YAML or JSON format)
    and extracts information into structured Document instances. 
    This is useful for building documentation, APIs inventory, or analyzing the API specification.
    """
    type: Literal['OpenAPISpecParser'] = 'OpenAPISpecParser'
    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses an OpenAPI Specification from a YAML or JSON string into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The OpenAPI specification in YAML or JSON format as a string.

        Returns:
        - List[IDocument]: A list of Document instances representing the parsed information.
        """
        try:
            # Load the OpenAPI spec into a Python dictionary
            spec_dict = yaml.safe_load(data)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse the OpenAPI specification: {e}")
        
        documents = []
        # Iterate over paths in the OpenAPI spec to extract endpoint information
        for path, path_item in spec_dict.get("paths", {}).items():
            for method, operation in path_item.items():
                # Create a Document instance for each operation
                content = yaml.dump(operation)
                metadata = {
                    "path": path,
                    "method": method.upper(),
                    "operationId": operation.get("operationId", "")
                }
                document = Document(content=content, metadata=metadata)
                documents.append(document)

        return documents

```

```swarmauri/standard/parsers/concrete/PhoneNumberExtractorParser.py

import re
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class PhoneNumberExtractorParser(ParserBase):
    """
    A parser that extracts phone numbers from the input text.
    Utilizes regular expressions to identify phone numbers in various formats.
    """
    type: Literal['PhoneNumberExtractorParser'] = 'PhoneNumberExtractorParser'
    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input data, looking for phone numbers employing a regular expression.
        Each phone number found is contained in a separate IDocument instance.

        Parameters:
        - data (Union[str, Any]): The input text to be parsed for phone numbers.

        Returns:
        - List[IDocument]: A list of IDocument instances, each containing a phone number.
        """
        # Define a regular expression for phone numbers.
        # This is a simple example and might not capture all phone number formats accurately.
        phone_regex = r'\+?\d[\d -]{8,}\d'

        # Find all occurrences of phone numbers in the text
        phone_numbers = re.findall(phone_regex, str(data))

        # Create a new IDocument for each phone number found
        documents = [Document(content=phone_number, metadata={}) for index, phone_number in enumerate(phone_numbers)]

        return documents

```

```swarmauri/standard/parsers/concrete/PythonParser.py

import ast
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase
from swarmauri.core.documents.IDocument import IDocument

class PythonParser(ParserBase):
    """
    A parser that processes Python source code to extract structural elements
    such as functions, classes, and their docstrings.
    
    This parser utilizes the `ast` module to parse the Python code into an abstract syntax tree (AST)
    and then walks the tree to extract relevant information.
    """
    type: Literal['PythonParser'] = 'PythonParser'
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given Python source code to extract structural elements.

        Args:
            data (Union[str, Any]): The input Python source code as a string.

        Returns:
            List[IDocument]: A list of IDocument objects, each representing a structural element 
                             extracted from the code along with its metadata.
        """
        if not isinstance(data, str):
            raise ValueError("PythonParser expects a string input.")
        
        documents = []
        tree = ast.parse(data)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                element_name = node.name
                docstring = ast.get_docstring(node)
                
                # Get the source code snippet
                source_code = ast.get_source_segment(data, node)
                
                # Create a metadata dictionary
                metadata = {
                    "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                    "name": element_name,
                    "docstring": docstring,
                    "source_code": source_code
                }
                
                # Create a Document for each structural element
                document = Document(content=docstring, metadata=metadata)
                documents.append(document)
                
        return documents

```

```swarmauri/standard/parsers/concrete/RegExParser.py

import re
from typing import List, Union, Any, Literal, Pattern
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class RegExParser(ParserBase):
    """
    A parser that uses a regular expression to extract information from text.
    """
    pattern: Pattern = re.compile(r'\d+')
    type: Literal['RegExParser'] = 'RegExParser'
    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input data using the specified regular expression pattern and
        returns a list of IDocument instances containing the extracted information.

        Parameters:
        - data (Union[str, Any]): The input data to be parsed. It can be a string or any format 
                                   that the concrete implementation can handle.

        Returns:
        - List[IDocument]: A list of IDocument instances containing the parsed information.
        """
        # Ensure data is a string
        if not isinstance(data, str):
            data = str(data)

        # Use the regular expression pattern to find all matches in the text
        matches = self.pattern.findall(data)

        # Create a Document for each match and collect them into a list
        documents = [Document(content=match, metadata={}) for i, match in enumerate(matches)]

        return documents

```

```swarmauri/standard/parsers/concrete/TextBlobNounParser.py

from textblob import TextBlob
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class TextBlobNounParser(ParserBase):
    """
    A concrete implementation of IParser using TextBlob for Natural Language Processing tasks.
    
    This parser leverages TextBlob's functionalities such as noun phrase extraction, 
    sentiment analysis, classification, language translation, and more for parsing texts.
    """
    type: Literal['TextBlobNounParser'] = 'TextBlobNounParser'
    
    def __init__(self, **kwargs):
        import nltk
        nltk.download('punkt')
        super().__init__(**kwargs)
        
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input data using TextBlob to perform basic NLP tasks 
        and returns a list of documents with the parsed information.
        
        Parameters:
        - data (Union[str, Any]): The input data to parse, expected to be text data for this parser.
        
        Returns:
        - List[IDocument]: A list of documents with metadata generated from the parsing process.
        """
        # Ensure the data is a string
        if not isinstance(data, str):
            raise ValueError("TextBlobParser expects a string as input data.")
        
        # Use TextBlob for NLP tasks
        blob = TextBlob(data)
        
        # Extracts noun phrases to demonstrate one of TextBlob's capabilities. 
        # In practice, this parser could be expanded to include more sophisticated processing.
        noun_phrases = list(blob.noun_phrases)
        
        # Example: Wrap the extracted noun phrases into an IDocument instance
        # In real scenarios, you might want to include more details, like sentiment, POS tags, etc.
        document = Document(content=data, metadata={"noun_phrases": noun_phrases})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/TextBlobSentenceParser.py

from textblob import TextBlob
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase


class TextBlobSentenceParser(ParserBase):
    """
    A parser that leverages TextBlob to break text into sentences.

    This parser uses the natural language processing capabilities of TextBlob
    to accurately identify sentence boundaries within large blocks of text.
    """
    type: Literal['TextBlobSentenceParser'] = 'TextBlobSentenceParser'
    
    def __init__(self, **kwargs):
        import nltk
        nltk.download('punkt')
        super().__init__(**kwargs)

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input text into sentence-based document chunks using TextBlob.

        Args:
            data (Union[str, Any]): The input text to be parsed.

        Returns:
            List[IDocument]: A list of IDocument instances, each representing a sentence.
        """
        # Ensure the input is a string
        if not isinstance(data, str):
            data = str(data)

        # Utilize TextBlob for sentence tokenization
        blob = TextBlob(data)
        sentences = blob.sentences

        # Create a document instance for each sentence
        documents = [
            Document(content=str(sentence), metadata={'parser': 'TextBlobSentenceParser'})
            for index, sentence in enumerate(sentences)
        ]

        return documents

```

```swarmauri/standard/parsers/concrete/URLExtractorParser.py

import re
from urllib.parse import urlparse
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class URLExtractorParser(ParserBase):
    """
    A concrete implementation of IParser that extracts URLs from text.
    
    This parser scans the input text for any URLs and creates separate
    documents for each extracted URL. It utilizes regular expressions
    to identify URLs within the given text.
    """
    type: Literal['URLExtractorParser'] = 'URLExtractorParser'

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parse input data (string) and extract URLs, each URL is then represented as a document.
        
        Parameters:
        - data (Union[str, Any]): The input data to be parsed for URLs.
        
        Returns:
        - List[IDocument]: A list of documents, each representing an extracted URL.
        """
        if not isinstance(data, str):
            raise ValueError("URLExtractorParser expects input data to be of type str.")

        # Regular expression for finding URLs
        url_regex = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        
        # Find all matches in the text
        urls = re.findall(url_regex, data)
        
        # Create a document for each extracted URL
        documents = [Document(content=url, metadata={"source": "URLExtractor"}) for i, url in enumerate(urls)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/XMLParser.py

import xml.etree.ElementTree as ET
from typing import List, Union, Any, Literal

from pydantic import Field
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class XMLParser(ParserBase):
    """
    A parser that extracts information from XML data and converts it into IDocument objects.
    This parser assumes a simple use-case where each targeted XML element represents a separate document.
    """
    element_tag: str = Field(default="root")
    type: Literal['XMLParser'] = 'XMLParser'

    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses XML data and converts elements with the specified tag into IDocument instances.

        Parameters:
        - data (Union[str, Any]): The XML data as a string to be parsed.

        Returns:
        - List[IDocument]: A list of IDocument instances created from the XML elements.
        """
        if isinstance(data, str):
            root = ET.fromstring(data)  # Parse the XML string into an ElementTree element
        else:
            raise TypeError("Data for XMLParser must be a string containing valid XML.")

        documents = []
        for element in root.findall(self.element_tag):
            # Extracting content and metadata from each element
            content = "".join(element.itertext())  # Get text content
            metadata = {child.tag: child.text for child in element}  # Extract child elements as metadata

            # Create a Document instance for each element
            doc = Document(content=content, metadata=metadata)
            documents.append(doc)

        return documents

```

```swarmauri/standard/parsers/concrete/BERTEmbeddingParser.py

from typing import List, Union, Any, Literal
from transformers import BertTokenizer, BertModel
import torch
from pydantic import PrivateAttr
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class BERTEmbeddingParser(ParserBase):
    """
    A parser that transforms input text into document embeddings using BERT.
    
    This parser tokenizes the input text, passes it through a pre-trained BERT model,
    and uses the resulting embeddings as the document content.
    """
    parser_model_name: str = 'bert-base-uncased'
    _model: Any = PrivateAttr()
    type: Literal['BERTEmbeddingParser'] = 'BERTEmbeddingParser'

    def __init__(self, **kwargs):
        """
        Initializes the BERTEmbeddingParser with a specific BERT model.
        
        Parameters:
        - model_name (str): The name of the pre-trained BERT model to use.
        """
        super().__init__(**kwargs)
        self.tokenizer = BertTokenizer.from_pretrained(self.parser_model_name)
        self._model = BertModel.from_pretrained(self.parser_model_name)
        self._model.eval()  # Set model to evaluation mode

    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Tokenizes input data and generates embeddings using a BERT model.

        Parameters:
        - data (Union[str, Any]): Input data, expected to be a single string or batch of strings.

        Returns:
        - List[IDocument]: A list containing a single IDocument instance with BERT embeddings as content.
        """
        
        # Tokenization
        inputs = self.tokenizer(data, return_tensors='pt', padding=True, truncation=True, max_length=512)

        # Generate embeddings
        with torch.no_grad():
            outputs = self._model(**inputs)

        # Use the last hidden state as document embeddings (batch_size, sequence_length, hidden_size)
        embeddings = outputs.last_hidden_state
        
        # Convert to list of numpy arrays
        embeddings = embeddings.detach().cpu().numpy()
        
        # For simplicity, let's consider the mean of embeddings across tokens to represent the document
        doc_embeddings = embeddings.mean(axis=1)
        
        # Creating document object(s)
        documents = [Document(doc_id=str(i), content=emb, metadata={"source": "BERTEmbeddingParser"}) for i, emb in enumerate(doc_embeddings)]
        
        return documents

```

```swarmauri/standard/prompts/__init__.py



```

```swarmauri/standard/prompts/base/__init__.py



```

```swarmauri/standard/prompts/base/PromptMatrixBase.py

from typing import List, Tuple, Optional, Any, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPromptMatrix import IPromptMatrix

class PromptMatrixBase(IPromptMatrix, ComponentBase):
    matrix: List[List[str]] = []
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value)
    type: Literal['PromptMatrixBase'] = 'PromptMatrixBase'    

    @property
    def shape(self) -> Tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt matrix."""
        if self.matrix:
            return len(self.matrix), len(self.matrix[0])
        return 0, 0

    def add_prompt_sequence(self, sequence: List[Optional[str]]) -> None:
        if not self.matrix or (self.matrix and len(sequence) == len(self.matrix[0])):
            self.matrix.append(sequence)
        else:
            raise ValueError("Sequence length does not match the prompt matrix dimensions.")

    def remove_prompt_sequence(self, index: int) -> None:
        if 0 <= index < len(self.matrix):
            self.matrix.pop(index)
        else:
            raise IndexError("Index out of range.")

    def get_prompt_sequence(self, index: int) -> List[Optional[str]]:
        if 0 <= index < len(self._matrix):
            return self.matrix[index]
        else:
            raise IndexError("Index out of range.")

    def show(self) -> List[List[Optional[str]]]:
        return self.matrix

```

```swarmauri/standard/prompts/base/PromptBase.py

from typing import Optional, Literal
from pydantic import ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPrompt import IPrompt

class PromptBase(IPrompt, ComponentBase):
    """
    The ChatPrompt class represents a simple, chat-like prompt system where a 
    message can be set and retrieved as needed. It's particularly useful in 
    applications involving conversational agents, chatbots, or any system that 
    requires dynamic text-based interactions.
    """
    prompt: str = ""
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptBase'] = 'PromptBase'

    def __call__(self):
        """
        Enables the instance to be callable, allowing direct retrieval of the message. 
        This method facilitates intuitive access to the prompt's message, mimicking callable 
        behavior seen in functional programming paradigms.
        
        Returns:
        - str: The current message stored in the prompt.
        """
        return self.prompt

    def set_prompt(self, prompt: str):
        """
        Updates the internal message of the chat prompt. This method provides a way to change 
        the content of the prompt dynamically, reflecting changes in the conversational context 
        or user inputs.
        
        Parameters:
        - message (str): The new message to set for the prompt.
        """
        self.prompt = prompt

```

```swarmauri/standard/prompts/base/PromptTemplateBase.py

from typing import Dict, List, Union, Optional, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate

class PromptTemplateBase(IPrompt, ITemplate, ComponentBase):
    """
    A class for generating prompts based on a template and variables.
    Implements the IPrompt for generating prompts and ITemplate for template manipulation.
    """

    template: str = ""
    variables: Union[List[Dict[str, str]], Dict[str,str]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptTemplateBase'] = 'PromptTemplateBase'

    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.
        """
        self.template = template

    def set_variables(self, variables: Dict[str, str]) -> None:
        """
        Sets or updates the variables to be substituted into the template.
        """
        self.variables = variables

    def generate_prompt(self, variables: Dict[str, str] = None) -> str:
        variables = variables or self.variables
        return self.template.format(**variables)

    def __call__(self, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Generates a prompt using the current template and provided keyword arguments for substitution.
        """
        variables = variables if variables else self.variables
        return self.generate_prompt(variables)

```

```swarmauri/standard/prompts/base/PromptGeneratorBase.py

from typing import Dict, List, Generator, Any, Union, Optional, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate


class PromptGeneratorBase(IPrompt, ITemplate, ComponentBase):
    """
    A class that generates prompts based on a template and a list of variable sets.
    It implements the IPrompt and ITemplate interfaces.
    """

    template: str = ""
    variables: Union[List[Dict[str, Any]], Dict[str, Any]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptGeneratorBase'] = 'PromptGeneratorBase'

    def set_template(self, template: str) -> None:
        self.template = template

    def set_variables(self, variables: List[Dict[str, Any]]) -> None:
        self.variables = variables

    def generate_prompt(self, variables: Dict[str, Any]) -> str:
        """
        Generates a prompt using the provided variables if any
        else uses the next variables set in the list.
        """
        variables = variables if variables else self.variables.pop(0) if self.variables else {}
        return self.template.format(**variables)

    def __call__(self) -> Generator[str, None, None]:
        """
        Returns a generator that yields prompts constructed from the template and 
        each set of variables in the variables list.
        """
        for variables_set in self.variables:
            yield self.generate_prompt(variables_set)
        self.variables = []

```

```swarmauri/standard/prompts/concrete/__init__.py



```

```swarmauri/standard/prompts/concrete/Prompt.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptBase import PromptBase

class Prompt(PromptBase):
    type: Literal['Prompt'] = 'Prompt'

```

```swarmauri/standard/prompts/concrete/PromptTemplate.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptTemplateBase import PromptTemplateBase

class PromptTemplate(PromptTemplateBase):
    type: Literal['PromptTemplate'] = 'PromptTemplate'

```

```swarmauri/standard/prompts/concrete/PromptGenerator.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptGeneratorBase import PromptGeneratorBase

class PromptGenerator(PromptGeneratorBase):
    type: Literal['PromptGenerator'] = 'PromptGenerator'

```

```swarmauri/standard/prompts/concrete/PromptMatrix.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptMatrixBase import PromptMatrixBase

class PromptMatrix(PromptMatrixBase):
    type: Literal['PromptMatrix'] = 'PromptMatrix'

```

```swarmauri/standard/swarms/__init__.py



```

```swarmauri/standard/swarms/base/__init__.py



```

```swarmauri/standard/swarms/base/SwarmComponentBase.py

from swarmauri.core.swarms.ISwarmComponent import ISwarmComponent

class SwarmComponentBase(ISwarmComponent):
    """
    Interface for defining basics of any component within the swarm system.
    """
    def __init__(self, key: str, name: str, superclass: str, module: str, class_name: str, args=None, kwargs=None):
        self.key = key
        self.name = name
        self.superclass = superclass
        self.module = module
        self.class_name = class_name
        self.args = args or []
        self.kwargs = kwargs or {}
    

```

```swarmauri/standard/swarms/concrete/__init__.py



```

```swarmauri/standard/swarms/concrete/SimpleSwarmFactory.py

import json
import pickle
from typing import List
from swarmauri.core.chains.ISwarmFactory import (
    ISwarmFactory , 
    CallableChainItem, 
    AgentDefinition, 
    FunctionDefinition
)
class SimpleSwarmFactory(ISwarmFactory):
    def __init__(self):
        self.swarms = []
        self.callable_chains = []

    def create_swarm(self, agents=[]):
        swarm = {"agents": agents}
        self.swarms.append(swarm)
        return swarm

    def create_agent(self, agent_definition: AgentDefinition):
        # For simplicity, agents are stored in a list
        # Real-world usage might involve more sophisticated management and instantiation based on type and configuration
        agent = {"definition": agent_definition._asdict()}
        self.agents.append(agent)
        return agent

    def create_callable_chain(self, chain_definition: List[CallableChainItem]):
        chain = {"definition": [item._asdict() for item in chain_definition]}
        self.callable_chains.append(chain)
        return chain

    def register_function(self, function_definition: FunctionDefinition):
        if function_definition.identifier in self.functions:
            raise ValueError(f"Function {function_definition.identifier} is already registered.")
        
        self.functions[function_definition.identifier] = function_definition
    
    def export_configuration(self, format_type: str = 'json'):
        # Now exporting both swarms and callable chains
        config = {"swarms": self.swarms, "callable_chains": self.callable_chains}
        if format_type == "json":
            return json.dumps(config)
        elif format_type == "pickle":
            return pickle.dumps(config)

    def load_configuration(self, config_data, format_type: str = 'json'):
        # Loading both swarms and callable chains
        config = json.loads(config_data) if format_type == "json" else pickle.loads(config_data)
        self.swarms = config.get("swarms", [])
        self.callable_chains = config.get("callable_chains", [])

```

```swarmauri/standard/toolkits/__init__.py



```

```swarmauri/standard/toolkits/base/__init__.py



```

```swarmauri/standard/toolkits/base/ToolkitBase.py

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.toolkits.IToolkit import IToolkit



class ToolkitBase(IToolkit, ComponentBase):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    tools: Dict[str, SubclassUnion[ToolBase]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.TOOLKIT.value, frozen=True)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolkitBase'] = 'ToolkitBase'

    def get_tools(self, 
                   include: Optional[List[str]] = None, 
                   exclude: Optional[List[str]] = None,
                   by_alias: bool = False, 
                   exclude_unset: bool = False,
                   exclude_defaults: bool = False, 
                   exclude_none: bool = False
                   ) -> Dict[str, SubclassUnion[ToolBase]]:
            """
            List all tools in the toolkit with options to include or exclude specific fields.
    
            Parameters:
                include (List[str], optional): Fields to include in the returned dictionary.
                exclude (List[str], optional): Fields to exclude from the returned dictionary.
    
            Returns:
                Dict[str, SubclassUnion[ToolBase]]: A dictionary of tools with specified fields included or excluded.
            """
            return [tool.model_dump(include=include, exclude=exclude, by_alias=by_alias,
                                   exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, 
                                    exclude_none=exclude_none) for name, tool in self.tools.items()]

    def add_tools(self, tools: Dict[str, SubclassUnion[ToolBase]]) -> None:
        """
        Add multiple tools to the toolkit.

        Parameters:
            tools (Dict[str, Tool]): A dictionary of tool objects keyed by their names.
        """
        self.tools.update(tools)

    def add_tool(self, tool: SubclassUnion[ToolBase])  -> None:
        """
        Add a single tool to the toolkit.

        Parameters:
            tool (Tool): The tool instance to be added to the toolkit.
        """
        self.tools[tool.name] = tool

    def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to be removed from the toolkit.
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def get_tool_by_name(self, tool_name: str) -> SubclassUnion[ToolBase]:
        """
        Get a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to retrieve.

        Returns:
            Tool: The tool instance with the specified name.
        """
        if tool_name in self.tools:
            return self.tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def __len__(self) -> int:
        """
        Returns the number of tools in the toolkit.

        Returns:
            int: The number of tools in the toolkit.
        """
        return len(self.tools)

```

```swarmauri/standard/toolkits/concrete/__init__.py



```

```swarmauri/standard/toolkits/concrete/Toolkit.py

from typing import Literal
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase

class Toolkit(ToolkitBase):
    type: Literal['Toolkit'] = 'Toolkit'

```

```swarmauri/standard/tools/__init__.py



```

```swarmauri/standard/tools/base/__init__.py



```

```swarmauri/standard/tools/base/ToolBase.py

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.standard.tools.concrete.Parameter import Parameter
from swarmauri.core.tools.ITool import ITool


class ToolBase(ITool, ComponentBase, ABC):
    name: str
    description: Optional[str] = None
    parameters: List[Parameter] = Field(default_factory=list)
    resource: Optional[str] =  Field(default=ResourceTypes.TOOL.value)
    type: Literal['ToolBase'] = 'ToolBase'
    
    def call(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the __call__ method.")


   # #def __getstate__(self):
        # return {'type': self.type, 'function': self.function}


    #def __iter__(self):
    #    yield ('type', self.type)
    #    yield ('function', self.function)

    # @property
    # def function(self):
    #     # Dynamically constructing the parameters schema
    #     properties = {}
    #     required = []

    #     for param in self.parameters:
    #         properties[param.name] = {
    #             "type": param.type,
    #             "description": param.description,
    #         }
    #         if param.enum:
    #             properties[param.name]['enum'] = param.enum

    #         if param.required:
    #             required.append(param.name)

    #     function = {
    #         "name": self.name,
    #         "description": self.description,
    #         "parameters": {
    #             "type": "object",
    #             "properties": properties,
    #         }
    #     }
        
    #     if required:  # Only include 'required' if there are any required parameters
    #         function['parameters']['required'] = required
    #     return function

   # def as_dict(self):
    #    #return asdict(self)
   #     return {'type': self.type, 'function': self.function}

```

```swarmauri/standard/tools/base/ParameterBase.py

from typing import Optional, List, Any
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.tools.IParameter import IParameter


class ParameterBase(IParameter, ComponentBase):
    name: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    resource: Optional[str] =  Field(default=ResourceTypes.PARAMETER.value)
    type: str # THIS DOES NOT USE LITERAL


```

```swarmauri/standard/tools/concrete/__init__.py



```

```swarmauri/standard/tools/concrete/TestTool.py

from typing import List, Literal
from pydantic import Field
import subprocess as sp
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class TestTool(ToolBase):
    version: str = "1.0.0"
        
    # Define the parameters required by the tool
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="program",
            type="string",
            description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
            required=True,
            enum=["notepad", "calc", "mspaint"]
        )
    ])
    name: str = 'TestTool'
    description: str = "This opens a program based on the user's request."
    type: Literal['TestTool'] = 'TestTool'

    def __call__(self, program) -> str:
        # sp.check_output(program)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Program Opened: {program}"


```

```swarmauri/standard/tools/concrete/Parameter.py

from swarmauri.standard.tools.base.ParameterBase import ParameterBase

class Parameter(ParameterBase):
    pass

```

```swarmauri/standard/tools/concrete/CodeInterpreterTool.py

import sys
import io
from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 


class CodeInterpreterTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
            Parameter(
                name="user_code",
                type="string",
                description=("Executes the provided Python code snippet in a secure sandbox environment. "
                             "This tool is designed to interpret the execution of the python code snippet."
                             "Returns the output"),
                required=True
            )
        ])
    name: str = 'CodeInterpreterTool'
    description: str = "Executes provided Python code and captures its output."
    type: Literal['CodeInterpreterTool'] = 'CodeInterpreterTool'

    def __call__(self, user_code: str) -> str:
        """
        Executes the provided user code and captures its stdout output.
        
        Parameters:
            user_code (str): Python code to be executed.
        
        Returns:
            str: Captured output or error message from the executed code.
        """
        return self.execute_code(user_code)
    
    def execute_code(self, user_code: str) -> str:
        """
        Executes the provided user code and captures its stdout output.

        Args:
            user_code (str): Python code to be executed.

        Returns:
            str: Captured output or error message from the executed code.
        """
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            # Note: Consider security implications of using 'exec'
            builtins = globals().copy()
            exec(user_code, builtins)
            sys.stdout = old_stdout
            captured_output = redirected_output.getvalue()
            return str(captured_output)
        except Exception as e:
            sys.stdout = old_stdout
            return f"An error occurred: {str(e)}"

```

```swarmauri/standard/tools/concrete/CalculatorTool.py

from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter

class CalculatorTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="operation",
            type="string",
            description="The arithmetic operation to perform ('add', 'subtract', 'multiply', 'divide').",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        ),
        Parameter(
            name="x",
            type="number",
            description="The left operand for the operation.",
            required=True
        ),
        Parameter(
            name="y",
            type="number",
            description="The right operand for the operation.",
            required=True
        )
    ])
    name: str = 'CalculatorTool'
    description: str = "Performs basic arithmetic operations."
    type: Literal['CalculatorTool'] = 'CalculatorTool'

    def __call__(self, operation: str, x: float, y: float) -> str:
        try:
            if operation == "add":
                result = x + y
            elif operation == "subtract":
                result = x - y
            elif operation == "multiply":
                result = x * y
            elif operation == "divide":
                if y == 0:
                    return "Error: Division by zero."
                result = x / y
            else:
                return "Error: Unknown operation."
            return str(result)
        except Exception as e:
            return f"An error occurred: {str(e)}"


```

```swarmauri/standard/tools/concrete/ImportMemoryModuleTool.py

import sys
import types
import importlib
from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class ImportMemoryModuleTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
            Parameter(
                name="name",
                type="string",
                description="Name of the new module.",
                required=True
            ),
            Parameter(
                name="code",
                type="string",
                description="Python code snippet to include in the module.",
                required=True
            ),
            Parameter(
                name="package_path",
                type="string",
                description="Dot-separated package path where the new module should be inserted.",
                required=True
            )
        ])
    
    name: str = 'ImportMemoryModuleTool'
    description: str = "Dynamically imports a module from memory into a specified package path."
    type: Literal['ImportMemoryModuleTool'] = 'ImportMemoryModuleTool'

    def __call__(self, name: str, code: str, package_path: str) -> str:
        """
        Dynamically creates a module from a code snippet and inserts it into the specified package path.

        Args:
            name (str): Name of the new module.
            code (str): Python code snippet to include in the module.
            package_path (str): Dot-separated package path where the new module should be inserted.
        """
        # Implementation adapted from the provided snippet
        # Ensure the package structure exists
        current_package = self.ensure_module(package_path)
        
        # Create a new module
        module = types.ModuleType(name)
        
        # Execute code in the context of this new module
        exec(code, module.__dict__)
        
        # Insert the new module into the desired location
        setattr(current_package, name, module)
        sys.modules[package_path + '.' + name] = module
        return f"{name} has been successfully imported into {package_path}"

    @staticmethod
    def ensure_module(package_path: str):
        package_parts = package_path.split('.')
        module_path = ""
        current_module = None

        for part in package_parts:
            if module_path:
                module_path += "." + part
            else:
                module_path = part
                
            if module_path not in sys.modules:
                try:
                    # Try importing the module; if it exists, this will add it to sys.modules
                    imported_module = importlib.import_module(module_path)
                    sys.modules[module_path] = imported_module
                except ImportError:
                    # If the module doesn't exist, create a new placeholder module
                    new_module = types.ModuleType(part)
                    if current_module:
                        setattr(current_module, part, new_module)
                    sys.modules[module_path] = new_module
            current_module = sys.modules[module_path]

        return current_module

```

```swarmauri/standard/tools/concrete/AdditionTool.py

from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter

class AdditionTool(ToolBase):
    version: str = "0.0.1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
            Parameter(
                name="x",
                type="integer",
                description="The left operand",
                required=True
            ),
            Parameter(
                name="y",
                type="integer",
                description="The right operand",
                required=True
            )
        ])

    name: str = 'AdditionTool'
    description: str = "This tool has two numbers together"
    type: Literal['AdditionTool'] = 'AdditionTool'


    def __call__(self, x: int, y: int) -> int:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (int): The first number.
        - y (int): The second number.

        Returns:
        - str: The sum of x and y.
        """
        return str(x + y)

```

```swarmauri/standard/tools/concrete/WeatherTool.py

from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class WeatherTool(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="location",
            type="string",
            description="The location for which to fetch weather information",
            required=True
        ),
        Parameter(
            name="unit",
            type="string",
            description="The unit for temperature ('fahrenheit' or 'celsius')",
            required=True,
            enum=["fahrenheit", "celsius"]
        )
    ])
    name: str = 'WeatherTool'
    description: str = "Fetch current weather info for a location"
    type: Literal['WeatherTool'] = 'WeatherTool'

    def __call__(self, location, unit="fahrenheit") -> str:
        weather_info = (location, unit)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Weather Info: {weather_info}\n"


```

```swarmauri/standard/apis/__init__.py



```

```swarmauri/standard/apis/base/__init__.py



```

```swarmauri/standard/apis/base/README.md



```

```swarmauri/standard/apis/concrete/__init__.py



```

```swarmauri/standard/vector_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/base/VectorStoreBase.py

import json
from abc import ABC, abstractmethod
from typing import List, Optional, Literal
from pydantic import Field, PrivateAttr
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.core.vector_stores.IVectorStore import IVectorStore

class VectorStoreBase(IVectorStore, ComponentBase):
    """
    Abstract base class for document stores, implementing the IVectorStore interface.

    This class provides a standard API for adding, updating, getting, and deleting documents in a vector store.
    The specifics of storing (e.g., in a database, in-memory, or file system) are to be implemented by concrete subclasses.
    """
    documents: List[Document] = []
    _embedder = PrivateAttr()
    _distance = PrivateAttr()
    resource: Optional[str] =  Field(default=ResourceTypes.VECTOR_STORE.value)
    type: Literal['VectorStoreBase'] = 'VectorStoreBase'
    
    @property
    def embedder(self):
        return self._embedder

    @abstractmethod
    def add_document(self, document: Document) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the store.
        """
        pass

    @abstractmethod
    def get_document(self, id: str) -> Optional[Document]:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise, None.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[Document]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """
        pass

    @abstractmethod
    def update_document(self, id: str, updated_document: Document) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """
        pass

    @abstractmethod
    def delete_document(self, id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass

    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store

        """
        self.documents = []
    
    def document_count(self):
        return len(self.documents)
    
    def document_dumps(self) -> str:
        """
        Placeholder
        """
        return json.dumps([each.to_dict() for each in self.documents])

    def document_dump(self, file_path: str) -> None:
        """
        Placeholder
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([each.to_dict() for each in self.documents], 
                f,
                ensure_ascii=False, 
                indent=4)  

    def document_loads(self, json_data: str) -> None:
        """
        Placeholder
        """
        self.documents = [globals()[each['type']].from_dict(each) for each in json.loads(json_data)]

    def document_load(self, file_path: str) -> None:
        """
        Placeholder
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.documents = [globals()[each['type']].from_dict(each) for each in json.load(file_path)]

```

```swarmauri/standard/vector_stores/base/VectorStoreSaveLoadMixin.py

from typing import List
import os
from pydantic import BaseModel
import json
import glob
import importlib 
from swarmauri.core.vector_stores.IVectorStoreSaveLoad import IVectorStoreSaveLoad
from swarmauri.standard.documents.concrete.Document import Document

class VectorStoreSaveLoadMixin(IVectorStoreSaveLoad, BaseModel):
    """
    Base class for vector stores with built-in support for saving and loading
    the vectorizer's model and the documents.
    """
    
    
    def save_store(self, directory_path: str) -> None:
        """
        Saves both the vectorizer's model and the documents.
        """
        # Ensure the directory exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        # Save the vectorizer model
        model_path = os.path.join(directory_path, "embedding_model")
        self._vectorizer.save_model(model_path)
        
        # Save documents
        documents_path = os.path.join(directory_path, "documents.json")
        with open(documents_path, 'w', encoding='utf-8') as f:
            json.dump([each.to_dict() for each in self.documents], 
                f,
                ensure_ascii=False, 
                indent=4)

    
    def load_store(self, directory_path: str) -> None:
        """
        Loads both the vectorizer's model and the documents.
        """
        # Load the vectorizer model
        model_path = os.path.join(directory_path, "embedding_model")
        self.vectorizer.load_model(model_path)
        
        # Load documents
        documents_path = os.path.join(directory_path, "documents.json")
        with open(documents_path, 'r', encoding='utf-8') as f:
            self.documents = [self._load_document(each) for each in json.load(f)]

    def _load_document(self, data):
        document_type = data.pop("type") 
        if document_type:
            module = importlib.import_module(f"swarmauri.standard.documents.concrete.{document_type}")
            document_class = getattr(module, document_type)
            document = document_class.from_dict(data)
            return document
        else:
            raise ValueError("Unknown document type")

    def save_parts(self, directory_path: str, chunk_size: int = 10485760) -> None:
        """
        Splits the file into parts if it's too large and saves those parts individually.
        """
        file_number = 1
        model_path = os.path.join(directory_path, "embedding_model")
        parts_directory = os.path.join(directory_path, "parts")
        
        if not os.path.exists(parts_directory):
            os.makedirs(parts_directory)



        with open(f"{model_path}/model.safetensors", 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                with open(f"{parts_directory}/model.safetensors.part{file_number:03}", 'wb') as chunk_file:
                    chunk_file.write(chunk)
                file_number += 1
                chunk = f.read(chunk_size)

        # Split the documents into parts and save them
        documents_dir = os.path.join(directory_path, "documents")

        self._split_json_file(directory_path, chunk_size=chunk_size)


    def _split_json_file(self, directory_path: str, max_records=100, chunk_size: int = 10485760):    
        # Read the input JSON file
        combined_documents_file_path = os.path.join(directory_path, "documents.json")

        # load the master JSON file
        with open(combined_documents_file_path , 'r') as file:
            data = json.load(file)

        # Set and Create documents parts folder if it does not exist
        documents_dir = os.path.join(directory_path, "documents")
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        current_batch = []
        file_index = 1
        current_size = 0
        
        for record in data:
            current_batch.append(record)
            current_size = len(json.dumps(current_batch).encode('utf-8'))
            
            # Check if current batch meets the splitting criteria
            if len(current_batch) >= max_records or current_size >= chunk_size:
                # Write current batch to a new file
                output_file = f'document_part_{file_index}.json'
                output_file = os.path.join(documents_dir, output_file)
                with open(output_file, 'w') as outfile:
                    json.dump(current_batch, outfile)
                
                # Prepare for the next batch
                current_batch = []
                current_size = 0
                file_index += 1

        # Check if there's any remaining data to be written
        if current_batch:
            output_file = f'document_part_{file_index}.json'
            output_file = os.path.join(documents_dir, output_file)
            with open(output_file, 'w') as outfile:
                json.dump(current_batch, outfile)

    def load_parts(self, directory_path: str, file_pattern: str = '*.part*') -> None:
        """
        Combines file parts from a directory back into a single file and loads it.
        """
        model_path = os.path.join(directory_path, "embedding_model")
        parts_directory = os.path.join(directory_path, "parts")
        output_file_path = os.path.join(model_path, "model.safetensors")

        parts = sorted(glob.glob(os.path.join(parts_directory, file_pattern)))
        with open(output_file_path, 'wb') as output_file:
            for part in parts:
                with open(part, 'rb') as file_part:
                    output_file.write(file_part.read())

        # Load the combined_model now        
        model_path = os.path.join(directory_path, "embedding_model")
        self._vectorizer.load_model(model_path)

        # Load document files
        self._load_documents(directory_path)
        

    def _load_documents(self, directory_path: str) -> None:
        """
        Loads the documents from parts stored in the given directory.
        """
        part_paths = glob.glob(os.path.join(directory_path, "documents/*.json"))
        for part_path in part_paths:
            with open(part_path, "r") as f:
                part_documents = json.load(f)
                for document_data in part_documents:
                    document_type = document_data.pop("type")
                    document_module = importlib.import_module(f"swarmauri.standard.documents.concrete.{document_type}")
                    document_class = getattr(document_module, document_type)
                    document = document_class.from_dict(document_data)
                    self.documents.append(document)

```

```swarmauri/standard/vector_stores/base/VectorStoreRetrieveMixin.py

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.core.vector_stores.IVectorStoreRetrieve import IVectorStoreRetrieve


class VectorStoreRetrieveMixin(IVectorStoreRetrieve, BaseModel):
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/standard/vector_stores/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/concrete/TfidfVectorStore.py

from typing import List, Union, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.TfidfEmbedding import TfidfEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    

class TfidfVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['TfidfVectorStore'] = 'TfidfVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = TfidfEmbedding()
        self._distance = CosineDistance()
        self.documents = []
      

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None

    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != id]
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def update_document(self, id: str, updated_document: Document) -> None:
        for i, document in enumerate(self.documents):
            if document.id == id:
                self.documents[i] = updated_document
                break

        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        documents = [query]
        documents.extend([doc.content for doc in self.documents])
        transform_matrix = self._embedder.fit_transform(documents)
        
        # The inferred vector is the last vector in the transformed_matrix
        # The rest of the matrix is what we are comparing
        distances = self._distance.distances(transform_matrix[-1], transform_matrix[:-1])  

        # Get the indices of the top_k most similar (least distant) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]



```

```swarmauri/standard/vector_stores/concrete/Doc2VecVectorStore.py

from typing import List, Union, Literal
from pydantic import PrivateAttr

from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.TfidfEmbedding import TfidfEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    


class Doc2VecVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['Doc2VecVectorStore'] = 'Doc2VecVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = TfidfEmbedding()
        self._distance = CosineDistance()
      

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None

    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != id]
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def update_document(self, id: str, updated_document: Document) -> None:
        for i, document in enumerate(self.documents):
            if document.id == id:
                self.documents[i] = updated_document
                break

        # Recalculate TF-IDF matrix for the current set of documents
        self._embedding.fit([doc.content for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        documents = [query]
        documents.extend([doc.content for doc in self.documents])
        transform_matrix = self._embedder.fit_transform(documents)

        # The inferred vector is the last vector in the transformed_matrix
        # The rest of the matrix is what we are comparing
        distances = self._distance.distances(transform_matrix[-1], transform_matrix[:-1])  

        # Get the indices of the top_k most similar (least distant) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/vector_stores/concrete/MlmVectorStore.py

from typing import List, Union, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.MlmEmbedding import MlmEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    

class MlmVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['MlmVectorStore'] = 'MlmVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = MlmEmbedding()
        self._distance = CosineDistance()
        self.documents: List[Document] = []   

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self._embedder.fit_transform(documents_text)

        embedded_documents = [Document(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count])

        for _count, _d in enumerate(self.documents) if _d.content]

        self.documents = embedded_documents

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self._embedder.fit_transform(documents_text)

        embedded_documents = [Document(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count]) for _count, _d in enumerate(self.documents) 
            if _d.content]

        self.documents = embedded_documents

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None
        
    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != id]

    def update_document(self, id: str) -> None:
        raise NotImplementedError('Update_document not implemented on MLMVectorStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._embedder.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self._distance.distances(query_vector, document_vectors)
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/standard/vector_stores/concrete/SpatialDocVectorStore.py

from typing import List, Union, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.SpatialDocEmbedding import SpatialDocEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    


class SpatialDocVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['SpatialDocVectorStore'] = 'SpatialDocVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = SpatialDocEmbedding()  # Assuming this is already implemented
        self._distance = CosineDistance()
        self.documents: List[Document] = []

    def add_document(self, document: Document) -> None:
        self.add_documents([document])  # Reuse the add_documents logic for batch processing

    def add_documents(self, documents: List[Document]) -> None:
        chunks = [doc.content for doc in documents]
        # Prepare a list of metadata dictionaries for each document based on the required special tokens
        metadata_list = [{ 
            'dir': doc.metadata.get('dir', ''),
            'type': doc.metadata.get('type', ''),
            'section': doc.metadata.get('section', ''),
            'path': doc.metadata.get('path', ''),
            'paragraph': doc.metadata.get('paragraph', ''),
            'subparagraph': doc.metadata.get('subparagraph', ''),
            'chapter': doc.metadata.get('chapter', ''), 
            'title': doc.metadata.get('title', ''),
            'subsection': doc.metadata.get('subsection', ''),
        } for doc in documents]

        # Use vectorize_document to process all documents with their corresponding metadata
        embeddings = self._embedder.vectorize_document(chunks, metadata_list=metadata_list)
        
        # Create Document instances for each document with the generated embeddings
        for doc, embedding in zip(documents, embeddings):
            embedded_doc = Document(
                id=doc.id, 
                content=doc.content, 
                metadata=doc.metadata, 
                embedding=embedding
            )
            self.documents.append(embedded_doc)

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None
        
    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != id]

    def update_document(self, id: str) -> None:
        raise NotImplementedError('Update_document not implemented on SpatialDocVectorStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._embedder.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self._distance.distances(query_vector, document_vectors)
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]



```

```swarmauri/standard/document_stores/__init__.py



```

```swarmauri/standard/document_stores/base/__init__.py



```

```swarmauri/standard/document_stores/base/DocumentStoreBase.py

import json
from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore

class DocumentStoreBase(IDocumentStore, ABC):
    """
    Abstract base class for document stores, implementing the IDocumentStore interface.

    This class provides a standard API for adding, updating, getting, and deleting documents in a store.
    The specifics of storing (e.g., in a database, in-memory, or file system) are to be implemented by concrete subclasses.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[IDocument]:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise, None.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """
        pass

    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass
    
    def document_count(self):
        return len(self.documents)
    
    def dump(self, file_path):
        with open(file_path, 'w') as f:
            json.dumps([each.__dict__ for each in self.documents], f, indent=4)
            
    def load(self, file_path):
        with open(file_path, 'r') as f:
            self.documents = json.loads(f)

```

```swarmauri/standard/document_stores/base/DocumentStoreRetrieveBase.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.document_stores.base.DocumentStoreBase import DocumentStoreBase

class DocumentStoreRetrieveBase(DocumentStoreBase, IDocumentRetrieve, ABC):

        
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/standard/document_stores/concrete/__init__.py



```

```swarmauri/standard/chunkers/__init__.py



```

```swarmauri/standard/chunkers/base/__init__.py



```

```swarmauri/standard/chunkers/base/ChunkerBase.py

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Any, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes

class ChunkerBase(ComponentBase, ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.CHUNKER.value)
    type: Literal['ChunkerBase'] = 'ChunkerBase'
    
    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[Any]:
        pass

```

```swarmauri/standard/chunkers/concrete/__init__.py



```

```swarmauri/standard/chunkers/concrete/SlidingWindowChunker.py

from typing import List, Literal
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase


class SlidingWindowChunker(ChunkerBase):
    """
    A concrete implementation of ChunkerBase that uses sliding window technique
    to break the text into chunks.
    """
    window_size: int = 256
    step_size: int = 256
    overlap: bool = False
    type: Literal['SlidingWindowChunker'] = 'SlidingWindowChunker'
         
    def chunk_text(self, text: str, *args, **kwargs) -> List[str]:
        """
        Splits the input text into chunks based on the sliding window technique.
        
        Parameters:
        - text (str): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks.
        """
        step_size = self.step_size if self.overlap else self.window_size  # Non-overlapping if window size equals step size.


        words = text.split()  # Tokenization by whitespaces. More sophisticated tokenization might be necessary.
        chunks = []
        
        for i in range(0, len(words) - self.window_size + 1, step_size):
            chunk = ' '.join(words[i:i+self.window_size])
            chunks.append(chunk)
        
        return chunks

```

```swarmauri/standard/chunkers/concrete/DelimiterBasedChunker.py

from typing import List, Union, Any, Literal
import re
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class DelimiterBasedChunker(ChunkerBase):
    """
    A concrete implementation of IChunker that splits text into chunks based on specified delimiters.
    """
    delimiters: List[str] = ['.', '!', '?']
    type: Literal['DelimiterBasedChunker'] = 'DelimiterBasedChunker'
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Chunks the given text based on the delimiters specified during initialization.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.

        Returns:
        - List[str]: A list of text chunks split based on the specified delimiters.
        """
        delimiter_pattern = f"({'|'.join(map(re.escape, self.delimiters))})"
        
        # Split the text based on the delimiter pattern, including the delimiters in the result
        chunks = re.split(delimiter_pattern, text)
        
        # Combine delimiters with the preceding text chunk since re.split() separates them
        combined_chunks = []
        for i in range(0, len(chunks), 2):  # Step by 2 to process text chunk with its following delimiter
            combined_chunks.append(chunks[i] + (chunks[i + 1] if i + 1 < len(chunks) else ''))

        # Remove whitespace
        combined_chunks = [chunk.strip() for chunk in combined_chunks]
        return combined_chunks

```

```swarmauri/standard/chunkers/concrete/FixedLengthChunker.py

from typing import List, Union, Any, Literal
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class FixedLengthChunker(ChunkerBase):
    """
    Concrete implementation of ChunkerBase that divides text into fixed-length chunks.
    
    This chunker breaks the input text into chunks of a specified size, making sure 
    that each chunk has exactly the number of characters specified by the chunk size, 
    except for possibly the last chunk.
    """
    chunk_size: int = 256
    type: Literal['FixedLengthChunker'] = 'FixedLengthChunker'
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Splits the input text into fixed-length chunks.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks, each of a specified fixed length.
        """
        # Check if the input is a string, if not, attempt to convert to a string.
        if not isinstance(text, str):
            text = str(text)
        
        # Using list comprehension to split text into chunks of fixed size
        chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        
        return chunks

```

```swarmauri/standard/chunkers/concrete/SentenceChunker.py

from typing import Literal
import re
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class SentenceChunker(ChunkerBase):
    """
    A simple implementation of the ChunkerBase to chunk text into sentences.
    
    This class uses basic punctuation marks (., !, and ?) as indicators for sentence boundaries.
    """
    type: Literal['SentenceChunker'] = 'SentenceChunker'
    
    def chunk_text(self, text, *args, **kwargs):
        """
        Chunks the given text into sentences using basic punctuation.

        Args:
            text (str): The input text to be chunked into sentences.
        
        Returns:
            List[str]: A list of sentence chunks.
        """
        # Split text using a simple regex pattern that looks for periods, exclamation marks, or question marks.
        # Note: This is a very simple approach and might not work well with abbreviations or other edge cases.
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s'
        sentences = re.split(sentence_pattern, text)
        
        # Filter out any empty strings that may have resulted from the split operation
        sentences = [sentence.strip() for sentence in sentences if sentence]
        
        return sentences

```

```swarmauri/standard/chunkers/concrete/MdSnippetChunker.py

from typing import List, Union, Any, Optional, Literal
import re
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class MdSnippetChunker(ChunkerBase):
    language: Optional[str] = None
    type: Literal['MdSnippetChunker'] = 'MdSnippetChunker'
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[tuple]:
        """
        Extracts paired comments and code blocks from Markdown content based on the 
        specified programming language.
        """
        if self.language:
            # If language is specified, directly extract the corresponding blocks
            pattern = fr'```{self.language}\s*(.*?)```'
            scripts = re.findall(pattern, text, re.DOTALL)
            comments_temp = re.split(pattern, text, flags=re.DOTALL)
        else:
            # Extract blocks and languages dynamically if no specific language is provided
            scripts = []
            languages = []
            for match in re.finditer(r'```(\w+)?\s*(.*?)```', text, re.DOTALL):
                if match.group(1) is not None:  # Checks if a language identifier is present
                    languages.append(match.group(1))
                    scripts.append(match.group(2))
                else:
                    languages.append('')  # Default to an empty string if no language is found
                    scripts.append(match.group(2))
            comments_temp = re.split(r'```.*?```', text, flags=re.DOTALL)

        comments = [comment.strip() for comment in comments_temp]

        if text.strip().startswith('```'):
            comments = [''] + comments
        if text.strip().endswith('```'):
            comments.append('')

        if self.language:
            structured_output = [(comments[i], self.language, scripts[i].strip()) for i in range(len(scripts))]
        else:
            structured_output = [(comments[i], languages[i], scripts[i].strip()) for i in range(len(scripts))]

        return structured_output


```

```swarmauri/standard/vectors/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/base/VectorBase.py

from abc import ABC, abstractmethod
from typing import List, Optional, Literal
import json
import numpy as np
from pydantic import Field
from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes

class VectorBase(IVector, ComponentBase):
    value: List[float]
    resource: Optional[str] =  Field(default=ResourceTypes.VECTOR.value, frozen=True)
    type: Literal['VectorBase'] = 'VectorBase'

    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return np.array(self.data)
        
    def __len__(self):
        return len(self.data)


```

```swarmauri/standard/vectors/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/concrete/Vector.py

from typing import Literal
from swarmauri.standard.vectors.base.VectorBase import VectorBase

class Vector(VectorBase):
    type: Literal['Vector'] = 'Vector'

```

```swarmauri/standard/vectors/concrete/VectorProductMixin.py

import numpy as np
from typing import List
from pydantic import BaseModel
from swarmauri.core.vectors.IVectorProduct import IVectorProduct
from swarmauri.standard.vectors.concrete.Vector import Vector

class VectorProductMixin(IVectorProduct, BaseModel):
    def dot_product(self, vector_a: Vector, vector_b: Vector) -> float:
        a = np.array(vector_a.value).flatten()
        b = np.array(vector_b.value).flatten()
        return np.dot(a, b)
    
    def cross_product(self, vector_a: Vector, vector_b: Vector) -> Vector:
        if len(vector_a.value) != 3 or len(vector_b.value) != 3:
            raise ValueError("Cross product is only defined for 3-dimensional vectors")
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        cross = np.cross(a, b)
        return Vector(value=cross.tolist())
    
    def vector_triple_product(self, vector_a: Vector, vector_b: Vector, vector_c: Vector) -> Vector:
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        c = np.array(vector_c.value)
        result = np.cross(a, np.cross(b, c))
        return Vector(value=result.tolist())
    
    def scalar_triple_product(self, vector_a: Vector, vector_b: Vector, vector_c: Vector) -> float:
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        c = np.array(vector_c.value)
        return np.dot(a, np.cross(b, c))

```

```swarmauri/standard/embeddings/__init__.py

#

```

```swarmauri/standard/embeddings/base/__init__.py

#

```

```swarmauri/standard/embeddings/base/EmbeddingBase.py

from typing import Optional, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.embeddings.IVectorize import IVectorize
from swarmauri.core.embeddings.IFeature import IFeature
from swarmauri.core.embeddings.ISaveModel import ISaveModel

class EmbeddingBase(IVectorize, IFeature, ISaveModel, ComponentBase):
    resource: Optional[str] =  Field(default=ResourceTypes.EMBEDDING.value, frozen=True)
    type: Literal['EmbeddingBase'] = 'EmbeddingBase'
        


```

```swarmauri/standard/embeddings/concrete/__init__.py

#

```

```swarmauri/standard/embeddings/concrete/Doc2VecEmbedding.py

from typing import List, Union, Any, Literal
from pydantic import PrivateAttr
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class Doc2VecEmbedding(EmbeddingBase):
    _model = PrivateAttr()
    type: Literal['Doc2VecEmbedding'] = 'Doc2VecEmbedding'    

    def __init__(self, 
                 vector_size: int = 2000, 
                 window: int = 10,
                 min_count: int = 1,
                 workers: int = 5,
                 **kwargs):
        super().__init__(**kwargs)
        self._model = Doc2Vec(vector_size=vector_size, 
                              window=window, 
                              min_count=min_count, 
                              workers=workers)
        

    def extract_features(self) -> List[Any]:
        return list(self._model.wv.key_to_index.keys())

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [TaggedDocument(words=_d.split(), 
            tags=[str(i)]) for i, _d in enumerate(documents)]

        self._model.build_vocab(tagged_data)
        self._model.train(tagged_data, total_examples=self._model.corpus_count, epochs=self._model.epochs)

    def transform(self, documents: List[str]) -> List[Vector]:
        vectors = [self._model.infer_vector(doc.split()) for doc in documents]
        return [Vector(value=vector) for vector in vectors]

    def fit_transform(self, documents: List[str], **kwargs) -> List[Vector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: str) -> Vector:
        vector = self._model.infer_vector(data.split())
        return Vector(value=vector.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the Doc2Vec model to the specified path.
        """
        self._model.save(path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a Doc2Vec model from the specified path.
        """
        self._model = Doc2Vec.load(path)

```

```swarmauri/standard/embeddings/concrete/TfidfEmbedding.py

from typing import List, Union, Any, Literal
import joblib
from pydantic import PrivateAttr
from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer

from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class TfidfEmbedding(EmbeddingBase):
    _model = PrivateAttr()
    _fit_matrix = PrivateAttr()
    type: Literal['TfidfEmbedding'] = 'TfidfEmbedding'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = SklearnTfidfVectorizer()
    
    def extract_features(self):
        return self._model.get_feature_names_out().tolist()

    def fit(self, documents: List[str]) -> None:
        self._fit_matrix = self._model.fit_transform(documents)

    def fit_transform(self, documents: List[str]) -> List[Vector]:
        self._fit_matrix = self._model.fit_transform(documents)
        # Convert the sparse matrix rows into Vector instances
        vectors = [Vector(value=vector.toarray().flatten()) for vector in self._fit_matrix]
        return vectors
    
    def transform(self, data: Union[str, Any], documents: List[str]) -> List[Vector]:
        raise NotImplementedError('Transform not implemented on TFIDFVectorizer.')

    def infer_vector(self, data: str, documents: List[str]) -> Vector:
        documents.append(data)
        tmp_tfidf_matrix = self.transform(documents)
        query_vector = tmp_tfidf_matrix[-1]
        return query_vector

    def save_model(self, path: str) -> None:
        """
        Saves the TF-IDF model to the specified path using joblib.
        """
        joblib.dump(self._model, path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a TF-IDF model from the specified path using joblib.
        """
        self._model = joblib.load(path)

```

```swarmauri/standard/embeddings/concrete/MlmEmbedding.py

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

from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

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

```

```swarmauri/standard/embeddings/concrete/NmfEmbedding.py

import joblib
from typing import List, Any, Literal
from pydantic import PrivateAttr
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class NmfEmbedding(EmbeddingBase):
    n_components: int = 10
    _tfidf_vectorizer = PrivateAttr()
    _model = PrivateAttr()
    feature_names: List[Any] = []
    
    type: Literal['NmfEmbedding'] = 'NmfEmbedding'
    def __init__(self,**kwargs):

        super().__init__(**kwargs)
        # Initialize TF-IDF Vectorizer
        self._tfidf_vectorizer = TfidfVectorizer()
        # Initialize NMF with the desired number of components
        self._model = NMF(n_components=self.n_components)

    def fit(self, data):
        """
        Fit the NMF model to data.

        Args:
            data (Union[str, Any]): The text data to fit.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self._tfidf_vectorizer.fit_transform(data)
        # Fit the NMF model
        self._model.fit(tfidf_matrix)
        # Store feature names
        self.feature_names = self._tfidf_vectorizer.get_feature_names_out()

    def transform(self, data):
        """
        Transform new data into NMF feature space.

        Args:
            data (Union[str, Any]): Text data to transform.

        Returns:
            List[IVector]: A list of vectors representing the transformed data.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self._tfidf_vectorizer.transform(data)
        # Transform TF-IDF matrix into NMF space
        nmf_features = self._model.transform(tfidf_matrix)

        # Wrap NMF features in SimpleVector instances and return
        return [Vector(value=features.tolist()) for features in nmf_features]

    def fit_transform(self, data):
        """
        Fit the model to data and then transform it.
        
        Args:
            data (Union[str, Any]): The text data to fit and transform.

        Returns:
            List[IVector]: A list of vectors representing the fitted and transformed data.
        """
        self.fit(data)
        return self.transform(data)

    def infer_vector(self, data):
        """
        Convenience method for transforming a single data point.
        
        Args:
            data (Union[str, Any]): Single text data to transform.

        Returns:
            IVector: A vector representing the transformed single data point.
        """
        return self.transform([data])[0]
    
    def extract_features(self):
        """
        Extract the feature names from the TF-IDF vectorizer.
        
        Returns:
            The feature names.
        """
        return self.feature_names.tolist()

    def save_model(self, path: str) -> None:
        """
        Saves the NMF model and TF-IDF vectorizer using joblib.
        """
        # It might be necessary to save both tfidf_vectorizer and model
        # Consider using a directory for 'path' or appended identifiers for each model file
        joblib.dump(self._tfidf_vectorizer, f"{path}_tfidf.joblib")
        joblib.dump(self._model, f"{path}_nmf.joblib")

    def load_model(self, path: str) -> None:
        """
        Loads the NMF model and TF-IDF vectorizer from paths using joblib.
        """
        self._tfidf_vectorizer = joblib.load(f"{path}_tfidf.joblib")
        self._model = joblib.load(f"{path}_nmf.joblib")
        # Dependending on your implementation, you might need to refresh the feature_names
        self.feature_names = self._tfidf_vectorizer.get_feature_names_out()

```

```swarmauri/standard/tracing/__init__.py

#

```

```swarmauri/standard/tracing/base/__init__.py

#

```

```swarmauri/standard/tracing/concrete/SimpleTracer.py

from datetime import datetime
import uuid
from typing import Dict, Any, Optional

from swarmauri.core.tracing.ITracer import ITracer
from swarmauri.standard.tracing.concrete.SimpleTraceContext import SimpleTraceContext

class SimpleTracer(ITracer):
    _instance = None  # Singleton instance placeholder

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if SimpleTracer._instance is not None:
            raise RuntimeError("SimpleTracer is a singleton. Use SimpleTracer.instance().")
        self.trace_stack = []

    def start_trace(self, name: str, initial_attributes: Optional[Dict[str, Any]] = None) -> SimpleTraceContext:
        trace_id = str(uuid.uuid4())
        trace_context = SimpleTraceContext(trace_id, name, initial_attributes)
        self.trace_stack.append(trace_context)
        return trace_context

    def end_trace(self):
        if self.trace_stack:
            completed_trace = self.trace_stack.pop()
            completed_trace.close()
            # Example of simply printing the completed trace; in practice, you might log it or store it elsewhere
            print(f"Trace Completed: {completed_trace.name}, Duration: {completed_trace.start_time} to {completed_trace.end_time}, Attributes: {completed_trace.attributes}")

    def annotate_trace(self, key: str, value: Any):
        if not self.trace_stack:
            print("No active trace to annotate.")
            return
        current_trace = self.trace_stack[-1]
        current_trace.add_attribute(key, value)

```

```swarmauri/standard/tracing/concrete/TracedVariable.py

from typing import Any
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer  # Assuming this is the path to the tracer

class TracedVariable:
    """
    Wrapper class to trace multiple changes to a variable within the context manager.
    """
    def __init__(self, name: str, value: Any, tracer: SimpleTracer):
        self.name = name
        self._value = value
        self._tracer = tracer
        self._changes = []  # Initialize an empty list to track changes

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any):
        # Record the change before updating the variable's value
        change_annotation = {"from": self._value, "to": new_value}
        self._changes.append(change_annotation)
        
        # Update the trace by appending the latest change to the list under a single key
        # Note that the key is now constant and does not change with each update
        self._tracer.annotate_trace(key=f"{self.name}_changes", value=self._changes)
        
        self._value = new_value

```

```swarmauri/standard/tracing/concrete/ChainTracer.py

from swarmauri.core.tracing.IChainTracer import IChainTracer
from typing import Callable, List, Tuple, Dict, Any   
        
class ChainTracer(IChainTracer):
    def __init__(self):
        self.traces = []

    def process_chain(self, chain: List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]) -> "ChainTracer":
        """
        Processes each item in the operation chain by executing the specified external function
        with its args and kwargs. Logs starting, annotating, and ending the trace based on tuple position.

        Args:
            chain (List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]): A list where each tuple contains:
                - An external function to execute.
                - A list of positional arguments for the function.
                - A dictionary of keyword arguments for the function.
        """
        for i, (func, args, kwargs) in enumerate(chain):
            # Infer operation type and log
            
            if i == 0:
                operation = "Start"
                self.start_trace(*args, **kwargs)
            elif i == len(chain) - 1:
                operation = "End"
                self.end_trace(*args, **kwargs)
            else:
                operation = "Annotate"
                self.annotate_trace(*args, **kwargs)
                
            # For the actual external function call
            result = func(*args, **kwargs)
            print(f"Function '{func.__name__}' executed with result: {result}")

            self.traces.append((operation, func, args, kwargs, result))

        return self

    def start_trace(self, *args, **kwargs) -> None:
        print(f"Starting trace with args: {args}, kwargs: {kwargs}")
        
    def annotate_trace(self, *args, **kwargs) -> None:
        print(f"Annotating trace with args: {args}, kwargs: {kwargs}")

    def end_trace(self, *args, **kwargs) -> None:
        print(f"Ending trace with args: {args}, kwargs: {kwargs}")

    def show(self) -> None:
        for entry in self.traces:
            print(entry)

```

```swarmauri/standard/tracing/concrete/SimpleTraceContext.py

from datetime import datetime
from typing import Dict, Any, Optional

from swarmauri.core.tracing.ITraceContext import ITraceContext

class SimpleTraceContext(ITraceContext):
    def __init__(self, trace_id: str, name: str, initial_attributes: Optional[Dict[str, Any]] = None):
        self.trace_id = trace_id
        self.name = name
        self.attributes = initial_attributes if initial_attributes else {}
        self.start_time = datetime.now()
        self.end_time = None

    def get_trace_id(self) -> str:
        return self.trace_id

    def add_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def close(self):
        self.end_time = datetime.now()

```

```swarmauri/standard/tracing/concrete/VariableTracer.py

from contextlib import contextmanager

from swarmauri.standard.tracing.concrete.TracedVariable import TracedVariable
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer

# Initialize a global instance of SimpleTracer for use across the application
global_tracer = SimpleTracer()

@contextmanager
def VariableTracer(name: str, initial_value=None):
    """
    Context manager for tracing the declaration, modification, and usage of a variable.
    """
    trace_context = global_tracer.start_trace(name=f"Variable: {name}", initial_attributes={"initial_value": initial_value})
    traced_variable = TracedVariable(name, initial_value, global_tracer)
    
    try:
        yield traced_variable
    finally:
        # Optionally record any final value or state of the variable before it goes out of scope
        global_tracer.annotate_trace(key=f"{name}_final", value={"final_value": traced_variable.value})
        # End the trace, marking the variable's lifecycle
        global_tracer.end_trace()

```

```swarmauri/standard/tracing/concrete/CallableTracer.py

import functools
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer  # Import SimpleTracer from the previously defined path

# Initialize the global tracer object
tracer = SimpleTracer()

def CallableTracer(func):
    """
    A decorator to trace function or method calls, capturing inputs, outputs, and the caller.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Trying to automatically identify the caller details; practical implementations 
        # might need to adjust based on specific requirements or environment.
        caller_info = f"{func.__module__}.{func.__name__}"
        
        # Start a new trace context for this callable
        trace_context = tracer.start_trace(name=caller_info, initial_attributes={'args': args, 'kwargs': kwargs})
        
        try:
            # Call the actual function/method
            result = func(*args, **kwargs)
            tracer.annotate_trace(key="result", value=result)
            return result
        except Exception as e:
            # Optionally annotate the trace with the exception details
            tracer.annotate_trace(key="exception", value=str(e))
            raise  # Re-raise the exception to not interfere with the program's flow
        finally:
            # End the trace after the function call is complete
            tracer.end_trace()
    return wrapper

```

```swarmauri/standard/tracing/concrete/__init__.py



```

```swarmauri/standard/chains/__init__.py



```

```swarmauri/standard/chains/base/__init__.py

#

```

```swarmauri/standard/chains/base/ChainBase.py

from typing import List, Dict, Any, Optional, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChain import IChain
from swarmauri.stanard.chains.concrete.ChainStep import ChainStep
from swarmauri.core.typing import SubclassUnion

class ChainBase(IChain, ComponentBase):
    """
    A base implementation of the IChain interface.
    """
    steps: List[ChainStep] = []
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ChainBase'] = 'ChainBase'

    def add_step(self, step: ChainStep) -> None:
        self.steps.append(step)

    def remove_step(self, step: ChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (ChainStep): The Callable representing the step to remove from the chain.
        """

        raise NotImplementedError('This is not yet implemented')

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError('This is not yet implemented')



```

```swarmauri/standard/chains/base/ChainStepBase.py

from typing import Any, Tuple, Dict, Optional, Union, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep, ComponentBase):
    """
    Represents a single step within an execution chain.
    """
    key: str
    method: SubclassUnion[ToolBase]
    args: Tuple = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    ref: Optional[str] =  Field(default=None)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAINSTEP.value)
    type: Literal['ChainStepBase'] = 'ChainStepBase'

```

```swarmauri/standard/chains/base/PromptContextChainBase.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from pydantic import Field
from collections import defaultdict, deque
import re
import numpy as np


from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.standard.chains.concrete.ChainStep import ChainStep
from swarmauri.standard.chains.base.ChainContextBase import ChainContextBase
from swarmauri.standard.prompts.concrete.PromptMatrix import PromptMatrix
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.core.prompts.IPromptMatrix import IPromptMatrix
from swarmauri.core.chains.IChainDependencyResolver import IChainDependencyResolver

class PromptContextChainBase(IChainDependencyResolver, ChainContextBase, ComponentBase):
    prompt_matrix: PromptMatrix
    agents: List[SubclassUnion[AgentBase]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    llm_kwargs: Dict[str, Any] = Field(default_factory=dict)
    response_matrix: Optional[PromptMatrix] = None
    current_step_index: int = 0
    steps: List[Any] = Field(default_factory=list)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    type: Literal['PromptContextChainBase'] = 'PromptContextChainBase'
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        # Now that the instance is created, we can safely access `prompt_matrix.shape`
        self.response_matrix = PromptMatrix(matrix=[[None for _ in range(self.prompt_matrix.shape[1])] 
                                                    for _ in range(self.prompt_matrix.shape[0])])

    def execute(self, build_dependencies=True) -> None:
        """
        Execute the chain of prompts based on the state of the prompt matrix.
        Iterates through each sequence in the prompt matrix, resolves dependencies, 
        and executes prompts in the resolved order.
        """
        if build_dependencies:
            self.steps = self.build_dependencies()
            self.current_step_index = 0

        while self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            method = step.method
            args = step.args
            ref = step.ref
            result = method(*args)
            self.context[ref] = result
            prompt_index = self._extract_step_number(ref)
            self._update_response_matrix(args[0], prompt_index, result)
            self.current_step_index += 1  # Move to the next step
        else:
            print("All steps have been executed.")

    def execute_next_step(self):
        """
        Execute the next step in the steps list if available.
        """
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            method = step.method
            args = step.args
            ref = step.ref
            result = method(*args)
            self.context[ref] = result
            prompt_index = self._extract_step_number(ref)
            self._update_response_matrix(args[0], prompt_index, result)
            self.current_step_index += 1  # Move to the next step
        else:
            print("All steps have been executed.")

    def _execute_prompt(self, agent_index: int, prompt: str, ref: str):
        """
        Executes a given prompt using the specified agent and updates the response.
        """
        formatted_prompt = prompt.format(**self.context)  # Using context for f-string formatting
        
        agent = self.agents[agent_index]
        # get the unformatted version
        unformatted_system_context = agent.system_context
        # use the formatted version
        agent.system_context = agent.system_context.content.format(**self.context)
        response = agent.exec(formatted_prompt, model_kwargs=self.model_kwargs)
        # reset back to the unformatted version
        agent.system_context = unformatted_system_context

        self.context[ref] = response
        prompt_index = self._extract_step_number(ref)
        self._update_response_matrix(agent_index, prompt_index, response)
        return response

    def _update_response_matrix(self, agent_index: int, prompt_index: int, response: Any):
        self.response_matrix.matrix[agent_index][prompt_index] = response


    def _extract_agent_number(self, text):
        # Regular expression to match the pattern and capture the agent number
        match = re.search(r'\{Agent_(\d+)_Step_\d+_response\}', text)
        if match:
            # Return the captured group, which is the agent number
            return int(match.group(1))
        else:
            # Return None if no match is found
            return None
    
    def _extract_step_number(self, ref):
        # This regex looks for the pattern '_Step_' followed by one or more digits.
        match = re.search(r"_Step_(\d+)_", ref)
        if match:
            return int(match.group(1))  # Convert the extracted digits to an integer
        else:
            return None  # If no match is found, return None
    
    def build_dependencies(self) -> List[ChainStep]:
        """
        Build the chain steps in the correct order by resolving dependencies first.
        """
        steps = []
        
        for i in range(self.prompt_matrix.shape[1]):
            try:
                sequence = np.array(self.prompt_matrix.matrix)[:,i].tolist()
                execution_order = self.resolve_dependencies(sequence=sequence)
                for j in execution_order:
                    prompt = sequence[j]
                    if prompt:
                        ref = f"Agent_{j}_Step_{i}_response"  # Using a unique reference string
                        step = ChainStep(
                            key=f"Agent_{j}_Step_{i}",
                            method=self._execute_prompt,
                            args=[j, prompt, ref],
                            ref=ref
                        )
                        steps.append(step)
            except Exception as e:
                print(str(e))
        return steps

    def resolve_dependencies(self, sequence: List[Optional[str]]) -> List[int]:
        """
        Resolve dependencies within a specific sequence of the prompt matrix.
        
        Args:
            matrix (List[List[Optional[str]]]): The prompt matrix.
            sequence_index (int): The index of the sequence to resolve dependencies for.

        Returns:
            List[int]: The execution order of the agents for the given sequence.
        """
        
        return [x for x in range(0, len(sequence), 1)]

```

```swarmauri/standard/chains/base/ChainContextBase.py

from typing import Any, Callable, Dict, List, Optional, Literal
from pydantic import Field, ConfigDict
import re
from swarmauri.standard.chains.concrete.ChainStep import ChainStep
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainContext import IChainContext

class ChainContextBase(IChainContext, ComponentBase):
    steps: List[ChainStep] = []
    context: Dict = {}
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ChainContextBase'] = 'ChainContextBase'

    def update(self, **kwargs):
        self.context.update(kwargs)

    def get_value(self, key: str) -> Any:
        return self.context.get(key)

    def _resolve_fstring(self, template: str) -> str:
        pattern = re.compile(r'{([^}]+)}')
        def replacer(match):
            expression = match.group(1)
            try:
                return str(eval(expression, {}, self.context))
            except Exception as e:
                print(f"Failed to resolve expression: {expression}. Error: {e}")
                return f"{{{expression}}}"
        return pattern.sub(replacer, template)

    def _resolve_placeholders(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._resolve_fstring(value)
        elif isinstance(value, dict):
            return {k: self._resolve_placeholders(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_placeholders(v) for v in value]
        else:
            return value

    def _resolve_ref(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('$'):
            placeholder = value[1:]
            return placeholder
        return value

```

```swarmauri/standard/chains/concrete/__init__.py



```

```swarmauri/standard/chains/concrete/CallableChain.py

from typing import Any, Callable, List, Dict, Optional
from swarmauri.core.chains.ICallableChain import ICallableChain, CallableDefinition


class CallableChain(ICallableChain):
    
    def __init__(self, callables: Optional[List[CallableDefinition]] = None):
        
        self.callables = callables if callables is not None else []

    def __call__(self, *initial_args, **initial_kwargs):
        result = None
        for func, args, kwargs in self.callables:
            if result is not None:
                # If there was a previous result, use it as the first argument for the next function
                args = [result] + list(args)
            result = func(*args, **kwargs)
        return result
    
    def add_callable(self, func: Callable[[Any], Any], args: List[Any] = None, kwargs: Dict[str, Any] = None) -> None:
        # Add a new callable to the chain
        self.callables.append((func, args or [], kwargs or {}))
    
    def __or__(self, other: "CallableChain") -> "CallableChain":
        if not isinstance(other, CallableChain):
            raise TypeError("Operand must be an instance of CallableChain")
        
        new_chain = CallableChain(self.callables + other.callables)
        return new_chain

```

```swarmauri/standard/chains/concrete/ChainStep.py

from typing import Literal
from swarmauri.standard.chains.base.ChainStepBase import ChainStepBase

class ChainStep(ChainStepBase):
    """
    Represents a single step within an execution chain.
    """
    type: Literal['ChainStep'] = 'ChainStep'

```

```swarmauri/standard/chains/concrete/ContextChain.py

from typing import Any, Dict, List, Callable, Optional, Tuple, Union, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.chains.concrete.ChainStep import ChainStep
from swarmauri.standard.chains.base.ChainContextBase import ChainContextBase
from swarmauri.core.chains.IChain import IChain

class ContextChain(IChain, ChainContextBase):
    """
    Enhanced to support ChainSteps with return parameters, storing return values as instance state variables.
    Implements the IChain interface including get_schema_info and remove_step methods.
    """
    type: Literal['ContextChain'] = 'ContextChain'

    def add_step(self, 
        key: str, 
        method: SubclassUnion[ToolBase],
        args: Tuple = (), 
        kwargs: Dict[str, Any] = {}, 
        ref: Optional[str] = None):

        # Directly store args, kwargs, and optionally a return_key without resolving them
        step = ChainStep(key=key, method=method, args=args, kwargs=kwargs, ref=ref)
        self.steps.append(step)

    def remove_step(self, step: ChainStep) -> None:
        self.steps = [s for s in self._steps if s.key != step.key]

    def execute(self, *args, **kwargs) -> Any:
        # Execute the chain and manage result storage based on return_key
        for step in self.steps:
            resolved_args = [self._resolve_placeholders(arg) for arg in step.args]
            resolved_kwargs = {k: self._resolve_placeholders(v) for k, v in step.kwargs.items() if k != 'ref'}
            result = step.method(*resolved_args, **resolved_kwargs)
            if step.ref:  # step.ref is used here as the return_key analogy
                resolved_ref = self._resolve_ref(step.ref)
                self.context[resolved_ref] = result
                self.update(**{resolved_ref: result})  # Update context with new state value
        return self.context  # or any specific result you intend to return


```

```swarmauri/standard/chains/concrete/PromptContextChain.py

from typing import Literal
from swarmauri.standard.chains.base.PromptContextChainBase import PromptContextChainBase

class PromptContextChain(PromptContextChainBase):
    type: Literal['PromptContextChain'] = 'PromptContextChain'

```

```swarmauri/standard/distances/__init__.py



```

```swarmauri/standard/distances/base/__init__.py



```

```swarmauri/standard/distances/base/DistanceBase.py

from abc import abstractmethod
from numpy.linalg import norm
from typing import List, Optional, Literal
from pydantic import Field
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.vectors.concrete.VectorProductMixin import VectorProductMixin
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes

class DistanceBase(IDistanceSimilarity, VectorProductMixin, ComponentBase):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.DISTANCE.value, frozen=True)
    type: Literal['DistanceBase'] = 'DistanceBase'
    @abstractmethod
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        pass
    
    @abstractmethod
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        pass
       

    @abstractmethod
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        pass
        
    @abstractmethod
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        pass
        

```

```swarmauri/standard/distances/concrete/ChiSquaredDistance.py

from typing import List, Literal

from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase

class ChiSquaredDistance(DistanceBase):
    """
    Implementation of the IDistanceSimilarity interface using Chi-squared distance metric.
    """    
    type: Literal['ChiSquaredDistance'] = 'ChiSquaredDistance'

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Chi-squared distance between two vectors.
        """
        if len(vector_a.value) != len(vector_b.value):
            raise ValueError("Vectors must have the same dimensionality.")

        chi_squared_distance = 0
        for a, b in zip(vector_a.value, vector_b.value):
            if (a + b) != 0:
                chi_squared_distance += (a - b) ** 2 / (a + b)

        return 0.5 * chi_squared_distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute the similarity between two vectors based on the Chi-squared distance.
        """
        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities



```

```swarmauri/standard/distances/concrete/CosineDistance.py

from numpy.linalg import norm
from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase

class CosineDistance(DistanceBase):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
    type: Literal['CosineDistance'] = 'CosineDistance'   
       
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """ 
        Computes the cosine distance between two vectors: 1 - cosine similarity.
    
        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.
    
        Returns:
            float: The computed cosine distance between vector_a and vector_b.
                   It ranges from 0 (completely similar) to 2 (completely dissimilar).
        """
        norm_a = norm(vector_a.value)
        norm_b = norm(vector_b.value)
    
        # Check if either of the vector norms is close to zero
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 1.0  # Return maximum distance for cosine which varies between -1 to 1, so 1 indicates complete dissimilarity
    
        # Compute the cosine similarity between the vectors
        cos_sim = self.dot_product(vector_a, vector_b) / (norm_a * norm_b)
    
        # Covert cosine similarity to cosine distance
        cos_distance = 1 - cos_sim
    
        return cos_distance
    
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the cosine similarity between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The cosine similarity between vector_a and vector_b.
        """
        return 1 - self.distance(vector_a, vector_b)

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/EuclideanDistance.py

from math import sqrt
from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase

class EuclideanDistance(DistanceBase):
    """
    Class to compute the Euclidean distance between two vectors.
    Implements the IDistanceSimiliarity interface.
    """    
    type: Literal['EuclideanDistance'] = 'EuclideanDistance'
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Euclidean distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Euclidean distance between vector_a and vector_b.
        """
        if len(vector_a.value) != len(vector_b.value):
            raise ValueError("Vectors do not have the same dimensionality.")
        
        distance = sqrt(sum((a - b) ** 2 for a, b in zip(vector_a.value, vector_b.value)))
        return distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the similarity score as the inverse of the Euclidean distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The similarity score between vector_a and vector_b.
        """
        distance = self.distance(vector_a, vector_b)
        return 1 / (1 + distance)
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/JaccardIndexDistance.py

from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase


class JaccardIndexDistance(DistanceBase):
    """
    A class implementing Jaccard Index as a similarity and distance metric between two vectors.
    """    
    type: Literal['JaccardIndexDistance'] = 'JaccardIndexDistance'
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Jaccard distance between two vectors.

        The Jaccard distance, which is 1 minus the Jaccard similarity,
        measures dissimilarity between sample sets. It's defined as
        1 - (the intersection of the sets divided by the union of the sets).

        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.

        Returns:
            float: The Jaccard distance between vector_a and vector_b.
        """
        set_a = set(vector_a.value)
        set_b = set(vector_b.value)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In the special case where the union is zero, return 1.0 which implies complete dissimilarity.
        if union == 0:
            return 1.0

        # Compute Jaccard similarity and then return the distance as 1 - similarity.
        jaccard_similarity = intersection / union
        return 1 - jaccard_similarity

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Jaccard similarity between two vectors.

        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.

        Returns:
            float: Jaccard similarity score between vector_a and vector_b.
        """
        set_a = set(vector_a.value)
        set_b = set(vector_b.value)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In case the union is zero, which means both vectors have no elements, return 1.0 implying identical sets.
        if union == 0:
            return 1.0

        # Compute and return Jaccard similarity.
        return intersection / union
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/LevenshteinDistance.py

import numpy as np
from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase


class LevenshteinDistance(DistanceBase):
    """
    Implements the IDistance interface to calculate the Levenshtein distance between two vectors.
    The Levenshtein distance between two strings is given by the minimum number of operations needed to transform
    one string into the other, where an operation is an insertion, deletion, or substitution of a single character.
    """
    type: Literal['LevenshteinDistance'] = 'LevenshteinDistance'   
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute the Levenshtein distance between two vectors.

        Note: Since Levenshtein distance is typically calculated between strings,
        it is assumed that the vectors represent strings where each element of the
        vector corresponds to the ASCII value of a character in the string.

        Args:
            vector_a (List[float]): The first vector in the comparison.
            vector_b (List[float]): The second vector in the comparison.

        Returns:
           float: The computed Levenshtein distance between vector_a and vector_b.
        """
        string_a = ''.join([chr(int(round(value))) for value in vector_a.value])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.value])
        
        return self.levenshtein(string_a, string_b)
    
    def levenshtein(self, seq1: str, seq2: str) -> float:
        """
        Calculate the Levenshtein distance between two strings.
        
        Args:
            seq1 (str): The first string.
            seq2 (str): The second string.
        
        Returns:
            float: The Levenshtein distance between seq1 and seq2.
        """
        size_x = len(seq1) + 1
        size_y = len(seq2) + 1
        matrix = np.zeros((size_x, size_y))
        
        for x in range(size_x):
            matrix[x, 0] = x
        for y in range(size_y):
            matrix[0, y] = y

        for x in range(1, size_x):
            for y in range(1, size_y):
                if seq1[x-1] == seq2[y-1]:
                    matrix[x, y] = min(matrix[x-1, y] + 1, matrix[x-1, y-1], matrix[x, y-1] + 1)
                else:
                    matrix[x, y] = min(matrix[x-1, y] + 1, matrix[x-1, y-1] + 1, matrix[x, y-1] + 1)
        
        return matrix[size_x - 1, size_y - 1]
    
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        string_a = ''.join([chr(int(round(value))) for value in vector_a.value])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.value])
        return 1 - self.levenshtein(string_a, string_b) / max(len(vector_a), len(vector_b))
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/__init__.py



```

```swarmauri/standard/metrics/__init__.py



```

```swarmauri/standard/metrics/base/__init__.py



```

```swarmauri/standard/metrics/base/MetricBase.py

from typing import Any, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.metrics.IMetric import IMetric

class MetricBase(IMetric, ComponentBase):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """
    unit: str
    value: Any = None
    resource: Optional[str] =  Field(default=ResourceTypes.METRIC.value, frozen=True)
    type: Literal['MetricBase'] = 'MetricBase'

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value

```

```swarmauri/standard/metrics/base/MetricCalculateMixin.py

from abc import abstractmethod
from typing import Any, Literal
from pydantic import BaseModel
from swarmauri.core.metrics.IMetricCalculate import IMetricCalculate

class MetricCalculateMixin(IMetricCalculate, BaseModel):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """
    
    def update(self, value) -> None:
        """
        Update the metric value based on new information.
        This should be used internally by the `calculate` method or other logic.
        """
        self.value = value

    @abstractmethod
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the metric based on the provided data.
        This method must be implemented by subclasses to define specific calculation logic.
        """
        raise NotImplementedError('calculate is not implemented yet.')
    
    def __call__(self, **kwargs) -> Any:
        """
        Calculates the metric, updates the value, and returns the current value.
        """
        self.calculate(**kwargs)
        return self.value


```

```swarmauri/standard/metrics/base/MetricAggregateMixin.py

from typing import List, Any, Literal
from pydantic import BaseModel
from swarmauri.core.metrics.IMetricAggregate import IMetricAggregate

class MetricAggregateMixin(IMetricAggregate, BaseModel):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    measurements: List[Any] = []

    
    def add_measurement(self, measurement) -> None:
        """
        Adds measurement to the internal store of measurements.
        """
        self.measurements.append(measurement)

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        self.measurements.clear()
        self.value = None



```

```swarmauri/standard/metrics/base/MetricThresholdMixin.py

from abc import ABC, abstractmethod
from typing import Literal
from pydantic import BaseModel
from swarmauri.core.metrics.IThreshold import IThreshold

class MetricThresholdMixin(IThreshold, BaseModel):
    k: int
    

```

```swarmauri/standard/metrics/concrete/__init__.py



```

```swarmauri/standard/metrics/concrete/MeanMetric.py

from typing import Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase
from swarmauri.standard.metrics.base.MetricCalculateMixin import MetricCalculateMixin
from swarmauri.standard.metrics.base.MetricAggregateMixin import MetricAggregateMixin

class MeanMetric(MetricAggregateMixin, MetricCalculateMixin, MetricBase):
    """
    A metric that calculates the mean (average) of a list of numerical values.

    Attributes:
        name (str): The name of the metric.
        unit (str): The unit of measurement for the mean (e.g., "degrees", "points").
        _value (float): The calculated mean of the measurements.
        _measurements (list): A list of measurements (numerical values) to average.
    """
    type: Literal['MeanMetric'] = 'MeanMetric'

    def add_measurement(self, measurement: int) -> None:
        """
        Adds a measurement to the internal list of measurements.

        Args:
            measurement (float): A numerical value to be added to the list of measurements.
        """
        # Append the measurement to the internal list
        self.measurements.append(measurement)

    def calculate(self) -> float:
        """
        Calculate the mean of all added measurements.
        
        Returns:
            float: The mean of the measurements or None if no measurements have been added.
        """
        if not self.measurements:
            return None  # Return None if there are no measurements
        # Calculate the mean
        mean = sum(self.measurements) / len(self.measurements)
        # Update the metric's value
        self.update(mean)
        # Return the calculated mean
        return mean

```

```swarmauri/standard/metrics/concrete/ZeroMetric.py

from typing import Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase

class ZeroMetric(MetricBase):
    """
    A concrete implementation of MetricBase that statically represents the value 0.
    This can be used as a placeholder or default metric where dynamic calculation is not required.
    """
    unit: str = "unitless"
    value: int = 0
    type: Literal['ZeroMetric'] = 'ZeroMetric'

    def __call__(self):
        """
        Overrides the value property to always return 0.
        """
        return self.value


```

```swarmauri/standard/metrics/concrete/FirstImpressionMetric.py

from typing import Any, Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase

class FirstImpressionMetric(MetricBase):
    """
    Metric for capturing the first impression score from a set of scores.
    """
    type: Literal['FirstImpressionMetric'] = 'FirstImpressionMetric'
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value


```

```swarmauri/standard/metrics/concrete/StaticMetric.py

from typing import Any, Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase

class StaticMetric(MetricBase):
    """
    Metric for capturing the first impression score from a set of scores.
    """
    type: Literal['StaticMetric'] = 'StaticMetric'

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value


```

```swarmauri/standard/agent_factories/__init__.py



```

```swarmauri/standard/agent_factories/base/__init__.py



```

```swarmauri/standard/agent_factories/concrete/AgentFactory.py

import json
from datetime import datetime
from typing import Callable, Dict, Any
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri.core.agentfactories.IExportConf import IExportConf

class AgentFactory(IAgentFactory, IExportConf):
    def __init__(self):
        """ Initializes the AgentFactory with an empty registry and metadata. """
        self._registry: Dict[str, Callable[..., IAgent]] = {}
        self._metadata = {
            'id': None,
            'name': 'DefaultAgentFactory',
            'type': 'Generic',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }
    
    # Implementation of IAgentFactory methods
    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        constructor = self._registry[agent_type]
        return constructor(**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., IAgent]) -> None:
        if agent_type in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is already registered.")
        self._registry[agent_type] = constructor
        self._metadata['last_modified'] = datetime.now()
    
    # Implementation of IExportConf methods
    def to_dict(self) -> Dict[str, Any]:
        """Exports the registry metadata as a dictionary."""
        export_data = self._metadata.copy()
        export_data['registry'] = list(self._registry.keys())
        return export_data

    def to_json(self) -> str:
        """Exports the registry metadata as a JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        """Exports the registry metadata to a file."""
        with open(file_path, 'w') as f:
            f.write(self.to_json())
    
    @property
    def id(self) -> int:
        return self._metadata['id']

    @id.setter
    def id(self, value: int) -> None:
        self._metadata['id'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata['name']

    @name.setter
    def name(self, value: str) -> None:
        self._metadata['name'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata['type']

    @type.setter
    def type(self, value: str) -> None:
        self._metadata['type'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata['date_created']

    @property
    def last_modified(self) -> datetime:
        return self._metadata['last_modified']

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata['last_modified'] = value

```

```swarmauri/standard/agent_factories/concrete/ConfDrivenAgentFactory.py

import json
import importlib
from datetime import datetime
from typing import Any, Dict, Callable
from swarmauri.core.agents.IAgent import IAgent  # Replace with the correct IAgent path
from swarmauri.core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri.core.agentfactories.IExportConf import IExportConf


class ConfDrivenAgentFactory(IAgentFactory, IExportConf):
    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = self._load_config(config_path)
        self._registry = {}
        self._metadata = {
            'id': None,
            'name': 'ConfAgentFactory',
            'type': 'Configurable',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }
        
        self._initialize_registry()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as file:
            return json.load(file)
    
    def _initialize_registry(self) -> None:
        for agent_type, agent_info in self._config.get("agents", {}).items():
            module_name, class_name = agent_info["class_path"].rsplit('.', 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            self.register_agent(agent_type, cls)
    
    # Implementation of IAgentFactory methods
    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        return self._registry[agent_type](**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., IAgent]) -> None:
        self._registry[agent_type] = constructor
        self._metadata['last_modified'] = datetime.now()
    
    # Implementation of IExportConf methods
    def to_dict(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as f:
            f.write(self.to_json())

    # Additional methods to implement required properties and their setters
    # Implementing getters and setters for metadata properties as needed
    @property
    def id(self) -> int:
        return self._metadata['id']

    @id.setter
    def id(self, value: int) -> None:
        self._metadata['id'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata['name']

    @name.setter
    def name(self, value: str) -> None:
        self._metadata['name'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata['type']

    @type.setter
    def type(self, value: str) -> None:
        self._metadata['type'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata['date_created']

    @property
    def last_modified(self) -> datetime:
        return self._metadata['last_modified']

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata['last_modified'] = value

```

```swarmauri/standard/agent_factories/concrete/ReflectiveAgentFactory.py

import importlib
from datetime import datetime
import json
from typing import Callable, Dict, Type, Any
from swarmauri.core.agents.IAgent import IAgent  # Update this import path as needed
from swarmauri.core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri.core.agentfactories.IExportConf import IExportConf

class ReflectiveAgentFactory(IAgentFactory, IExportConf):
    def __init__(self):
        self._registry: Dict[str, Type[IAgent]] = {}
        self._metadata = {
            'id': None,
            'name': 'ReflectiveAgentFactory',
            'type': 'Reflective',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }

    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        agent_class = self._registry[agent_type]
        return agent_class(**kwargs)

    def register_agent(self, agent_type: str, class_path: str) -> None:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        self._registry[agent_type] = cls
        self._metadata['last_modified'] = datetime.now()

    # Implementations for the IExportConf interface
    def to_dict(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            file.write(self.to_json())

    # Property implementations: id, name, type, date_created, and last_modified
    @property
    def id(self) -> int:
        return self._metadata['id']

    @id.setter
    def id(self, value: int) -> None:
        self._metadata['id'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata['name']

    @name.setter
    def name(self, value: str) -> None:
        self._metadata['name'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata['type']

    @type.setter
    def type(self, value: str) -> None:
        self._metadata['type'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata['date_created']

    @property
    def last_modified(self) -> datetime:
        return self._metadata['last_modified']

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata['last_modified'] = value

```

```swarmauri/standard/agent_factories/concrete/__init__.py



```

```swarmauri/standard/agent_factories/concrete/JsonAgentFactory.py

import json
from jsonschema import validate, ValidationError
from typing import Dict, Any, Callable, Type
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.agent_factories.IAgentFactory import IAgentFactory
from swarmauri.core.agent_factories.IExportConf import IExportConf
import importlib

class JsonAgentFactory:
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._registry: Dict[str, Type[Any]] = {}

        # Load and validate config
        self._validate_config()
        self._load_config()

    def _validate_config(self) -> None:
        """Validates the configuration against the JSON schema."""
        schema = {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "agents": {
                  "type": "object",
                  "patternProperties": {
                    "^[a-zA-Z][a-zA-Z0-9_-]*$": {
                      "type": "object",
                      "properties": {
                        "constructor": {
                          "type": "object",
                          "required": ["module", "class"]
                        }
                      },
                      "required": ["constructor"]
                    }
                  }
                }
              },
              "required": ["agents"]
            }

        try:
            validate(instance=self._config, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e.message}")

    def _load_config(self):
        """Loads configuration and registers agents accordingly."""
        agents_config = self._config.get("agents", {})
        for agent_type, agent_info in agents_config.items():
            module_name = agent_info["constructor"]["module"]
            class_name = agent_info["constructor"]["class"]

            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)

            self.register_agent(agent_type, cls)

    def create_agent(self, agent_type: str, **kwargs) -> Any:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        constructor = self._registry[agent_type]
        print(f"Creating instance of {constructor}, with args: {kwargs}")
        return constructor(**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., Any]) -> None:
        if agent_type in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is already registered.")
        
        print(f"Registering agent type '{agent_type}' with constructor: {constructor}")
        self._registry[agent_type] = constructor

    def to_dict(self) -> Dict[str, Any]:
        return self._config

    def to_json(self) -> str:
        return json.dumps(self._config, default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            file.write(self.to_json())

    @property
    def id(self) -> int:
        return self._config.get('id', None)  # Assuming config has an 'id'.

    @id.setter
    def id(self, value: int) -> None:
        self._config['id'] = value

    @property
    def name(self) -> str:
        return self._config.get('name', 'ConfDrivenAgentFactory')

    @name.setter
    def name(self, value: str) -> None:
        self._config['name'] = value

    @property
    def type(self) -> str:
        return self._config.get('type', 'Configuration-Driven')

    @type.setter
    def type(self, value: str) -> None:
        self._config['type'] = value

    @property
    def date_created(self) -> str:
        return self._config.get('date_created', None)

    @property
    def last_modified(self) -> str:
        return self._config.get('last_modified', None)

    @last_modified.setter
    def last_modified(self, value: str) -> None:
        self._config['last_modified'] = value
        self._config['last_modified'] = value

```

```swarmauri/standard/exceptions/__init__.py



```

```swarmauri/standard/exceptions/base/__init__.py



```

```swarmauri/standard/exceptions/concrete/IndexErrorWithContext.py

import inspect

class IndexErrorWithContext(Exception):
    def __init__(self, original_exception):
        self.original_exception = original_exception
        self.stack_info = inspect.stack()
        self.handle_error()

    def handle_error(self):
        # You might want to log this information or handle it differently depending on your application's needs
        frame = self.stack_info[1]  # Assuming the IndexError occurs one level up from where it's caught
        error_details = {
            "message": str(self.original_exception),
            "function": frame.function,
            "file": frame.filename,
            "line": frame.lineno,
            "code_context": ''.join(frame.code_context).strip() if frame.code_context else "No context available"
        }
        print("IndexError occurred with detailed context:")
        for key, value in error_details.items():
            print(f"{key.capitalize()}: {value}")

```

```swarmauri/standard/exceptions/concrete/__init__.py

from .IndexErrorWithContext import IndexErrorWithContext

```

```swarmauri/standard/schema_converters/__init__.py



```

```swarmauri/standard/schema_converters/base/SchemaConverterBase.py

from abc import abstractmethod
from typing import Optional, Dict, Any, Literal
from pydantic import ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.schema_converters.ISchemaConvert import ISchemaConvert
from swarmauri.core.tools.ITool import ITool

class SchemaConverterBase(ISchemaConvert, ComponentBase):
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.SCHEMA_CONVERTER.value, frozen=True)
    type: Literal['SchemaConverterBase'] = 'SchemaConverterBase'

    @abstractmethod
    def convert(self, tool: ITool) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the convert method.")


```

```swarmauri/standard/schema_converters/base/__init__.py



```

```swarmauri/standard/schema_converters/concrete/__init__.py



```

```swarmauri/standard/schema_converters/concrete/GroqSchemaConverter.py

from typing import  Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class GroqSchemaConverter(SchemaConverterBase):
    type: Literal['GroqSchemaConverter'] = 'GroqSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)

        function = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                }
            }
        }
        if required:
            function['function']['parameters']['required'] = required

        return function


```

```swarmauri/standard/schema_converters/concrete/AnthropicSchemaConverter.py

from typing import  Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class AnthropicSchemaConverter(SchemaConverterBase):
    type: Literal['AnthropicSchemaConverter'] = 'AnthropicSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }


```

```swarmauri/standard/schema_converters/concrete/OpenAISchemaConverter.py

from typing import  Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class OpenAISchemaConverter(SchemaConverterBase):
    type: Literal['OpenAISchemaConverter'] = 'OpenAISchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }

```

```swarmauri/standard/schema_converters/concrete/CohereSchemaConverter.py

from typing import Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class CohereSchemaConverter(SchemaConverterBase):
    type: Literal['CohereSchemaConverter'] = 'CohereSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}

        for param in tool.parameters:
            properties[param.name] = {
                "description": param.description,
                "required": param.required
            }
            if param.type == 'string':
                _type = 'str'
            elif param.type == 'float':
                _type = 'float'
            elif param.type == 'integer':
                _type = 'int'
            elif param.type == 'boolean':
                _type = 'bool'
            else:
                raise NotImplementedError(f'🚧 Support for missing type pending https://docs.cohere.com/docs/parameter-types-in-tool-use\n: Missing Type: {param.type}')
            properties[param.name].update({'type': _type})

        return {
            "name": tool.name,
            "description": tool.description,
            "parameter_definitions": properties
        }

```

```swarmauri/standard/schema_converters/concrete/MistralSchemaConverter.py

from typing import Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class MistralSchemaConverter(SchemaConverterBase):
    type: Literal['MistralSchemaConverter'] = 'MistralSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }

```

```swarmauri/standard/schema_converters/concrete/GeminiSchemaConverter.py

from typing import Dict, Any, Literal
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class GeminiSchemaConverter(SchemaConverterBase):
    type: Literal['GeminiSchemaConverter'] = 'GeminiSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> genai.protos.FunctionDeclaration:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = genai.protos.Schema(
                type=self.convert_type(param.type),
                description=param.description
            )
            if param.required:
                required.append(param.name)

        schema = genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties=properties,
            required=required
        )

        return genai.protos.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=schema
        )

    def convert_type(self, param_type: str) -> genai.protos.Type:
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "str": genai.protos.Type.STRING,
            "integer": genai.protos.Type.INTEGER,
            "int": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "bool": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT
        }
        return type_mapping.get(param_type, genai.protos.Type.STRING)

```