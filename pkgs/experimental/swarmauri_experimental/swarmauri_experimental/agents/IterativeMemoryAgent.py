from typing import Any, Optional, Dict, Union, Literal
import json
import os


from swarmauri.vector_stores.Doc2VecVectorStore import Doc2VecVectorStore
from swarmauri.embeddings.Doc2VecEmbedding import Doc2VecEmbedding

from swarmauri.documents.Document import Document
from swarmauri.chunkers.MdSnippetChunker import MdSnippetChunker
from swarmauri.distances.EuclideanDistance import EuclideanDistance

from swarmauri.messages.HumanMessage import HumanMessage
from swarmauri.conversations.MaxSystemContextConversation import MaxSystemContextConversation
from swarmauri.conversations.SessionCacheConversation import SessionCacheConversation
from swarmauri.messages.SystemMessage import SystemMessage
from swarmauri.prompts.PromptTemplate import PromptTemplate

from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri_base.prompts.PromptTemplateBase import PromptTemplateBase
from swarmauri_base.chunkers.ChunkerBase import ChunkerBase

from swarmauri_base.agents.AgentRetrieveMixin import AgentRetrieveMixin
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.agents.AgentVectorStoreMixin import AgentVectorStoreMixin
from swarmauri_base.agents.AgentSystemContextMixin import AgentSystemContextMixin

from swarmauri_base.ComponentBase import SubclassUnion, ComponentBase
from swarmauri_core.messages.IMessage import IMessage

@ComponentBase.register_type(AgentBase, 'IterativeMemoryAgent')
class IterativeMemoryAgent(AgentRetrieveMixin, 
                  AgentVectorStoreMixin, 
                  AgentSystemContextMixin, 
                  AgentConversationMixin, 
                  AgentBase):
    """
    A subclass of AgentBase that integrates the RAG workflow and additional capabilities.
    """
    llm: SubclassUnion[LLMBase]
    vector_store: SubclassUnion[VectorStoreBase]
    conversation: Union[MaxSystemContextConversation, SessionCacheConversation] = MaxSystemContextConversation(max_size=3)
    system_context: Union[SystemMessage, str] = SystemMessage(content="")
    chunker: SubclassUnion[ChunkerBase] = MdSnippetChunker() 
    prompt_template: SubclassUnion[PromptTemplateBase] = PromptTemplate()
    type: Literal['IterativeMemoryAgent'] = 'IterativeMemoryAgent'

    def exec(self, input_data: Optional[Union[Dict, str]] = "", folder_path: str = "", llm_kwargs: Optional[Dict] = {}) -> Any:
        try:
            # Reload vector store and documents
            self.reload(folder_path)

            # Parse string input to a dictionary if needed
            if isinstance(input_data, str):
                input_data = json.loads(input_data)
            elif not isinstance(input_data, dict):
                raise ValueError("Input must be a dictionary or a JSON string representing a dictionary.")

            # Propagate the template
            filled_prompt = self.propagate_template(input_data)

            # Predict with the LLM
            response = self._exec(filled_prompt, llm_kwargs=llm_kwargs)

            # Chunk the content
            chunk = self.chunk_content(response)

            # Write the content to a file
            self.write_to_file(folder_path, input_data, chunk)

            return chunk

        except Exception as e:
            print(f"Error in NewRagAgent exec: {e}")
            raise e

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

    def _exec(self, 
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

    def reload(self, folder_path: str):
        """
        Reloads the vector store by clearing it and loading documents from the folder.
        """
        self.vector_store = Doc2VecVectorStore()
        self.vector_store._distance = EuclideanDistance()
        self.vector_store._embedder = Doc2VecEmbedding()
        
        self.load_documents_from_folder(folder_path)

    def propagate_template(self, input_data: Dict) -> str:
        """
        Fills the prompt template with the given input data.
        """
        if not self.prompt_template:
            raise ValueError("PromptTemplate is not initialized.")

        return self.prompt_template.generate_prompt(input_data)

    def chunk_content(self, full_content: str) -> str:
        """
        Splits the content into chunks using the chunker.
        """
        if not self.chunker:
            raise ValueError("Chunker is not initialized.")

        split = self.chunker.chunk_text(full_content)
        try:
            return split[0][2]
        except IndexError:
            return full_content

    def write_to_file(self, root_folder: str, component: Dict, content: str):
        """
        Writes the content to a file at the specified location.
        """
        try:
            filename = component['FILE_NAME']
            os.makedirs(root_folder, exist_ok=True)
            file_path = os.path.join(root_folder, filename)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            print(f"File successfully written to {file_path}")

        except Exception as e:
            print(f"Error writing to file: {e}")
            raise e

    def load_documents_from_folder(self, folder_path: str):
        """Recursively walks through a folder and loads documents from all files."""
        documents = []
        
        # Traverse through all directories and files
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                        document = Document(content=file_content, metadata={"filepath": file_path})
                        documents.append(document)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {file_name}")
        # Add all loaded documents to the vector store
        self.vector_store.add_documents(documents)
        print(f"Successfully loaded {len(documents)} documents from folder into the vector store.")