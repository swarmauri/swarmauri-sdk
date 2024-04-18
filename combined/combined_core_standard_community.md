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

```swarmauri/core/models/__init__.py



```

```swarmauri/core/models/IPredict.py

from abc import ABC, abstractmethod

class IPredict(ABC):
    """
    Interface for making predictions with models.
    """

    @abstractmethod
    def predict(self, input_data) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

```

```swarmauri/core/models/IFit.py

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

```swarmauri/core/models/IModel.py

from abc import ABC, abstractmethod

class IModel(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining models.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the model.
        """
        pass

    @model_name.setter
    @abstractmethod
    def model_name(self, value: str) -> None:
        """
        Set the name of the model.
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

    @property
    @abstractmethod
    def max_size(self) -> int:
        """
        """
        pass

    @max_size.setter
    @abstractmethod
    def max_size(self, new_max_size: int) -> None:
        """ 
        """
        pass

```

```swarmauri/core/conversations/IConversation.py

from abc import ABC, abstractmethod
from typing import List, Optional
from ..messages.IMessage import IMessage

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

    @abstractmethod
    def as_dict(self) -> List[dict]:
        """
        Returns all messages from the conversation history as a list of dictionaries.
        """
        pass

```

```swarmauri/core/conversations/ISystemContext.py

from abc import ABC, abstractmethod
from typing import Optional
from ..messages.IMessage import IMessage

class ISystemContext(ABC):

    @property
    @abstractmethod
    def system_context(self) -> Optional[IMessage]:
        """
        An abstract property to get the system context message.
        Subclasses must provide an implementation for storing and retrieving system context.
        """
        pass

    @system_context.setter
    @abstractmethod
    def system_context(self, new_system_message: Optional[IMessage]) -> None:
        """
        An abstract property setter to update the system context.
        Subclasses must provide an implementation for how the system context is updated.
        This might be a direct string, which is converted to an IMessage instance, or directly an IMessage instance.
        """
        pass

```

```swarmauri/core/documents/__init__.py



```

```swarmauri/core/documents/IDocument.py

from abc import ABC, abstractmethod
from typing import Dict

class IDocument(ABC):
    @abstractmethod
    def __init__(self, id: str, content: str, metadata: Dict):
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Get the document's ID.
        """
        pass

    @id.setter
    @abstractmethod
    def id(self, value: str) -> None:
        """
        Set the document's ID.
        """
        pass

    @property
    @abstractmethod
    def content(self) -> str:
        """
        Get the document's content.
        """
        pass

    @content.setter
    @abstractmethod
    def content(self, value: str) -> None:
        """
        Set the document's content.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Dict:
        """
        Get the document's metadata.
        """
        pass

    @metadata.setter
    @abstractmethod
    def metadata(self, value: Dict) -> None:
        """
        Set the document's metadata.
        """
        pass

    # Including the abstract methods __str__ and __repr__ definitions for completeness.
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass
    
    def __setitem__(self, key, value):
        """Allow setting items like a dict for metadata."""
        self.metadata[key] = value

    def __getitem__(self, key):
        """Allow getting items like a dict for metadata."""
        return self.metadata.get(key)

```

```swarmauri/core/documents/IEmbed.py

from abc import ABC, abstractmethod
from typing import Dict
from swarmauri.core.vectors.IVector import IVector

class IEmbed(ABC):
    @property
    @abstractmethod
    def embedding(self) -> IVector:
        """
        Get the document's embedding.
        """
        pass

    @embedding.setter
    @abstractmethod
    def embedding(self, value: IVector) -> None:
        """
        Set the document's embedding.
        """
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
    @property
    @abstractmethod
    def role(self) -> str:
        pass
    
    @property
    @abstractmethod
    def content(self) -> str:
        pass

    @abstractmethod
    def as_dict(self) -> dict:
        """
        An abstract method that subclasses must implement to return a dictionary representation of the object.
        """
        pass

```

```swarmauri/core/messages/__init__.py

from .IMessage import IMessage

```

```swarmauri/core/parsers/__init__.py



```

```swarmauri/core/parsers/IParser.py

from abc import ABC, abstractmethod
from typing import List, Union, Any
from ..documents.IDocument import IDocument

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
    def __call__(self, prompt: Optional[Any]) -> str:
        """
        Abstract method that subclasses must implement to define the behavior of the prompt when called.

        """
        pass


```

```swarmauri/core/prompts/ITemplate.py

from typing import Dict, List
from abc import ABC, abstractmethod


class ITemplate(ABC):
    """
    Interface for template-based prompt generation within the SwarmAURI framework.
    Defines standard operations and attributes for managing and utilizing templates.
    """

    @property
    @abstractmethod
    def template(self) -> str:
        """
        Abstract property to get the current template string.
        """
        pass

    @template.setter
    @abstractmethod
    def template(self, value: str) -> None:
        """
        Abstract property setter to set or update the current template string.

        Args:
            value (str): The new template string to be used for generating prompts.
        """
        pass


    @property
    @abstractmethod
    def variables(self) -> List[Dict[str, str]]:
        """
        Abstract property to get the current set of variables for the template.
        """
        pass

    @variables.setter
    @abstractmethod
    def variables(self, value: List[Dict[str, str]]) -> None:
        """
        Abstract property setter to set or update the variables for the template.
        """
        pass

    @abstractmethod
    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.

        Args:
            template (str): The new template string to be used for generating prompts.
        """
        pass

    @abstractmethod
    def set_variables(self, variables: List[Dict[str, str]]) -> None:
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

```swarmauri/core/agents/__init__.py



```

```swarmauri/core/agents/IAgentToolkit.py

from abc import ABC, abstractmethod
from swarmauri.core.toolkits.IToolkit import IToolkit


class IAgentToolkit(ABC):


    @property
    @abstractmethod
    def toolkit(self) -> IToolkit:
        pass
    
    @toolkit.setter
    @abstractmethod
    def toolkit(self) -> IToolkit:
        pass
    


```

```swarmauri/core/agents/IAgentConversation.py

from abc import ABC, abstractmethod
from swarmauri.core.conversations.IConversation import IConversation

class IAgentConversation(ABC):
    
    @property
    @abstractmethod
    def conversation(self) -> IConversation:
        """
        The conversation property encapsulates the agent's ongoing dialogue or interaction context.
        """
        pass

    @conversation.setter
    @abstractmethod
    def conversation(self) -> IConversation:
        pass

```

```swarmauri/core/agents/IAgentRetriever.py

from abc import ABC, abstractmethod
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve

class IAgentRetriever(ABC):
    
    @property
    @abstractmethod
    def retriever(self) -> IDocumentRetrieve:
        pass

    @retriever.setter
    @abstractmethod
    def retriever(self) -> IDocumentRetrieve:
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

```swarmauri/core/agents/IAgentName.py

from abc import ABC, abstractmethod

class IAgentName(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        The conversation property encapsulates the agent's ongoing dialogue or interaction context.
        """
        pass

    @name.setter
    @abstractmethod
    def name(self) -> str:
        pass

```

```swarmauri/core/agents/IAgent.py

from abc import ABC, abstractmethod
from typing import Any, Optional
from swarmauri.core.models.IModel import IModel

class IAgent(ABC):

    @abstractmethod
    def exec(self, input_data: Optional[Any]) -> Any:
        """
        Executive method that triggers the agent's action based on the input data.
        """
        pass
    
    @property
    @abstractmethod
    def model(self) -> IModel:
        """
        The model property describes the computational model used by the agent.
        """
        pass
    
    @model.setter
    @abstractmethod
    def model(self) -> IModel:

        pass


```

```swarmauri/core/agents/IAgentVectorStore.py

from abc import ABC, abstractmethod
from swarmauri.core.vector_stores.IVectorStore import IVectorStore

class IAgentVectorStore(ABC):
    
    @property
    @abstractmethod
    def vector_store(self) -> IVectorStore:
        pass

    @vector_store.setter
    @abstractmethod
    def vector_store(self) -> IVectorStore:
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
from ..tools.ITool import ITool  # Ensure Tool is correctly imported from your tools package

class IToolkit(ABC):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    @property
    @abstractmethod
    def tools(self) -> Dict[str, ITool]:
        """
        An abstract property that should be implemented by subclasses to return the tools dictionary
        """
        pass

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
    
    @property
    @abstractmethod
    def name(self):
        pass
    
    @property
    @abstractmethod
    def description(self):
        pass
    
    @property
    @abstractmethod
    def parameters(self):
        pass
    
    @abstractmethod
    def as_dict(self):
        pass

    @abstractmethod
    def to_json(obj):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass







```

```swarmauri/core/tools/IParameter.py

from abc import ABC, abstractmethod
from typing import Optional, List, Any

class IParameter(ABC):
    """
    An abstract class to represent a parameter for a tool.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Abstract property for getting the name of the parameter.
        """
        pass

    @name.setter
    @abstractmethod
    def name(self, value: str):
        """
        Abstract setter for setting the name of the parameter.
        """
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """
        Abstract property for getting the type of the parameter.
        """
        pass

    @type.setter
    @abstractmethod
    def type(self, value: str):
        """
        Abstract setter for setting the type of the parameter.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Abstract property for getting the description of the parameter.
        """
        pass

    @description.setter
    @abstractmethod
    def description(self, value: str):
        """
        Abstract setter for setting the description of the parameter.
        """
        pass

    @property
    @abstractmethod
    def required(self) -> bool:
        """
        Abstract property for getting the required status of the parameter.
        """
        pass

    @required.setter
    @abstractmethod
    def required(self, value: bool):
        """
        Abstract setter for setting the required status of the parameter.
        """
        pass

    @property
    @abstractmethod
    def enum(self) -> Optional[List[Any]]:
        """
        Abstract property for getting the enum list of the parameter.
        """
        pass

    @enum.setter
    @abstractmethod
    def enum(self, value: Optional[List[Any]]):
        """
        Abstract setter for setting the enum list of the parameter.
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

```swarmauri/core/vector_stores/ISaveLoadStore.py

from abc import ABC, abstractmethod

class ISaveLoadStore(ABC):
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

```swarmauri/core/document_stores/IDocumentStore.py

from abc import ABC, abstractmethod
from typing import List, Union
from ..documents.IDocument import IDocument

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

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 20:35:27 2024

@author: bigman
"""



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
from typing import Any, Dict, List

class IVector(ABC):
    """
    Interface for a high-dimensional data vector. This interface defines the
    basic structure and operations for interacting with vectors in various applications,
    such as machine learning, information retrieval, and similarity search.
    """

    @property
    @abstractmethod
    def data(self) -> List[float]:
        """
        The high-dimensional data that the vector represents. It is typically a list of float values.
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

```swarmauri/core/vectorizers/__init__.py

#

```

```swarmauri/core/vectorizers/IVectorize.py

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
    def fit(self, data: Union[str, Any]) -> List[IVector]:
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

```swarmauri/core/vectorizers/IFeature.py

from abc import ABC, abstractmethod
from typing import List, Any

class IFeature(ABC):

    @abstractmethod
    def extract_features(self) -> List[Any]:
        pass
    


```

```swarmauri/core/vectorizers/ISaveModel.py

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
    def __init__(self, steps: List[IChainStep] = None, **configs):
        pass

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

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
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
    def __init__(self, **configs):
        pass

    @abstractmethod
    def create_chain(self, steps: List[IChainStep] = None) -> IChain:
        pass
    
    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_chain_info(self) -> Dict[str, Any]:
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
    
    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_chain_info(self) -> Dict[str, Any]:
        pass    
    


```

```swarmauri/core/chains/IChainStep.py

from typing import List, Dict, Any, Callable

class IChainStep:
    """
    Represents a single step within an execution chain.
    """
    def __init__(self, 
        key: str, 
        method: Callable, 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None, 
        ref: str = None):
        """
        Initialize a chain step.

        Args:
            key (str): Unique key or identifier for the step.
            method (Callable): The callable object (function or method) to execute in this step.
            args (List[Any], optional): Positional arguments for the callable.
            kwargs (Dict[str, Any], optional): Keyword arguments for the callable.
            ref (str, optional): Reference to another component or context variable, if applicable.
        """
        self.key = key
        self.method = method
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.ref = ref

```

```swarmauri/core/distances/__init__.py



```

```swarmauri/core/distances/IDistanceSimilarity.py

from abc import ABC, abstractmethod
from typing import List
from ..vectors.IVector import IVector

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

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name identifier for the metric.

        Returns:
            str: The name of the metric.
        """
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        """
        Current value of the metric.

        Returns:
            The metric's value. The type depends on the specific metric implementation.
        """
        pass

    @property
    @abstractmethod
    def unit(self) -> str:
        """
        The unit of measurement for the metric.

        Returns:
            str: The unit of measurement (e.g., 'seconds', 'Mbps').
        """
        pass

    @unit.setter
    @abstractmethod
    def unit(self, value: str) -> None:
        """
        Update the unit of measurement for the metric.

        Args:
            value (str): The new unit of measurement for the metric.
        """
        pass

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        pass

```

```swarmauri/core/metrics/ICalculateMetric.py

from typing import Any
from abc import ABC, abstractmethod

class ICalculateMetric(ABC):

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

```swarmauri/core/metrics/IAggMeasurements.py

from typing import List, Any
from abc import ABC, abstractmethod

class IAggMeasurements(ABC):

    @abstractmethod
    def add_measurement(self, measurement: Any) -> None:
        pass

    @property
    @abstractmethod
    def measurements(self) -> List[Any]:
        pass

    @measurements.setter
    @abstractmethod
    def measurements(self, value) -> None:
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
    @property
    @abstractmethod
    def k(self) -> int:
        pass

    @k.setter
    @abstractmethod
    def k(self, value: int) -> None:
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

``````swarmauri/standard/README.md

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

```swarmauri/standard/models/__init__.py



```

```swarmauri/standard/models/base/__init__.py



```

```swarmauri/standard/models/base/ModelBase.py

from abc import ABC, abstractmethod
from typing import Any
from ....core.models.IModel import IModel

class ModelBase(IModel, ABC):
    """
    Concrete implementation of the IModel abstract base class.
    This version includes managing the model name through a property and a setter.
    """
    @abstractmethod
    def __init__(self, model_name: str):
        self._model_name = model_name
    
    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, value: str) -> None:
        """
        Property setter that sets the name of the model.

        Parameters:
        - value (str): The new name of the model.
        """
        self._model_name = value
       
    


```

```swarmauri/standard/models/concrete/__init__.py



```

```swarmauri/standard/models/concrete/OpenAIModel.py

import json
from typing import List
from openai import OpenAI
from swarmauri.core.models.IPredict import IPredict
from swarmauri.standard.models.base.ModelBase import ModelBase


class OpenAIModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the OpenAI model with an API key.

        Parameters:
        - api_key (str): Your OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)
        
    
    def predict(self, messages, temperature=0.7, max_tokens=256, enable_json=False, stop: List[str] = None):
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
        if self.client is None:
            raise Exception("OpenAI client is not initialized. Call 'load_model' first.")
        
        if enable_json:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content

```

```swarmauri/standard/models/concrete/AzureGPT.py

import json
from openai import AzureOpenAI
from ..base.ModelBase import ModelBase
from ....core.models.IPredict import IPredict

class AzureGPT(ModelBase, IPredict):
    def __init__(self, azure_endpoint: str, api_key: str, api_version: str, model_name: str):
        """
        Initialize the Azure model with an API key.

        Parameters:
        - api_key (str): Your OpenAI API key.
        """
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.client = AzureOpenAI(
                azure_endpoint = azure_endpoint, 
                api_key = api_key,  
                api_version = api_version
            )
        super().__init__(model_name)
       

    
    def predict(self, messages, temperature=0.7, max_tokens=256, enable_json=True):
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
        if self.client is None:
            raise Exception("OpenAI client is not initialized. Call 'load_model' first.")
        
        if enable_json:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        
        result = response.json()
        message_content = json.loads(result['choices'][0]['message']['content'])
        
        return message_content

```

```swarmauri/standard/models/concrete/OpenAIImageGenerator.py

import json
from openai import OpenAI
from ..base.ModelBase import ModelBase
from ....core.models.IPredict import IPredict

class OpenAIImageGenerator(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "dall-e"):
        """
        Initializes the OpenAI image generator model.

        Parameters:
        - api_key (str): The API key provided by OpenAI for access to their services.
        - model_name (str): Name of the image generation model provided by OpenAI.
                            Defaults to "dall-e" for DALL·E, their image generation model.
        """
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)

    def predict(self, prompt: str, size: str = "1024x1024", 
                quality: str = "standard", n: int = 1) -> str:
        """
        Generates an image based on the given prompt and other parameters.

        Parameters:
        - prompt (str): A description of the image you want to generate.
        - **kwargs: Additional parameters that the image generation endpoint might use.

        Returns:
        - str: A URL or identifier for the generated image.
        """
        try:
            response = self.client.images.generate(
                model=self.model_name,
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

```swarmauri/standard/models/concrete/OpenAIToolModel.py

from openai import OpenAI
from swarmauri.standard.models.base.ModelBase import ModelBase
from swarmauri.core.models.IPredict import IPredict

class OpenAIToolModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo-0125"):
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)

    def predict(self, messages, tools=None, tool_choice=None, temperature=0.7, max_tokens=1024):
        if tools and not tool_choice:
            tool_choice = "auto"
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response

```

```swarmauri/standard/agents/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/base/NamedAgentBase.py

from typing import Any, Optional
from abc import ABC
from swarmauri.core.agents.IAgentName import IAgentName


class NamedAgentBase(IAgentName,ABC):
    
    def __init__(self, name: str):
        self._name = name

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value) -> None:
        self._name = value     

```

```swarmauri/standard/agents/base/ConversationAgentBase.py

from typing import Any, Optional
from abc import ABC

from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase

class ConversationAgentBase(AgentBase, IAgentConversation, ABC):
    def __init__(self, model: IModel, conversation: IConversation):
        AgentBase.__init__(self, model)
        self._conversation = conversation

    
    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
      

    @property
    def conversation(self) -> IConversation:
        return self._conversation

    @conversation.setter
    def conversation(self, value) -> None:
        self._conversation = value



```

```swarmauri/standard/agents/base/ToolAgentBase.py

from abc import ABC
from typing import Any, Optional
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase


class ToolAgentBase(ConversationAgentBase, IAgentConversation, ABC):
    
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation,
                 toolkit: IToolkit):
        ConversationAgentBase.__init__(self, model, conversation)
        self._toolkit = toolkit

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    @property
    def toolkit(self) -> IToolkit:
        return self._toolkit
    
    @toolkit.setter
    def toolkit(self, value) -> None:
        self._toolkit = value        


```

```swarmauri/standard/agents/base/AgentBase.py

from typing import Any, Optional
from abc import ABC
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.models.IModel import IModel



class AgentBase(IAgent, ABC):
    def __init__(self, model: IModel):
        self._model = model

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    @property
    def model(self) -> IModel:
        return self._model
    
    @model.setter
    def model(self, value) -> None:
        self._model = value        

    
    def __getattr__(self, name):
        # Example of transforming attribute name from simplified to internal naming convention
        internal_name = f"_{name}"
        if internal_name in self.__dict__:
            return self.__dict__[internal_name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        # Direct assignment to the __dict__ to bypass any potential infinite recursion
        # from setting attributes that do not explicitly exist.
        object.__setattr__(self, name, value) 
        
        
    def __str__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{class_name} {variables_str}>"
        
    def __repr__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{class_name} ({variables_str})"

```

```swarmauri/standard/agents/base/VectorStoreAgentBase.py

from typing import Any, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.agents.IAgentVectorStore import IAgentVectorStore
from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase


class VectorStoreAgentBase(ConversationAgentBase, NamedAgentBase, IAgentVectorStore):
    """
    Base class for agents that handle and store documents within their processing scope.
    Extends ConversationAgentBase and NamedAgentBase to utilize conversational context,
    naming capabilities, and implements IAgentDocumentStore for document storage.
    """

    def __init__(self, name: str, model: IModel, conversation: IConversation, vector_store: IVectorStore):
        NamedAgentBase.__init__(self, name=name)  # Initialize name through NamedAgentBase
        ConversationAgentBase.__init__(self, model, conversation)  # Initialize conversation and model
        self._vector_store = vector_store  # Document store initialization

    @property
    def vector_store(self) -> Optional[IDocument]:
        """
        Gets the document store associated with this agent.
        
        Returns:
            Optional[IDocument]: The document store of the agent, if any.
        """
        return self._vector_store

    @vector_store.setter
    def vector_store(self, value: IDocument) -> None:
        """
        Sets the document store for this agent.

        Args:
            value (IDocument): The new document store to be associated with the agent.
        """
        self._vector_store = value
    
    def exec(self, input_data: Optional[Any]) -> Any:
        """
        Placeholder method to demonstrate expected behavior of derived classes.
        Subclasses should implement their specific logic for processing input data and optionally interacting with the document store.

        Args:
            input_data (Optional[Any]): Input data to process, can be of any format that the agent is designed to handle.

        Returns:
            Any: The result of processing the input data.
        """
        raise NotImplementedError("Subclasses must implement the exec method.")

```

```swarmauri/standard/agents/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/concrete/ToolAgent.py

from typing import Any, Optional, Union, Dict
import json

from swarmauri.core.models.IModel import IModel
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.ToolAgentBase import ToolAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage


class ToolAgent(ToolAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation, 
                 toolkit: IToolkit):
        super().__init__(model, conversation, toolkit)

    def exec(self, input_data: Union[str, IMessage],  model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model
        toolkit = self.toolkit
        

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)

            
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        
        prediction = model.predict(messages=messages, 
                                   tools=toolkit.tools, 
                                   tool_choice="auto", 
                                   **model_kwargs)
        
        prediction_message = prediction.choices[0].message
        
        agent_response = prediction_message.content
        
        agent_message = AgentMessage(content=prediction_message.content, 
                                     tool_calls=prediction_message.tool_calls)
        conversation.add_message(agent_message)
        
        tool_calls = prediction.choices[0].message.tool_calls
        if tool_calls:
        
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message)
            
            
            messages = conversation.as_dict()
            rag_prediction = model.predict(messages=messages, 
                                           tools=toolkit.tools, 
                                           tool_choice="none",
                                           **model_kwargs)
            
            prediction_message = rag_prediction.choices[0].message
            
            agent_response = prediction_message.content
            agent_message = AgentMessage(agent_response)
            conversation.add_message(agent_message)
            prediction = rag_prediction
            
        return agent_response 
    

```

```swarmauri/standard/agents/concrete/ChatSwarmAgent.py

from typing import Any, Optional, Union, Dict
from swarmauri.core.models.IModel import IModel
from swarmauri.core.messages import IMessage
from swarmauri.core.conversations import IConversation
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage

class ChatSwarmAgent(ConversationAgentBase):
    def __init__(self, model: IModel, conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_data: Union[str, IMessage], model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        return prediction

```

```swarmauri/standard/agents/concrete/SingleCommandAgent.py

from typing import Any, Optional

from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase

class SingleCommandAgent(AgentBase):
    def __init__(self, model: IModel, 
                 conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_str: Optional[str] = None) -> Any:
        model = self.model
        prediction = model.predict(input_str)
        
        return prediction

```

```swarmauri/standard/agents/concrete/SimpleSwarmAgent.py

from typing import Any, Optional

from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation


from swarmauri.standard.agents.base.SwarmAgentBase import AgentBase
from swarmauri.standard.messages.concrete import HumanMessage

class SimpleSwarmAgent(AgentBase):
    def __init__(self, model: IModel, 
                 conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_str: Optional[str] = None) -> Any:
        conversation = self.conversation
        model = self.model

        # Construct a new human message (for example purposes)
        if input_str:
            human_message = HumanMessage(input_str)
            conversation.add_message(human_message)
        
        messages = conversation.as_dict()
        prediction = model.predict(messages=messages)
        return prediction

```

```swarmauri/standard/agents/concrete/MultiPartyChatSwarmAgent.py

from typing import Any, Optional, Union, Dict

from swarmauri.core.models.IModel import IModel
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase
from swarmauri.standard.conversations.concrete.SharedConversation import SharedConversation
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage

class MultiPartyChatSwarmAgent(ConversationAgentBase, NamedAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: SharedConversation,
                 name: str):
        ConversationAgentBase.__init__(self, model, conversation)
        NamedAgentBase.__init__(self, name)

    def exec(self, input_data: Union[str, IMessage] = "", model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        if input_data != "":
            # Add the human message to the conversation
            conversation.add_message(human_message, sender_id=self.name)
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()

        
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        # Create an AgentMessage instance with the model's response and update the conversation
        if prediction != '':
            agent_message = AgentMessage(prediction)
            conversation.add_message(agent_message, sender_id=self.name)
        
        return prediction

```

```swarmauri/standard/agents/concrete/MultiPartyToolAgent.py

from typing import Any, Optional, Union, Dict
import json

from swarmauri.core.models.IModel import IModel
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.ToolAgentBase import ToolAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage


class MultiPartyToolAgent(ToolAgentBase, NamedAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation, 
                 toolkit: IToolkit,
                 name: str):
        ToolAgentBase.__init__(self, model, conversation, toolkit)
        NamedAgentBase.__init__(self, name)

    def exec(self, input_data: Union[str, IMessage], model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model
        toolkit = self.toolkit
        

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        if input_data != "":
            # Add the human message to the conversation
            conversation.add_message(human_message, sender_id=self.name)
            
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        

        if model_kwargs:
            prediction = model.predict(messages=messages, 
                                   tools=toolkit.tools, 
                                   tool_choice="auto",
                                   **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        
        
        prediction_message = prediction.choices[0].message
        agent_response = prediction_message.content
        
        agent_message = AgentMessage(content=prediction_message.content, 
                                     tool_calls=prediction_message.tool_calls)
        conversation.add_message(agent_message, sender_id=self.name)
        
        tool_calls = prediction.choices[0].message.tool_calls
        if tool_calls:
        
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message, sender_id=self.name)
            
            
            messages = conversation.as_dict()
            rag_prediction = model.predict(messages=messages, 
                                           tools=toolkit.tools, 
                                           tool_choice="none")
            
            prediction_message = rag_prediction.choices[0].message
            
            agent_response = prediction_message.content
            if agent_response != "":
                agent_message = AgentMessage(agent_response)
                conversation.add_message(agent_message, sender_id=self.name)
            prediction = rag_prediction
            
        return agent_response 
    

```

```swarmauri/standard/agents/concrete/RagAgent.py

from typing import Any, Optional, Union, Dict
from swarmauri.core.messages import IMessage
from swarmauri.core.models.IModel import IModel
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.agents.base.VectorStoreAgentBase import VectorStoreAgentBase
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

class RagAgent(VectorStoreAgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    def __init__(self, name: str, model: IModel, conversation: SystemContextBase, vector_store: VectorDocumentStoreRetrieveBase):
        super().__init__(name=name, model=model, conversation=conversation, vector_store=vector_store)

    def exec(self, 
             input_data: Union[str, IMessage], 
             top_k: int = 5, 
             model_kwargs: Optional[Dict] = {}
             ) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")
        
        # Add the human message to the conversation
        conversation.add_message(human_message)
        
        
        
        similar_documents = self.vector_store.retrieve(query=input_data, top_k=top_k)
        substr = '\n'.join([doc.content for doc in similar_documents])
        
        # Use substr to set system context
        system_context = SystemMessage(substr)
        conversation.system_context = system_context
        

        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
            
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        return prediction
    
    
    


```

```swarmauri/standard/agents/concrete/GenerativeRagAgent.py

from typing import Any, Optional, Union, Dict
from swarmauri.core.messages import IMessage
from swarmauri.core.models.IModel import IModel
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.agents.base.DocumentAgentBase import DocumentAgentBase
from swarmauri.standard.document_stores.base.DocumentStoreRetrieveBase import DocumentStoreRetrieveBase
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.chunkers.concrete.MdSnippetChunker import MdSnippetChunker
from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

class GenerativeRagAgent(DocumentAgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    def __init__(self, name: str, model: IModel, conversation: SystemContextBase, document_store: DocumentStoreRetrieveBase):
        super().__init__(name=name, model=model, conversation=conversation, document_store=document_store)

    def exec(self, 
             input_data: Union[str, IMessage], 
             top_k: int = 5, 
             model_kwargs: Optional[Dict] = {}
             ) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")
        
        # Add the human message to the conversation
        conversation.add_message(human_message)
        
        
        
        similar_documents = self.document_store.retrieve(query=input_data, top_k=top_k)
        substr = '\n'.join([doc.content for doc in similar_documents])
        
        # Use substr to set system context
        system_context = SystemMessage(substr)
        conversation.system_context = system_context
        

        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
            
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        chunker = MdSnippetChunker()
        
        new_documents = [Document(doc_id=self.document_store.document_count()+1,
                                     content=each[2], 
                                     metadata={"source": "RagSaverAgent", 
                                               "language": each[1],
                                               "comments": each[0]})
                     for each in chunker.chunk_text(prediction)]

        self.document_store.add_documents(new_documents)
        
        return prediction
    
    
    


```

```swarmauri/standard/utils/__init__.py



```

```swarmauri/standard/utils/load_documents_from_json.py

import json
from typing import List
from swarmauri.standard.documents.concrete.Document import Document

def load_documents_from_json(json_file_path):
    documents = []
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    documents = [Document(id=str(_), content=doc['content'], metadata={"document_name": doc['document_name']}) for _, doc in enumerate(data) if doc['content']]
    return documents

```

```swarmauri/standard/conversations/__init__.py



```

```swarmauri/standard/conversations/base/__init__.py



```

```swarmauri/standard/conversations/base/ConversationBase.py

from abc import ABC
from typing import List, Union
from ....core.messages.IMessage import IMessage
from ....core.conversations.IConversation import IConversation

class ConversationBase(IConversation, ABC):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    
    def __init__(self):
        self._history: List[IMessage] = []

    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        return self._history
    
    def add_message(self, message: IMessage):
        self._history.append(message)

    def get_last(self) -> Union[IMessage, None]:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self):
        self._history.clear()

    def as_dict(self) -> List[dict]:
        return [message.as_dict() for message in self.history] # This must utilize the public self.history
    
    
    # def __repr__(self):
        # return repr([message.as_dict() for message in self._history])

```

```swarmauri/standard/conversations/base/SystemContextBase.py

from abc import ABC
from typing import Optional, Union
from swarmauri.core.conversations.ISystemContext import ISystemContext
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class SystemContextBase(ConversationBase, ISystemContext, ABC):
    def __init__(self, *args, system_message_content: Optional[SystemMessage] = None):
        ConversationBase.__init__(self)
        # Automatically handle both string and SystemMessage types for initializing system context
        self._system_context = None  # Initialize with None
        if system_message_content:
            self.system_context = system_message_content
    
    @property
    def system_context(self) -> Union[SystemMessage, None]:
        """Get the system context message. Raises an error if it's not set."""
        if self._system_context is None:
            raise ValueError("System context has not been set.")
        return self._system_context
    
    @system_context.setter
    def system_context(self, new_system_message: Union[SystemMessage, str]) -> None:
        """
        Set a new system context message. The new system message can be a string or 
        an instance of SystemMessage. If it's a string, it converts it to a SystemMessage.
        """
        if isinstance(new_system_message, SystemMessage):
            self._system_context = new_system_message
        elif isinstance(new_system_message, str):
            self._system_context = SystemMessage(new_system_message)
        else:
            raise ValueError("System context must be a string or a SystemMessage instance.")

```

```swarmauri/standard/conversations/concrete/__init__.py



```

```swarmauri/standard/conversations/concrete/LimitedSizeConversation.py

from ..base.ConversationBase import ConversationBase
from ....core.messages.IMessage import IMessage
from ....core.conversations.IMaxSize import IMaxSize

class LimitedSizeConversation(ConversationBase, IMaxSize):
    def __init__(self, max_size: int):
        super().__init__()
        self._max_size = max_size
        
    @property
    def max_size(self) -> int:
        """
        Provides read-only access to the conversation history.
        """
        return self._max_size
    
    @max_size.setter
    def max_size(self, new_max_size: int) -> int:
        """
        Provides read-only access to the conversation history.
        """
        if new_max_size > 0:
            self._max_size = int
        else:
            raise ValueError('Cannot set conversation size to 0.')


    def add_message(self, message: IMessage):
        """Adds a message and ensures the conversation does not exceed the max size."""
        super().add_message(message)
        self._enforce_max_size_limit()

    def _enforce_max_size_limit(self):
        """
        Enforces the maximum size limit of the conversation history.
        If the current history size exceeds the maximum size, the oldest messages are removed.
        """
        while len(self._history) > self.max_size:
            self._history.pop(0)

```

```swarmauri/standard/conversations/concrete/SimpleConversation.py

from typing import List, Union
from ....core.messages.IMessage import IMessage
from ..base.ConversationBase import ConversationBase

class SimpleConversation(ConversationBase):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    
    def __init__(self):
       super().__init__()

```

```swarmauri/standard/conversations/concrete/LimitedSystemContextConversation.py

from typing import Optional, Union, List
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class LimitedSystemContextConversation(SystemContextBase, IMaxSize):
    def __init__(self, max_size: int, system_message_content: Optional[SystemMessage] = None):
        """
        Initializes the conversation with a system context message and a maximum history size.
        
        Parameters:
            max_size (int): The maximum number of messages allowed in the conversation history.
            system_message_content (Optional[str], optional): The initial system message content. Can be a string.
        """
        SystemContextBase.__init__(self, system_message_content=system_message_content if system_message_content else "")  # Initialize SystemContext with a SystemMessage
        self._max_size = max_size  # Set the maximum size
    
    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        
        
        res = [] 
        res.append(self.system_context)
        res.extend(self._history)
        return res
        
        
    @property
    def max_size(self) -> int:
        """
        Provides access to the max_size property.
        """
        return self._max_size
    
    @max_size.setter
    def max_size(self, new_max_size: int) -> None:
        """
        Sets a new maximum size for the conversation history.
        """
        if new_max_size <= 0:
            raise ValueError("max_size must be greater than 0.")
        self._max_size = new_max_size

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        else:
            super().add_message(message)
        self._enforce_max_size_limit()
        
    def _enforce_max_size_limit(self):
        """
        Remove messages from the beginning of the conversation history if the limit is exceeded.
        """
        while len(self._history) + 1 > self._max_size:
            self._history.pop(0)

    @property
    def system_context(self) -> Union[SystemMessage, None]:
        """Get the system context message. Raises an error if it's not set."""
        if self._system_context is None:
            raise ValueError("System context has not been set.")
        return self._system_context


    @system_context.setter
    def system_context(self, new_system_message: Union[SystemMessage, str]) -> None:
        """
        Set a new system context message. The new system message can be a string or 
        an instance of SystemMessage. If it's a string, it converts it to a SystemMessage.
        """
        if isinstance(new_system_message, SystemMessage):
            self._system_context = new_system_message
        elif isinstance(new_system_message, str):
            self._system_context = SystemMessage(new_system_message)
        else:
            raise ValueError("System context must be a string or a SystemMessage instance.")
            

```

```swarmauri/standard/conversations/concrete/SharedConversation.py

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

```swarmauri/standard/documents/__init__.py

from .concrete import *
from .base import *

```

```swarmauri/standard/documents/base/__init__.py

from .DocumentBase import DocumentBase
from .EmbeddedBase import EmbeddedBase

```

```swarmauri/standard/documents/base/EmbeddedBase.py

from abc import ABC
from typing import List, Any, Optional
import importlib
from swarmauri.core.documents.IEmbed import IEmbed
from swarmauri.standard.vectors.base.VectorBase import VectorBase
from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class EmbeddedBase(DocumentBase, IEmbed, ABC):
    def __init__(self, id: str = "", content: str = "", metadata: dict = {}, embedding: VectorBase = None):
        DocumentBase.__init__(self, id, content, metadata)
        self._embedding = embedding
        
    @property
    def embedding(self) -> VectorBase:
        return self._embedding

    @embedding.setter
    def embedding(self, value: VectorBase) -> None:
        self._embedding = value

    def __str__(self):
        return f"EmbeddedDocument ID: {self.id}, Content: {self.content}, Metadata: {self.metadata}, embedding={self.embedding}"

    def __repr__(self):
        return f"EmbeddedDocument(id={self.id}, content={self.content}, metadata={self.metadata}, embedding={self.embedding})"

    def to_dict(self):
        document_dict = super().to_dict()
        document_dict.update({
            "type": self.__class__.__name__,
            "embedding": self.embedding.to_dict() if hasattr(self.embedding, 'to_dict') else self.embedding
            })

        return document_dict

    @classmethod
    def from_dict(cls, data):
        vector_data = data.pop("embedding")
        if vector_data:
            vector_type = vector_data.pop('type')
            if vector_type:
                module = importlib.import_module(f"swarmauri.standard.vectors.concrete.{vector_type}")
                vector_class = getattr(module, vector_type)
                vector = vector_class.from_dict(vector_data)
            else:
                vector = None
        else:
            vector = None 
        return cls(**data, embedding=vector)

```

```swarmauri/standard/documents/base/DocumentBase.py

from abc import ABC, abstractmethod
from typing import Dict
from swarmauri.core.documents.IDocument import IDocument

class DocumentBase(IDocument, ABC):
    
    def __init__(self, id: str = "", content: str = "", metadata: dict = {}):
        self._id = id
        self._content = content
        self._metadata = metadata

    @property
    def id(self) -> str:
        """
        Get the document's ID.
        """
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """
        Set the document's ID.
        """
        self._id = value

    @property
    def content(self) -> str:
        """
        Get the document's content.
        """
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """
        Set the document's content.
        """
        if value:
            self._content = value
        else:
            raise ValueError('Cannot create a document with no content.')

    @property
    def metadata(self) -> Dict:
        """
        Get the document's metadata.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict) -> None:
        """
        Set the document's metadata.
        """
        self._metadata = value

    def __str__(self):
        return f"Document ID: {self.id}, Content: {self.content}, Metadata: {self.metadata}"

    def __repr__(self):
        return f"Document(id={self.id}, content={self.content}, metadata={self.metadata})"

    def to_dict(self):
        return {'type': self.__class__.__name__,
                'id': self.id, 
                'content': self.content, 
                'metadata': self.metadata}
      
    @classmethod
    def from_dict(cls, data):
        data.pop("type", None)
        return cls(**data)


```

```swarmauri/standard/documents/concrete/__init__.py

from .Document import Document
from .EmbeddedDocument import EmbeddedDocument

```

```swarmauri/standard/documents/concrete/EmbeddedDocument.py

from typing import Optional, Any
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.documents.base.EmbeddedBase import EmbeddedBase

class EmbeddedDocument(EmbeddedBase):
    def __init__(self, id,  content, metadata, embedding: Optional[IVector] = None):
        EmbeddedBase.__init__(self, id=id, content=content, metadata=metadata, embedding=embedding)


```

```swarmauri/standard/documents/concrete/Document.py

from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class Document(DocumentBase):
    pass
    
        


```

```swarmauri/standard/messages/__init__.py



```

```swarmauri/standard/messages/base/__init__.py



```

```swarmauri/standard/messages/base/MessageBase.py

from abc import ABC, abstractmethod
from swarmauri.core.messages.IMessage import IMessage

class MessageBase(IMessage, ABC):
    
    @abstractmethod
    def __init__(self, role: str, content: str):
        self._role = role
        self._content = content
    
    @property
    def role(self) -> str:
        return self._role
    
    @property
    def content(self) -> str:
        return self._content

    
    def as_dict(self) -> dict:
        """
        Dynamically return a dictionary representation of the object,
        including all properties.
        """
        result_dict = {}
        # Iterate over all attributes
        for attr in dir(self):
            # Skip private attributes and anything not considered a property
            if attr.startswith("_") or callable(getattr(self, attr)):
                continue
            result_dict[attr] = getattr(self, attr)
            
        return result_dict

    def __repr__(self) -> str:
        """
        Return the string representation of the ConcreteMessage.
        """
        return f"{self.__class__.__name__}(role='{self.role}')"
    
    def __getattr__(self, name):
        """
        Return the value of the named attribute of the instance.
        """
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    
    def __setattr__(self, name, value):
        """
        Set the value of the named attribute of the instance.
        """
        self.__dict__[name] = value

```

```swarmauri/standard/messages/concrete/__init__.py

from .HumanMessage import HumanMessage
from .AgentMessage import AgentMessage
from .FunctionMessage import FunctionMessage
from .SystemMessage import SystemMessage

```

```swarmauri/standard/messages/concrete/AgentMessage.py

from typing import Optional, Any
from swarmauri.standard.messages.base.MessageBase import MessageBase


class AgentMessage(MessageBase):
    def __init__(self, content, tool_calls: Optional[Any] = None):
        super().__init__(role='assistant', content=content)
        if tool_calls:
            self.tool_calls = tool_calls

```

```swarmauri/standard/messages/concrete/HumanMessage.py

from swarmauri.standard.messages.base.MessageBase import MessageBase

class HumanMessage(MessageBase):
    """
    Represents a message created by a human user.

    Extends the `Message` class to specifically represent messages input by human users in a conversational
    interface. It contains the message content and assigns the type "HumanMessage" to distinguish it from
    other types of messages.
    """

    def __init__(self, content, name=None):
        """
        Initializes a new instance of HumanMessage with specified content.

        Args:
            content (str): The text content of the human-created message.
            name (str, optional): The name of the human sender.
        """
        super().__init__(role='user', content=content)



```

```swarmauri/standard/messages/concrete/FunctionMessage.py

from swarmauri.standard.messages.base.MessageBase import MessageBase


class FunctionMessage(MessageBase):
    """
    Represents a message created by a human user.

    This class extends the `Message` class to specifically represent messages that
    are input by human users in a conversational interface. It contains the message
    content and assigns the type "HumanMessage" to distinguish it from other types
    of messages.

    Attributes:
        content (str): The text content of the message.

    Methods:
        display: Returns a dictionary representation of the message for display,
                 tagging it with the role "user".
    """

    def __init__(self, content, name, tool_call_id):
        super().__init__(role='tool', content=content)
        self.name = name
        self.tool_call_id = tool_call_id
    

```

```swarmauri/standard/messages/concrete/SystemMessage.py

from swarmauri.standard.messages.base.MessageBase import MessageBase

class SystemMessage(MessageBase):
    """
    SystemMessage class represents a message generated by the system. 
    
    This type of message is used to communicate system-level information such as 
    errors, notifications, or updates to the user. Inherits from the Message base class.
    
    Attributes:
        content (str): The content of the system message.
    """
    
    def __init__(self, content):
        super().__init__(role='system', content=content)
    


```

```swarmauri/standard/parsers/__init__.py



```

```swarmauri/standard/parsers/base/__init__.py



```

```swarmauri/standard/parsers/concrete/__init__.py



```

```swarmauri/standard/parsers/concrete/CSVParser.py

import csv
from io import StringIO
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class CSVParser(IParser):
    """
    Concrete implementation of IParser for parsing CSV formatted text into Document instances.

    The parser can handle input as a CSV formatted string or from a file, with each row
    represented as a separate Document. Assumes the first row is the header which will
    be used as keys for document metadata.
    """

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
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class EntityRecognitionParser(IParser):
    """
    EntityRecognitionParser leverages NER capabilities to parse text and 
    extract entities with their respective tags such as PERSON, LOCATION, ORGANIZATION, etc.
    """

    def __init__(self):
        # Load a SpaCy model. The small model is used for demonstration; larger models provide improved accuracy.
        self.nlp = spacy.load("en_core_web_sm")
    
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
        doc = self.nlp(text)

        # Compile identified entities into documents
        entities_docs = []
        for ent in doc.ents:
            # Create a document for each entity with metadata carrying entity type
            entity_doc = Document(doc_id=ent.text, content=ent.text, metadata={"entity_type": ent.label_})
            entities_docs.append(entity_doc)
        
        return entities_docs

```

```swarmauri/standard/parsers/concrete/HtmlTagStripParser.py

from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
import html
import re

class HTMLTagStripParser(IParser):
    """
    A concrete parser that removes HTML tags and unescapes HTML content,
    leaving plain text.
    """

    def parse(self, data):
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
        document = Document(doc_id="1", content=text, metadata={"original_length": len(data)})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/KeywordExtractorParser.py

import yake
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class KeywordExtractorParser(IParser):
    """
    Extracts keywords from text using the YAKE keyword extraction library.
    """

    def __init__(self, lang: str = 'en', num_keywords: int = 10):
        """
        Initialize the keyword extractor with specified language and number of keywords.

        Parameters:
        - lang (str): The language of the text for keyword extraction. Default is 'en' for English.
        - num_keywords (int): The number of top keywords to extract. Default is 10.
        """
        self.lang = lang
        self.num_keywords = num_keywords
        # Initialize YAKE extractor with specified parameters
        self.kw_extractor = yake.KeywordExtractor(lan=lang, n=3, dedupLim=0.9, dedupFunc='seqm', windowsSize=1, top=num_keywords, features=None)

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Extract keywords from input text and return as list of IDocument instances containing keyword information.

        Parameters:
        - data (Union[str, Any]): The input text from which to extract keywords.

        Returns:
        - List[IDocument]: A list of IDocument instances, each containing information about an extracted keyword.
        """
        # Ensure data is in string format for analysis
        text = str(data) if not isinstance(data, str) else data

        # Extract keywords using YAKE
        keywords = self.kw_extractor.extract_keywords(text)

        # Create Document instances for each keyword
        documents = [Document(doc_id=str(index), content=keyword, metadata={"score": score}) for index, (keyword, score) in enumerate(keywords)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/MarkdownParser.py

import re
from markdown import markdown
from bs4 import BeautifulSoup
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class MarkdownParser(IParser):
    """
    A concrete implementation of the IParser interface that parses Markdown text.
    
    This parser takes Markdown formatted text, converts it to HTML using Python's
    markdown library, and then uses BeautifulSoup to extract plain text content. The
    resulting plain text is then wrapped into IDocument instances.
    """
    
    def parse(self, data: str) -> list[IDocument]:
        """
        Parses the input Markdown data into a list of IDocument instances.
        
        Parameters:
        - data (str): The input Markdown formatted text to be parsed.
        
        Returns:
        - list[IDocument]: A list containing a single IDocument instance with the parsed text content.
        """
        # Convert Markdown to HTML
        html_content = markdown(data)
        
        # Use BeautifulSoup to extract text content from HTML
        soup = BeautifulSoup(html_content, features="html.parser")
        plain_text = soup.get_text(separator=" ", strip=True)
        
        # Generate a document ID
        doc_id = "1"  # For this implementation, a simple fixed ID is used. 
                      # A more complex system might generate unique IDs for each piece of text.

        # Create and return a list containing the single extracted plain text document
        document = Document(doc_id=doc_id, content=plain_text, metadata={"source_format": "markdown"})
        return [document]

```

```swarmauri/standard/parsers/concrete/OpenAPISpecParser.py

from typing import List, Union, Any
import yaml
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class OpenAPISpecParser(IParser):
    """
    A parser that processes OpenAPI Specification files (YAML or JSON format)
    and extracts information into structured Document instances. 
    This is useful for building documentation, APIs inventory, or analyzing the API specification.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
                doc_id = f"{path}_{method}"
                content = yaml.dump(operation)
                metadata = {
                    "path": path,
                    "method": method.upper(),
                    "operationId": operation.get("operationId", "")
                }
                document = Document(doc_id=doc_id, content=content, metadata=metadata)
                documents.append(document)

        return documents

```

```swarmauri/standard/parsers/concrete/PhoneNumberExtractorParser.py

import re
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class PhoneNumberExtractorParser(IParser):
    """
    A parser that extracts phone numbers from the input text.
    Utilizes regular expressions to identify phone numbers in various formats.
    """

    def __init__(self):
        """
        Initializes the PhoneNumberExtractorParser.
        """
        super().__init__()

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
        documents = [Document(doc_id=str(index), content=phone_number, metadata={}) for index, phone_number in enumerate(phone_numbers)]

        return documents

```

```swarmauri/standard/parsers/concrete/PythonParser.py

from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
import ast
import uuid

class PythonParser(IParser):
    """
    A parser that processes Python source code to extract structural elements
    such as functions, classes, and their docstrings.
    
    This parser utilizes the `ast` module to parse the Python code into an abstract syntax tree (AST)
    and then walks the tree to extract relevant information.
    """
    
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
                
                # Generate a unique ID for each element
                doc_id = str(uuid.uuid4())
                
                # Create a metadata dictionary
                metadata = {
                    "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                    "name": element_name,
                    "docstring": docstring
                }
                
                # Create a Document for each structural element
                document = Document(doc_id=doc_id, content=docstring, metadata=metadata)
                documents.append(document)
                
        return documents

```

```swarmauri/standard/parsers/concrete/RegExParser.py

import re
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class RegExParser(IParser):
    """
    A parser that uses a regular expression to extract information from text.
    """

    def __init__(self, pattern: str):
        """
        Initializes the RegExParser with a specific regular expression pattern.

        Parameters:
        - pattern (str): The regular expression pattern used for parsing the text.
        """
        self.pattern = pattern

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
        matches = re.findall(self.pattern, data)

        # Create a Document for each match and collect them into a list
        documents = [Document(doc_id=str(i+1), content=match, metadata={}) for i, match in enumerate(matches)]

        return documents

```

```swarmauri/standard/parsers/concrete/TextBlobNounParser.py

from typing import List, Union, Any
from textblob import TextBlob
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class TextBlobNounParser(IParser):
    """
    A concrete implementation of IParser using TextBlob for Natural Language Processing tasks.
    
    This parser leverages TextBlob's functionalities such as noun phrase extraction, 
    sentiment analysis, classification, language translation, and more for parsing texts.
    """
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
        document = Document(doc_id="0", content=data, metadata={"noun_phrases": noun_phrases})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/TextBlobSentenceParser.py

from textblob import TextBlob
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
from typing import List, Union, Any

class TextBlobParser(IParser):
    """
    A parser that leverages TextBlob to break text into sentences.

    This parser uses the natural language processing capabilities of TextBlob
    to accurately identify sentence boundaries within large blocks of text.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
            Document(doc_id=str(index), content=str(sentence), metadata={'parser': 'TextBlobParser'})
            for index, sentence in enumerate(sentences)
        ]

        return documents

```

```swarmauri/standard/parsers/concrete/TFIDFParser.py

from sklearn.feature_extraction.text import TfidfVectorizer
from swarmauri.core.parsers.IParser import IParser
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document

class TFIDFParser(IParser):
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        super().__init__()

    def parse(self, data):
        # Assuming `data` is a list of strings (documents)
        tfidf_matrix = self.vectorizer.fit_transform(data)
        # Depending on how you want to use the output, you could return Document objects
        # For demonstration, let's return a list of IDocument with vectorized content
        documents = [Document(doc_id=str(i), content=vector, metadata={}) for i, vector in enumerate(tfidf_matrix.toarray())]
        return documents

```

```swarmauri/standard/parsers/concrete/URLExtractorParser.py

from typing import List, Union, Any
from urllib.parse import urlparse
import re
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class URLExtractorParser(IParser):
    """
    A concrete implementation of IParser that extracts URLs from text.
    
    This parser scans the input text for any URLs and creates separate
    documents for each extracted URL. It utilizes regular expressions
    to identify URLs within the given text.
    """

    def __init__(self):
        """
        Initializes the URLExtractorParser.
        """
        super().__init__()
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
        documents = [Document(doc_id=str(i), content=url, metadata={"source": "URLExtractor"}) for i, url in enumerate(urls)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/XMLParser.py

import xml.etree.ElementTree as ET
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class XMLParser(IParser):
    """
    A parser that extracts information from XML data and converts it into IDocument objects.
    This parser assumes a simple use-case where each targeted XML element represents a separate document.
    """

    def __init__(self, element_tag: str):
        """
        Initialize the XMLParser with the tag name of the XML elements to be extracted as documents.

        Parameters:
        - element_tag (str): The tag name of XML elements to parse into documents.
        """
        self.element_tag = element_tag

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
            doc = Document(doc_id=None, content=content, metadata=metadata)
            documents.append(doc)

        return documents

```

```swarmauri/standard/parsers/concrete/BERTEmbeddingParser.py

from typing import List, Union, Any
from transformers import BertTokenizer, BertModel
import torch
from swarmauri.core.parsers.IParser import IParser
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document

class BERTEmbeddingParser(IParser):
    """
    A parser that transforms input text into document embeddings using BERT.
    
    This parser tokenizes the input text, passes it through a pre-trained BERT model,
    and uses the resulting embeddings as the document content.
    """

    def __init__(self, model_name: str = 'bert-base-uncased'):
        """
        Initializes the BERTEmbeddingParser with a specific BERT model.
        
        Parameters:
        - model_name (str): The name of the pre-trained BERT model to use.
        """
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()  # Set model to evaluation mode

    
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
            outputs = self.model(**inputs)

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

```swarmauri/standard/prompts/concrete/__init__.py



```

```swarmauri/standard/prompts/concrete/Prompt.py

from swarmauri.core.prompts.IPrompt import IPrompt

class Prompt(IPrompt):
    """
    The ChatPrompt class represents a simple, chat-like prompt system where a 
    message can be set and retrieved as needed. It's particularly useful in 
    applications involving conversational agents, chatbots, or any system that 
    requires dynamic text-based interactions.
    """

    def __init__(self, prompt: str = ""):
        """
        Initializes an instance of ChatPrompt with an optional initial message.
        
        Parameters:
        - message (str, optional): The initial message for the prompt. Defaults to an empty string.
        """
        self.prompt = prompt

    def __call__(self, prompt):
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

```swarmauri/standard/prompts/concrete/PromptTemplate.py

from typing import Dict, List
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate

class PromptTemplate(IPrompt, ITemplate):
    """
    A class for generating prompts based on a template and variables.
    Implements the IPrompt for generating prompts and ITemplate for template manipulation.
    """

    def __init__(self, template: str = "", variables: List[Dict[str, str]] = []):
        self._template = template
        self._variables_list = variables

    @property
    def template(self) -> str:
        """
        Get the current prompt template.
        """
        return self._template

    @template.setter
    def template(self, value: str) -> None:
        """
        Set a new template string for the prompt.
        """
        self._template = value

    @property
    def variables(self) -> List[Dict[str, str]]:
        """
        Get the current set of variables for the template.
        """
        return self._variables_list 

    @variables.setter
    def variables(self, value: List[Dict[str, str]]) -> None:
        if not isinstance(value, list):
            raise ValueError("Variables must be a list of dictionaries.")
        self._variables_list = value

    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.
        """
        self._template = template

    def set_variables(self, variables: Dict[str, str]) -> None:
        """
        Sets or updates the variables to be substituted into the template.
        """
        self._variables_list = variables

    def generate_prompt(self, variables: List[Dict[str, str]] = None) -> str:
        variables = variables.pop(0) or (self._variables_list.pop(0) if self._variables_list else {})
        return self._template.format(**variables)

    def __call__(self, variables: List[Dict[str, str]]) -> str:
        """
        Generates a prompt using the current template and provided keyword arguments for substitution.
        """
        return self.generate_prompt(variables)

```

```swarmauri/standard/prompts/concrete/PromptGenerator.py

from typing import Dict, List, Generator
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate


class PromptGenerator(IPrompt, ITemplate):
    """
    A class that generates prompts based on a template and a list of variable sets.
    It implements the IPrompt and ITemplate interfaces.
    """

    def __init__(self, template: str = "", variables: List[Dict[str, str]] = []):
        self._template = template
        self._variables_list = variables

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, value: str) -> None:
        self._template = value

    @property
    def variables(self) -> List[Dict[str, str]]:
        return self._variables_list

    @variables.setter
    def variables(self, value: List[Dict[str, str]]) -> None:
        if not isinstance(value, list):
            raise ValueError("Expected a list of dictionaries for variables.")
        self._variables_list = value

    def set_template(self, template: str) -> None:
        self._template = template

    def set_variables(self, variables: List[Dict[str, str]]) -> None:
        self.variables = variables

    def generate_prompt(self, **kwargs) -> str:
        """
        Generates a prompt using the provided variables if any, 
        else uses the next variables set in the list.
        """
        variables = kwargs if kwargs else self.variables.pop(0) if self.variables else {}
        return self._template.format(**variables)

    def __call__(self) -> Generator[str, None, None]:
        """
        Returns a generator that yields prompts constructed from the template and 
        each set of variables in the variables list.
        """
        for variables_set in self._variables_list:
            yield self.generate_prompt(**variables_set)
        self._variables_list = []  # Reset the list after all prompts have been generated.

```

```swarmauri/standard/states/__init__.py



```

```swarmauri/standard/states/base/__init__.py



```

```swarmauri/standard/states/concrete/__init__.py



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
from typing import Dict
from ....core.toolkits.IToolkit import IToolkit
from ....core.tools.ITool import ITool  

class ToolkitBase(IToolkit, ABC):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    @abstractmethod
    def __init__(self, initial_tools: Dict[str, ITool] = None):
        """
        Initialize the Toolkit with an optional dictionary of initial tools.
        """
        # If initial_tools is provided, use it; otherwise, use an empty dictionary
        self._tools = initial_tools if initial_tools is not None else {}

    @property
    def tools(self) -> Dict[str, ITool]:
        return [self._tools[tool].as_dict() for tool in self._tools]

    def add_tools(self, tools: Dict[str, ITool]):
        """
        Add multiple tools to the toolkit.

        Parameters:
            tools (Dict[str, Tool]): A dictionary of tool objects keyed by their names.
        """
        self._tools.update(tools)

    def add_tool(self, tool: ITool):
        """
        Add a single tool to the toolkit.

        Parameters:
            tool (Tool): The tool instance to be added to the toolkit.
        """
        self._tools[tool.function['name']] = tool

    def remove_tool(self, tool_name: str):
        """
        Remove a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to be removed from the toolkit.
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def get_tool_by_name(self, tool_name: str) -> ITool:
        """
        Get a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to retrieve.

        Returns:
            Tool: The tool instance with the specified name.
        """
        if tool_name in self._tools:
            return self._tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def __len__(self) -> int:
        """
        Returns the number of tools in the toolkit.

        Returns:
            int: The number of tools in the toolkit.
        """
        return len(self._tools)

```

```swarmauri/standard/toolkits/concrete/__init__.py



```

```swarmauri/standard/toolkits/concrete/Toolkit.py

from typing import Dict
from ..base.ToolkitBase import ToolkitBase
from ....core.tools.ITool import ITool

class Toolkit(ToolkitBase):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    def __init__(self, initial_tools: Dict[str, ITool] = None):
        """
        Initialize the Toolkit with an optional dictionary of initial tools.
        """
        
        super().__init__(initial_tools)
    

```

```swarmauri/standard/tools/__init__.py



```

```swarmauri/standard/tools/base/__init__.py



```

```swarmauri/standard/tools/base/ToolBase.py

from typing import Optional, List, Any
from abc import ABC, abstractmethod
import json
from swarmauri.core.tools.ITool import ITool
        
class ToolBase(ITool, ABC):
    
    @abstractmethod
    def __init__(self, name, description, parameters=[]):
        self._name = name
        self._description = description
        self._parameters = parameters
        self.type = "function"
        self.function = {
            "name": name,
            "description": description,
        }
        
        # Dynamically constructing the parameters schema
        properties = {}
        required = []
        
        for param in parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)
        
        self.function['parameters'] = {
            "type": "object",
            "properties": properties,
        }
        
        if required:  # Only include 'required' if there are any required parameters
            self.function['parameters']['required'] = required


    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def parameters(self):
        return self._parameters

    def __iter__(self):
        yield ('type', self.type)
        yield ('function', self.function)
        

    def as_dict(self):
        return {'type': self.type, 'function': self.function}
        # return self.__dict__

    def to_json(obj):
        return json.dumps(obj, default=lambda obj: obj.__dict__)

    def __getstate__(self):
        return {'type': self.type, 'function': self.function}


    def __call__(self, *args, **kwargs):
        """
        Placeholder method for executing the functionality of the tool.
        Subclasses should override this method to define specific tool behaviors.

        Parameters:
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        """
        raise NotImplementedError("Subclasses must implement the call_function method.")

```

```swarmauri/standard/tools/concrete/__init__.py



```

```swarmauri/standard/tools/concrete/TestTool.py

import json
import subprocess as sp
from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class TestTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="program",
                type="string",
                description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
                required=True,
                enum=["notepad", "calc", "mspaint"]
            )
        ]
        
        super().__init__(name="TestTool", 
                         description="This opens a program based on the user's request.", 
                         parameters=parameters)

    def __call__(self, program) -> str:
        # sp.check_output(program)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Program Opened: {program}\n"


```

```swarmauri/standard/tools/concrete/WeatherTool.py

import json
from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class WeatherTool(ToolBase):
    def __init__(self):
        parameters = [
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
        ]
        
        super().__init__(name="WeatherTool", description="Fetch current weather info for a location", parameters=parameters)

    def __call__(self, location, unit="fahrenheit") -> str:
        weather_info = (location, unit)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Weather Info: {weather_info}\n"


```

```swarmauri/standard/tools/concrete/Parameter.py

from typing import Optional, List, Any
import json
from ....core.tools.IParameter import IParameter

class Parameter(IParameter):
    """
    A class to represent a parameter for a tool.

    Attributes:
        name (str): Name of the parameter.
        type (str): Data type of the parameter (e.g., 'int', 'str', 'float').
        description (str): A brief description of the parameter.
        required (bool): Whether the parameter is required or optional.
        enum (Optional[List[any]]): A list of acceptable values for the parameter, if any.
    """

    def __init__(self, name: str, type: str, description: str, required: bool = True, enum: Optional[List[Any]] = None):
        """
        Initializes a new instance of the Parameter class.

        Args:
            name (str): The name of the parameter.
            type (str): The type of the parameter.
            description (str): A brief description of what the parameter is used for.
            required (bool, optional): Specifies if the parameter is required. Defaults to True.
            enum (Optional[List[Any]], optional): A list of acceptable values for the parameter. Defaults to None.
        """
        self._name = name
        self._type = type
        self._description = description
        self._required = required
        self._enum = enum
        
    @property
    def name(self) -> str:
        """
        Abstract property for getting the name of the parameter.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Abstract setter for setting the name of the parameter.
        """
        self._name = value

    @property
    def type(self) -> str:
        """
        Abstract property for getting the type of the parameter.
        """
        return self._type

    @type.setter
    def type(self, value: str):
        """
        Abstract setter for setting the type of the parameter.
        """
        self._type = value

    @property
    def description(self) -> str:
        """
        Abstract property for getting the description of the parameter.
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """
        Abstract setter for setting the description of the parameter.
        """
        self._description = value

    @property
    def required(self) -> bool:
        """
        Abstract property for getting the required status of the parameter.
        """
        return self._required

    @required.setter
    def required(self, value: bool):
        """
        Abstract setter for setting the required status of the parameter.
        """
        self._required = value

    @property
    def enum(self) -> Optional[List[Any]]:
        """
        Abstract property for getting the enum list of the parameter.
        """
        return self._enum

    @enum.setter
    def enum(self, value: Optional[List[Any]]):
        """
        Abstract setter for setting the enum list of the parameter.
        """
        self._enum = value

```

```swarmauri/standard/tools/concrete/AdditionTool.py

from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class AdditionTool(ToolBase):
    
    def __init__(self):
        parameters = [
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
        ]
        super().__init__(name="TestTool", 
                         description="This opens a program based on the user's request.", 
                         parameters=parameters)

    def __call__(self, x: int, y: int) -> int:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (int): The first number.
        - y (int): The second number.

        Returns:
        - int: The sum of x and y.
        """
        return x + y

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

```swarmauri/standard/vector_stores/base/VectorDocumentStoreBase.py

import json
from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore

class VectorDocumentStoreBase(IDocumentStore, ABC):
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
    
    def document_dumps(self) -> str:
        return json.dumps([each.to_dict() for each in self.documents])

    def document_dump(self, file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([each.to_dict() for each in self.documents], 
                f,
                ensure_ascii=False, 
                indent=4)  

    def document_loads(self, json_data: str) -> None:
        self.documents = [globals()[each['type']].from_dict(each) for each in json.loads(json_data)]

    def document_load(self, file_path: str) -> None:
        with open(file_path, 'r', encoding='utf-8') as f:
            self.documents = [globals()[each['type']].from_dict(each) for each in json.load(file_path)]



```

```swarmauri/standard/vector_stores/base/VectorDocumentStoreRetrieveBase.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve
from swarmauri.standard.vector_stores.base.VectorDocumentStoreBase import VectorDocumentStoreBase

class VectorDocumentStoreRetrieveBase(VectorDocumentStoreBase, IDocumentRetrieve, ABC):
        
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

```swarmauri/standard/vector_stores/base/SaveLoadStoreBase.py

from typing import List
import os
import json
import glob
import importlib 
from swarmauri.core.vector_stores.ISaveLoadStore import ISaveLoadStore
from swarmauri.standard.documents import DocumentBase
from swarmauri.core.vectorizers.IVectorize import IVectorize

class SaveLoadStoreBase(ISaveLoadStore):
    """
    Base class for vector stores with built-in support for saving and loading
    the vectorizer's model and the documents.
    """
    
    def __init__(self, vectorizer: IVectorize, documents: List[DocumentBase]):
        self.vectorizer = vectorizer
        self.documents = documents
    
    def save_store(self, directory_path: str) -> None:
        """
        Saves both the vectorizer's model and the documents.
        """
        # Ensure the directory exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        # Save the vectorizer model
        model_path = os.path.join(directory_path, "vectorizer_model")
        self.vectorizer.save_model(model_path)
        
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
        model_path = os.path.join(directory_path, "vectorizer_model")
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
        model_path = os.path.join(directory_path, "vectorizer_model")
        parts_directory = f"{directory_path}/parts"
        if not os.path.exists(parts_directory):
            os.makedirs(parts_directory)

        with open(f"{model_path}/model.safetensors", 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                with open(f"{parts_directory}/model.safetensors.part{file_number}", 'wb') as chunk_file:
                    chunk_file.write(chunk)
                file_number += 1
                chunk = f.read(chunk_size)

    def load_parts(self, directory_path: str, file_pattern: str = '*.part*') -> None:
        """
        Combines file parts from a directory back into a single file and loads it.
        """
        model_path = os.path.join(directory_path, "vectorizer_model")
        parts_directory = f"{directory_path}/parts"
        output_file_path = os.path.join(model_path, "model.safetensors")

        parts = sorted(glob.glob(os.path.join(parts_directory, file_pattern)))
        with open(output_file_path, 'wb') as output_file:
            for part in parts:
                with open(part, 'rb') as file_part:
                    output_file.write(file_part.read())

        self.load_store(directory_path)

```

```swarmauri/standard/vector_stores/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/concrete/TFIDFVectorStore.py

from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.vectorizers.concrete.TFIDFVectorizer import TFIDFVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase

class TFIDFVectorStore(VectorDocumentStoreRetrieveBase, SaveLoadStoreBase):
    def __init__(self):
        self.vectorizer = TFIDFVectorizer()
        self.metric = CosineDistance()
        self.documents = []
        SaveLoadStoreBase.__init__(self, self.vectorizer, self.documents)
      

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None

    def get_all_documents(self) -> List[IDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        transform_matrix = self.vectorizer.fit_transform(query, self.documents)

        # The inferred vector is the last vector in the transformed_matrix
        # The rest of the matrix is what we are comparing
        distances = self.metric.distances(transform_matrix[-1], transform_matrix[:-1])  

        # Get the indices of the top_k most similar (least distant) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/vector_stores/concrete/Doc2VecVectorStore.py

from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.Doc2VecVectorizer import Doc2VecVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase    


class Doc2VecVectorStore(VectorDocumentStoreRetrieveBase, SaveLoadStoreBase):
    def __init__(self):
        self.vectorizer = Doc2VecVectorizer()
        self.metric = CosineDistance()
        self.documents = []      
        SaveLoadStoreBase.__init__(self, self.vectorizer, self.documents)

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        self._recalculate_embeddings()

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        self._recalculate_embeddings()

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None

    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        self._recalculate_embeddings()

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break
        self._recalculate_embeddings()

    def _recalculate_embeddings(self):
        # Recalculate document embeddings for the current set of documents
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self.vectorizer.fit_transform(documents_text)

        embedded_documents = [EmbeddedDocument(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count]) for _count, _d in enumerate(self.documents)
            if _d.content]

        self.documents = embedded_documents

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]

        distances = self.metric.distances(query_vector, document_vectors)

        # Get the indices of the top_k least distant (most similar) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/vector_stores/concrete/MLMVectorStore.py

from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.MLMVectorizer import MLMVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase    

class MLMVectorStore(VectorDocumentStoreRetrieveBase, SaveLoadStoreBase):
    def __init__(self):
        self.vectorizer = MLMVectorizer()  # Assuming this is already implemented
        self.metric = CosineDistance()
        self.documents: List[EmbeddedDocument] = []
        SaveLoadStoreBase.__init__(self, self.vectorizer, self.documents)      

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self.vectorizer.fit_transform(documents_text)

        embedded_documents = [EmbeddedDocument(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count])

        for _count, _d in enumerate(self.documents) if _d.content]

        self.documents = embedded_documents

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self.vectorizer.fit_transform(documents_text)

        embedded_documents = [EmbeddedDocument(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count]) for _count, _d in enumerate(self.documents) 
            if _d.content]

        self.documents = embedded_documents

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != doc_id]

    def update_document(self, doc_id: str) -> None:
        raise NotImplementedError('Update_document not implemented on BERTDocumentStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self.metric.distances(query_vector, document_vectors)
        
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

```swarmauri/standard/chunkers/concrete/__init__.py



```

```swarmauri/standard/chunkers/concrete/SlidingWindowChunker.py

from typing import List
from swarmauri.core.chunkers.IChunker import IChunker

class SlidingWindowChunker(IChunker):
    """
    A concrete implementation of IChunker that uses sliding window technique
    to break the text into chunks.
    """
    
    def __init__(self, window_size: int, step_size: int, overlap: bool = True):
        """
        Initialize the SlidingWindowChunker with specific window and step sizes.
        
        Parameters:
        - window_size (int): The size of the window for each chunk (in terms of number of words).
        - step_size (int): The step size for the sliding window (in terms of number of words).
        - overlap (bool, optional): Whether the windows should overlap. Default is True.
        """
        self.window_size = window_size
        self.step_size = step_size if overlap else window_size  # Non-overlapping if window size equals step size.
           
    def chunk_text(self, text: str, *args, **kwargs) -> List[str]:
        """
        Splits the input text into chunks based on the sliding window technique.
        
        Parameters:
        - text (str): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks.
        """
        words = text.split()  # Tokenization by whitespaces. More sophisticated tokenization might be necessary.
        chunks = []
        
        for i in range(0, len(words) - self.window_size + 1, self.step_size):
            chunk = ' '.join(words[i:i+self.window_size])
            chunks.append(chunk)
        
        return chunks

```

```swarmauri/standard/chunkers/concrete/DelimiterBasedChunker.py

from typing import List, Union, Any
import re
from swarmauri.core.chunkers.IChunker import IChunker

class DelimiterBasedChunker(IChunker):
    """
    A concrete implementation of IChunker that splits text into chunks based on specified delimiters.
    """

    def __init__(self, delimiters: List[str] = None):
        """
        Initializes the chunker with a list of delimiters.

        Parameters:
        - delimiters (List[str], optional): A list of strings that will be used as delimiters for splitting the text.
                                            If not specified, a default list of sentence-ending punctuation is used.
        """
        if delimiters is None:
            delimiters = ['.', '!', '?']  # Default delimiters
        # Create a regex pattern that matches any of the specified delimiters.
        # The pattern uses re.escape on each delimiter to ensure special regex characters are treated literally.
        self.delimiter_pattern = f"({'|'.join(map(re.escape, delimiters))})"
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Chunks the given text based on the delimiters specified during initialization.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.

        Returns:
        - List[str]: A list of text chunks split based on the specified delimiters.
        """
        # Split the text based on the delimiter pattern, including the delimiters in the result
        chunks = re.split(self.delimiter_pattern, text)
        # Combine delimiters with the preceding text chunk since re.split() separates them
        combined_chunks = []
        for i in range(0, len(chunks) - 1, 2):  # Step by 2 to process text chunk with its following delimiter
            combined_chunks.append(chunks[i] + (chunks[i + 1] if i + 1 < len(chunks) else ''))
        return combined_chunks

```

```swarmauri/standard/chunkers/concrete/FixedLengthChunker.py

from typing import List, Union, Any
from swarmauri.core.chunkers.IChunker import IChunker

class FixedLengthChunker(IChunker):
    """
    Concrete implementation of IChunker that divides text into fixed-length chunks.
    
    This chunker breaks the input text into chunks of a specified size, making sure 
    that each chunk has exactly the number of characters specified by the chunk size, 
    except for possibly the last chunk.
    """

    def __init__(self, chunk_size: int):
        """
        Initializes a new instance of the FixedLengthChunker class with a specific chunk size.

        Parameters:
        - chunk_size (int): The fixed size (number of characters) for each chunk.
        """
        self.chunk_size = chunk_size

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

```swarmauri/standard/chunkers/concrete/SimpleSentenceChunker.py

import re
from swarmauri.core.chunkers.IChunker import IChunker

class SimpleSentenceChunker(IChunker):
    """
    A simple implementation of the IChunker interface to chunk text into sentences.
    
    This class uses basic punctuation marks (., !, and ?) as indicators for sentence boundaries.
    """
    
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

from typing import List, Union, Any, Optional
import re
from swarmauri.core.chunkers.IChunker import IChunker

class MdSnippetChunker(IChunker):
    def __init__(self, language: Optional[str] = None):
        """
        Initializes the MdSnippetChunker with a specific programming language
        to look for within Markdown fenced code blocks.
        """
        self.language = language
    
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
from typing import List
import json
import numpy as np
from swarmauri.core.vectors.IVector import IVector

class VectorBase(IVector, ABC):
    def __init__(self, data: List[float]):
        self._data = data

    @property
    def data(self) -> List[float]:
        """
        Returns the vector's data.
        """
        return self._data

    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return np.array(self._data)
    
    def __repr__(self):
        return str(self.data)
    
    def __len__(self):
        return len(self.data)

    def to_dict(self) -> dict:
        """
        Converts the vector into a dictionary suitable for JSON serialization.
        This method needs to be called explicitly for conversion.
        """
        return {'type': self.__class__.__name__,'data': self.data}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

```

```swarmauri/standard/vectors/concrete/SimpleVector.py

from typing import List
from swarmauri.standard.vectors.base.VectorBase import VectorBase

class SimpleVector(VectorBase):
    def __init__(self, data: List[float]):
        super().__init__(data)
        

```

```swarmauri/standard/vectors/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/concrete/VectorProduct.py

import numpy as np
from typing import List

from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.vectors.IVectorProduct import IVectorProduct
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class VectorProduct(IVectorProduct):
    def dot_product(self, vector_a: IVector, vector_b: IVector) -> float:
        a = np.array(vector_a.data).flatten()
        b = np.array(vector_b.data).flatten()
        return np.dot(a, b)
    
    def cross_product(self, vector_a: IVector, vector_b: IVector) -> IVector:
        if len(vector_a.data) != 3 or len(vector_b.data) != 3:
            raise ValueError("Cross product is only defined for 3-dimensional vectors")
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        cross = np.cross(a, b)
        return SimpleVector(cross.tolist())
    
    def vector_triple_product(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> IVector:
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        c = np.array(vector_c.data)
        result = np.cross(a, np.cross(b, c))
        return SimpleVector(result.tolist())
    
    def scalar_triple_product(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> float:
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        c = np.array(vector_c.data)
        return np.dot(a, np.cross(b, c))

```

```swarmauri/standard/vectorizers/__init__.py

#

```

```swarmauri/standard/vectorizers/base/__init__.py

#

```

```swarmauri/standard/vectorizers/concrete/__init__.py

#

```

```swarmauri/standard/vectorizers/concrete/Doc2VecVectorizer.py

from typing import List, Union, Any
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel

class Doc2VecVectorizer(IVectorize, IFeature, ISaveModel):
    def __init__(self):
        self.model = Doc2Vec(vector_size=2000, window=10, min_count=1, workers=5)

    def extract_features(self):
        return list(self.model.wv.key_to_index.keys())

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [TaggedDocument(words=_d.split(), 
            tags=[str(i)]) for i, _d in enumerate(documents)]

        self.model.build_vocab(tagged_data)
        self.model.train(tagged_data, total_examples=self.model.corpus_count, epochs=self.model.epochs)

    def transform(self, documents: List[str]) -> List[IVector]:
        vectors = [self.model.infer_vector(doc.split()) for doc in documents]
        return [SimpleVector(vector) for vector in vectors]

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[IVector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: str) -> IVector:
        vector = self.model.infer_vector(data.split())
        return SimpleVector(vector.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the Doc2Vec model to the specified path.
        """
        self.model.save(path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a Doc2Vec model from the specified path.
        """
        self.model = Doc2Vec.load(path)

```

```swarmauri/standard/vectorizers/concrete/MLMVectorizer.py

from typing import List, Union, Any
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel

class MLMVectorizer(IVectorize, IFeature, ISaveModel):
    """
    IVectorize implementation that fine-tunes a Masked Language Model (MLM).
    """

    def __init__(self, model_name='bert-base-uncased', 
        batch_size = 32, 
        learning_rate = 5e-5, 
        masking_ratio: float = 0.15, 
        randomness_ratio: float = 0.10,
        add_new_tokens: bool = False):
        """
        Initializes the vectorizer with a pre-trained MLM model and tokenizer for fine-tuning.
        
        Parameters:
        - model_name (str): Identifier for the pre-trained model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.epochs = 0
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.masking_ratio = masking_ratio
        self.randomness_ratio = randomness_ratio
        self.add_new_tokens = add_new_tokens
        self.mask_token_id = self.tokenizer.convert_tokens_to_ids([self.tokenizer.mask_token])[0]

    def extract_features(self):
        raise NotImplementedError('Extract_features not implemented on MLMVectorizer.')

    def _mask_tokens(self, encodings):
        input_ids = encodings.input_ids.to(self.device)
        attention_mask = encodings.attention_mask.to(self.device)

        labels = input_ids.detach().clone()

        probability_matrix = torch.full(labels.shape, self.masking_ratio, device=self.device)
        special_tokens_mask = [
            self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool, device=self.device), value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()

        labels[~masked_indices] = -100
        
        indices_replaced = torch.bernoulli(torch.full(labels.shape, self.masking_ratio, device=self.device)).bool() & masked_indices
        input_ids[indices_replaced] = self.mask_token_id

        indices_random = torch.bernoulli(torch.full(labels.shape, self.randomness_ratio, device=self.device)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long, device=self.device)
        input_ids[indices_random] = random_words[indices_random]

        return input_ids, attention_mask, labels

    def fit(self, documents: List[Union[str, Any]]):
        # Check if we need to add new tokens
        if self.add_new_tokens:
            new_tokens = self.find_new_tokens(documents)
            if new_tokens:
                num_added_toks = self.tokenizer.add_tokens(new_tokens)
                if num_added_toks > 0:
                    print(f"Added {num_added_toks} new tokens.")
                    self.model.resize_token_embeddings(len(self.tokenizer))

        encodings = self.tokenizer(documents, return_tensors='pt', padding=True, truncation=True, max_length=512)
        input_ids, attention_mask, labels = self._mask_tokens(encodings)
        optimizer = AdamW(self.model.parameters(), lr=self.learning_rate)
        dataset = TensorDataset(input_ids, attention_mask, labels)
        data_loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model.train()
        for batch in data_loader:
            batch = {k: v.to(self.device) for k, v in zip(['input_ids', 'attention_mask', 'labels'], batch)}
            outputs = self.model(**batch)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        self.epochs += 1
        print(f"Epoch {self.epochs} complete. Loss {loss.item()}")

    def find_new_tokens(self, documents):
        # Identify unique words in documents that are not in the tokenizer's vocabulary
        unique_words = set()
        for doc in documents:
            tokens = set(doc.split())  # Simple whitespace tokenization
            unique_words.update(tokens)
        existing_vocab = set(self.tokenizer.get_vocab().keys())
        new_tokens = list(unique_words - existing_vocab)
        return new_tokens if new_tokens else None

    def transform(self, documents: List[Union[str, Any]]) -> List[IVector]:
        """
        Generates embeddings for a list of documents using the fine-tuned MLM.
        """
        self.model.eval()
        embedding_list = []
        
        for document in documents:
            inputs = self.tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Extract embedding (for simplicity, averaging the last hidden states)
            if hasattr(outputs, 'last_hidden_state'):
                embedding = outputs.last_hidden_state.mean(1)
            else:
                # Fallback or corrected attribute access
                embedding = outputs['logits'].mean(1)
            embedding = embedding.cpu().numpy()
            embedding_list.append(SimpleVector(embedding.squeeze().tolist()))

        return embedding_list

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[IVector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: Union[str, Any], *args, **kwargs) -> IVector:
        """
        Generates an embedding for the input data.

        Parameters:
        - data (Union[str, Any]): The input data, expected to be a textual representation.
                                  Could be a single string or a batch of strings.
        """
        # Tokenize the input data and ensure the tensors are on the correct device.
        self.model.eval()
        inputs = self.tokenizer(data, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embeddings using the model
        with torch.no_grad():
            outputs = self.model(**inputs)

        if hasattr(outputs, 'last_hidden_state'):
            # Access the last layer and calculate the mean across all tokens (simple pooling)
            embedding = outputs.last_hidden_state.mean(dim=1)
        else:
            embedding = outputs['logits'].mean(1)
        # Move the embeddings back to CPU for compatibility with downstream tasks if necessary
        embedding = embedding.cpu().numpy()

        return SimpleVector(embedding.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the model and tokenizer to the specified directory.
        """
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)

    def load_model(self, path: str) -> None:
        """
        Loads the model and tokenizer from the specified directory.
        """
        self.model = AutoModelForMaskedLM.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model.to(self.device)  # Ensure the model is loaded to the correct device

```

```swarmauri/standard/vectorizers/concrete/TFIDFVectorizer.py

from typing import List, Union, Any
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel


class TFIDFVectorizer(IVectorize, IFeature, ISaveModel):
    def __init__(self):
        # Using scikit-learn's TfidfVectorizer as the underlying mechanism
        self.model = SklearnTfidfVectorizer()
        super().__init__()
        
    def extract_features(self):
        return self.model.get_feature_names_out()

    def fit(self, data: Union[str, Any]) -> List[IVector]:
        """
        Vectorizes the input data using the TF-IDF scheme.

        Parameters:
        - data (Union[str, Any]): The input data to be vectorized. Expected to be a single string (document)
                                  or a list of strings (corpus).

        Returns:
        - List[IVector]: A list containing IVector instances, each representing a document's TF-IDF vector.
        """
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        
        self.fit_matrix = self.model.fit_transform(data)

        # Convert the sparse matrix rows into SimpleVector instances
        vectors = [SimpleVector(vector.toarray().flatten()) for vector in self.fit_matrix]

        return vectors

    def fit_transform(self, data: Union[str, Any], documents) -> List[IVector]:
        documents = [doc.content for doc in documents]
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        documents.extend(data)

        transform_matrix = self.model.fit_transform(documents)

        # Convert the sparse matrix rows into SimpleVector instances
        vectors = [SimpleVector(vector.toarray().flatten()) for vector in transform_matrix]
        return vectors
    
    def transform(self, data: Union[str, Any], documents) -> List[IVector]:
        raise NotImplementedError('Transform not implemented on TFIDFVectorizer.')

    def infer_vector(self, data: str, documents) -> IVector:
        documents = [doc.content for doc in documents]
        documents.append(data)
        tmp_tfidf_matrix = self.transform(documents)
        query_vector = tmp_tfidf_matrix[-1]
        return query_vector

    def save_model(self, path: str) -> None:
        """
        Saves the TF-IDF model to the specified path using joblib.
        """
        joblib.dump(self.model, path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a TF-IDF model from the specified path using joblib.
        """
        self.model = joblib.load(path)

```

```swarmauri/standard/vectorizers/concrete/NMFVectorizer.py

import joblib

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel

class NMFVectorizer(IVectorize, IFeature, ISaveModel):
    def __init__(self, n_components=10):
        # Initialize TF-IDF Vectorizer
        self.tfidf_vectorizer = TfidfVectorizer()
        # Initialize NMF with the desired number of components
        self.model = NMF(n_components=n_components)
        self.feature_names = []

    def fit(self, data):
        """
        Fit the NMF model to data.

        Args:
            data (Union[str, Any]): The text data to fit.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(data)
        # Fit the NMF model
        self.model.fit(tfidf_matrix)
        # Store feature names
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()

    def transform(self, data):
        """
        Transform new data into NMF feature space.

        Args:
            data (Union[str, Any]): Text data to transform.

        Returns:
            List[IVector]: A list of vectors representing the transformed data.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.transform(data)
        # Transform TF-IDF matrix into NMF space
        nmf_features = self.model.transform(tfidf_matrix)

        # Wrap NMF features in SimpleVector instances and return
        return [SimpleVector(features.tolist()) for features in nmf_features]

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
        return self.feature_names

    def save_model(self, path: str) -> None:
        """
        Saves the NMF model and TF-IDF vectorizer using joblib.
        """
        # It might be necessary to save both tfidf_vectorizer and model
        # Consider using a directory for 'path' or appended identifiers for each model file
        joblib.dump(self.tfidf_vectorizer, f"{path}_tfidf.joblib")
        joblib.dump(self.model, f"{path}_nmf.joblib")

    def load_model(self, path: str) -> None:
        """
        Loads the NMF model and TF-IDF vectorizer from paths using joblib.
        """
        self.tfidf_vectorizer = joblib.load(f"{path}_tfidf.joblib")
        self.model = joblib.load(f"{path}_nmf.joblib")
        # Dependending on your implementation, you might need to refresh the feature_names
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()

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

from typing import List, Dict, Any
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep

class ChainBase(IChain):
    """
    A base implementation of the IChain interface.
    """

    def __init__(self, 
                 steps: List[IChainStep] = None,
                 **configs):
        self.steps = steps if steps is not None else []
        self.configs = configs

    def add_step(self, step: IChainStep) -> None:
        self.steps.append(step)

    def remove_step(self, step: IChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (IChainStep): The Callable representing the step to remove from the chain.
        """

        raise NotImplementedError('this is not yet implemented')

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError('this is not yet implemented')

    def get_schema_info(self) -> Dict[str, Any]:
        # Return a serialized version of the Chain instance's configuration
        return {
            "steps": [str(step) for step in self.steps],
            "configs": self.configs
        }

```

```swarmauri/standard/chains/base/ChainStepBase.py

from typing import Any, Callable, List, Dict
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep):
    """
    Represents a single step within an execution chain.
    """
    
    def __init__(self, 
        key: str, 
        method: Callable, 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None, 
        ref: str = None):
        """
        Initialize a chain step.

        Args:
            key (str): Unique key or identifier for the step.
            method (Callable): The callable object (function or method) to execute in this step.
            args (List[Any], optional): Positional arguments for the callable.
            kwargs (Dict[str, Any], optional): Keyword arguments for the callable.
            ref (str, optional): Reference to another component or context variable, if applicable.
        """
        self.key = key
        self.method = method
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.ref = ref
        


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

```swarmauri/standard/chains/concrete/StateChain.py

from typing import Any, Dict, List, Callable
from swarmauri.standard.chains.base.ChainStepBase import ChainStepBase
from swarmauri.core.chains.IChain import IChain

class StateChain(IChain):
    """
    Enhanced to support ChainSteps with return parameters, storing return values as instance state variables.
    Implements the IChain interface including get_schema_info and remove_step methods.
    """
    def __init__(self):
        self._steps: List[ChainStepBase] = []
        self._context: Dict[str, Any] = {}
    
    def add_step(self, key: str, method: Callable[..., Any], *args, ref: str = None, **kwargs):
        # Directly store args, kwargs, and optionally a return_key without resolving them
        step = ChainStepBase(key, method, args=args, kwargs=kwargs, ref=ref)  # Note the use of 'ref' as 'return_key'
        self._steps.append(step)
    
    def remove_step(self, step: ChainStepBase) -> None:
        self._steps = [s for s in self._steps if s.key != step.key]
    
    def execute(self, *args, **kwargs) -> Any:
        # Execute the chain and manage result storage based on return_key
        for step in self._steps:
            resolved_args = [self._resolve_placeholders(arg) for arg in step.args]
            resolved_kwargs = {k: self._resolve_placeholders(v) for k, v in step.kwargs.items() if k != 'ref'}
            result = step.method(*resolved_args, **resolved_kwargs)
            if step.ref:  # step.ref is used here as the return_key analogy
                print('step.ref', step.ref)
                resolved_ref = self._resolve_ref(step.ref)
                print(resolved_ref)
                self._context[resolved_ref] = result
        return self._context  # or any specific result you intend to return
    
    def _resolve_ref(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            placeholder = value[2:-1]
            return placeholder
        return value
    
    def _resolve_placeholders(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            placeholder = value[2:-1]
            return self._context.get(placeholder)
        return value

    def set_context(self, **kwargs):
        self._context.update(kwargs)
    
    def get_schema_info(self) -> Dict[str, Any]:
        # Implementing required method from IChain; 
        # Adapt the return structure to your needs
        return {
            "steps": [step.key for step in self._steps],
            "context_keys": list(self._context.keys())
        }

```

```swarmauri/standard/chains/concrete/ChainStep.py

from typing import Any, Callable, List, Dict
from swarmauri.core.chains.IChainStep import IChainStep
from swarmauri.standard.chains.base.ChainStepBase import ChainStepBase

class ChainStep(ChainStepBase):
    """
    Represents a single step within an execution chain.
    """
    
    def __init__(self, 
        key: str, 
        method: Callable, 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None, 
        ref: str = None):
        """
        Initialize a chain step.

        Args:
            key (str): Unique key or identifier for the step.
            method (Callable): The callable object (function or method) to execute in this step.
            args (List[Any], optional): Positional arguments for the callable.
            kwargs (Dict[str, Any], optional): Keyword arguments for the callable.
            ref (str, optional): Reference to another component or context variable, if applicable.
        """
        self.key = key
        self.method = method
        self.args = args 
        self.kwargs = kwargs
        self.ref = ref
        


```

```swarmauri/standard/distances/__init__.py



```

```swarmauri/standard/distances/base/__init__.py



```

```swarmauri/standard/distances/concrete/ChiSquaredDistance.py

from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class ChiSquaredDistance(IDistanceSimilarity):
    """
    Implementation of the IDistanceSimilarity interface using Chi-squared distance metric.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Chi-squared distance between two vectors.
        """
        if len(vector_a.data) != len(vector_b.data):
            raise ValueError("Vectors must have the same dimensionality.")

        chi_squared_distance = 0
        for a, b in zip(vector_a.data, vector_b.data):
            if (a + b) != 0:
                chi_squared_distance += (a - b) ** 2 / (a + b)

        return 0.5 * chi_squared_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors based on the Chi-squared distance.
        """
        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/CosineDistance.py

from numpy.linalg import norm
from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.VectorProduct import VectorProduct

class CosineDistance(IDistanceSimilarity, VectorProduct):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
       
    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """ 
        Computes the cosine distance between two vectors: 1 - cosine similarity.
    
        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.
    
        Returns:
            float: The computed cosine distance between vector_a and vector_b.
                   It ranges from 0 (completely similar) to 2 (completely dissimilar).
        """
        norm_a = norm(vector_a.data)
        norm_b = norm(vector_b.data)
    
        # Check if either of the vector norms is close to zero
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 1.0  # Return maximum distance for cosine which varies between -1 to 1, so 1 indicates complete dissimilarity
    
        # Compute the cosine similarity between the vectors
        cos_sim = self.dot_product(vector_a, vector_b) / (norm_a * norm_b)
    
        # Covert cosine similarity to cosine distance
        cos_distance = 1 - cos_sim
    
        return cos_distance
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the cosine similarity between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The cosine similarity between vector_a and vector_b.
        """
        return 1 - self.distance(vector_a, vector_b)

    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/EuclideanDistance.py

from math import sqrt
from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class EuclideanDistance(IDistanceSimilarity):
    """
    Class to compute the Euclidean distance between two vectors.
    Implements the IDistanceSimiliarity interface.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Euclidean distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Euclidean distance between vector_a and vector_b.
        """
        if len(vector_a.data) != len(vector_b.data):
            raise ValueError("Vectors do not have the same dimensionality.")
        
        distance = sqrt(sum((a - b) ** 2 for a, b in zip(vector_a.data, vector_b.data)))
        return distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the similarity score as the inverse of the Euclidean distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The similarity score between vector_a and vector_b.
        """
        distance = self.distance(vector_a, vector_b)
        return 1 / (1 + distance)
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/JaccardIndexDistance.py

from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class JaccardIndexDistance(IDistanceSimilarity):
    """
    A class implementing Jaccard Index as a similarity and distance metric between two vectors.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Jaccard distance between two vectors.

        The Jaccard distance, which is 1 minus the Jaccard similarity,
        measures dissimilarity between sample sets. It's defined as
        1 - (the intersection of the sets divided by the union of the sets).

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: The Jaccard distance between vector_a and vector_b.
        """
        set_a = set(vector_a.data)
        set_b = set(vector_b.data)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In the special case where the union is zero, return 1.0 which implies complete dissimilarity.
        if union == 0:
            return 1.0

        # Compute Jaccard similarity and then return the distance as 1 - similarity.
        jaccard_similarity = intersection / union
        return 1 - jaccard_similarity

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Jaccard similarity between two vectors.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: Jaccard similarity score between vector_a and vector_b.
        """
        set_a = set(vector_a.data)
        set_b = set(vector_b.data)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In case the union is zero, which means both vectors have no elements, return 1.0 implying identical sets.
        if union == 0:
            return 1.0

        # Compute and return Jaccard similarity.
        return intersection / union
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/LevenshteinDistance.py

from typing import List
import numpy as np
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class LevenshteinDistance(IDistanceSimilarity):
    """
    Implements the IDistance interface to calculate the Levenshtein distance between two vectors.
    The Levenshtein distance between two strings is given by the minimum number of operations needed to transform
    one string into the other, where an operation is an insertion, deletion, or substitution of a single character.
    """
    
    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
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
        string_a = ''.join([chr(int(round(value))) for value in vector_a.data])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.data])
        
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
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        string_a = ''.join([chr(int(round(value))) for value in vector_a.data])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.data])
        return 1 - self.levenshtein(string_a, string_b) / max(len(vector_a), len(vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
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

from typing import Any
from abc import ABC, abstractmethod
from swarmauri.core.metrics.IMetric import IMetric

class MetricBase(IMetric, ABC):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """

    def __init__(self, name: str, unit: str):
        """
        Initializes the metric with a name and unit of measurement.

        Args:
            name (str): The name of the metric.
            unit (str): The unit of measurement for the metric (e.g., 'seconds', 'accuracy').
        """
        self._name = name
        self._unit = unit
        self._value = None  # Initialize with None, or a default value as appropriate

    @property
    def name(self) -> str:
        """
        The metric's name identifier.
        """
        return self._name

    @property
    def value(self) -> Any:
        """
        The current value of the metric.
        """
        return self._value

    @property
    def unit(self) -> str:
        """
        The unit of measurement for the metric.
        """
        return self._unit

    @unit.setter
    def unit(self, value: str) -> None:
        """
        Set the unit of measurement for the metric.
        """
        self._unit = value

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value

```

```swarmauri/standard/metrics/base/CalculateMetricBase.py

from typing import Any
from abc import ABC, abstractmethod
from swarmauri.core.metrics.IMetric import IMetric
from swarmauri.core.metrics.ICalculateMetric import ICalculateMetric

class CalculateMetricBase(IMetric, ICalculateMetric, ABC):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """

    def __init__(self, name: str, unit: str):
        """
        Initializes the metric with a name and unit of measurement.

        Args:
            name (str): The name of the metric.
            unit (str): The unit of measurement for the metric (e.g., 'seconds', 'accuracy').
        """
        self._name = name
        self._unit = unit
        self._value = None  # Initialize with None, or a default value as appropriate

    @property
    def name(self) -> str:
        """
        The metric's name identifier.
        """
        return self._name

    @property
    def value(self):
        """
        The current value of the metric.
        """
        return self._value

    @property
    def unit(self) -> str:
        """
        The unit of measurement for the metric.
        """
        return self._unit

    @unit.setter
    def unit(self, value: str) -> None:
        """
        Set the unit of measurement for the metric.
        """
        self._unit = value

    @abstractmethod
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the metric based on the provided data.
        This method must be implemented by subclasses to define specific calculation logic.
        """
        raise NotImplementedError('calculate is not implemented yet.')

    def update(self, value) -> None:
        """
        Update the metric value based on new information.
        This should be used internally by the `calculate` method or other logic.
        """
        self._value = value

    def __call__(self, **kwargs) -> Any:
        """
        Calculates the metric, updates the value, and returns the current value.
        """
        self.calculate(**kwargs)
        return self.value


```

```swarmauri/standard/metrics/base/AggregateMetricBase.py

from typing import List, Any
from abc import ABC, abstractmethod
from swarmauri.standard.metrics.base.CalculateMetricBase import CalculateMetricBase
from swarmauri.core.metrics.IAggMeasurements import IAggMeasurements

class AggregateMetricBase(CalculateMetricBase, IAggMeasurements, ABC):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    def __init__(self, name: str, unit: str):
        CalculateMetricBase.__init__(name, unit)
        self._measurements = []

    @abstractmethod
    def add_measurement(self, measurement) -> None:
        """
        Adds measurement to the internal store of measurements.
        """
        self._measurements.append(measurement)

    @property
    def measurements(self) -> List[Any]:
        return self._measurements

    @measurements.setter
    def measurements(self, value) -> None:
        self._measurements = value

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        self._measurements.clear()
        self._value = None



```

```swarmauri/standard/metrics/base/ThresholdMetricBase.py

from abc import ABC, abstractmethod
from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase
from swarmauri.core.metrics.IAggMeasurements import IAggMeasurements
from swarmauri.core.metrics.IThreshold import IThreshold

class ThresholdMetricBase(AggregateMetricBase, IAggMeasurements, ABC):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    def __init__(self, name: str, unit: str, k: int):
        AggregateMetricBase.__init__(name, unit)
        self._k = k

    @property
    @abstractmethod
    def k(self) -> int:
        return self._k

    @k.setter
    @abstractmethod
    def k(self, value: int) -> None:
        self._k = value


```

```swarmauri/standard/metrics/concrete/__init__.py



```

```swarmauri/standard/metrics/concrete/TaskSuccessRateMetric.py

from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class TaskSuccessRateMetric(AggregateMetricBase):
    """
    Metric calculating the task success rate over all attempted tasks.
    """
    
    def __init__(self):
        super().__init__(name="TaskSuccessRate", unit="percentage")
        self.total_tasks = 0
        self.successful_tasks = 0

    def add_measurement(self, measurement) -> None:
        """
        Adds a task outcome to the metrics. Measurement should be a boolean indicating task success.
        """
        self.total_tasks += 1
        if measurement:
            self.successful_tasks += 1

    def calculate(self, **kwargs) -> float:
        """
        Calculate the success rate of tasks based on the total and successful tasks.

        Returns:
            float: The success rate as a percentage.
        """
        if self.total_tasks == 0:
            return 0.0
        success_rate = (self.successful_tasks / self.total_tasks) * 100
        self.update(success_rate)
        return self.value
    
    @property
    def measurements(self):
        return {"total_tasks": self.total_tasks, "successful_tasks": self.successful_tasks} 

```

```swarmauri/standard/metrics/concrete/TimeOnTaskMetric.py

import statistics
from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class TimeOnTaskMetric(AggregateMetricBase):
    """
    Metric to calculate the average time users spend on a given task.
    """
    def __init__(self, name="Time on Task", unit="seconds"):
        super().__init__(name, unit)

    def calculate(self, **kwargs):
        """
        Calculate the average time on task based on the collected measurements.
        """
        if not self.measurements:
            return 0
        return statistics.mean(self.measurements)

    def add_measurement(self, seconds: float) -> None:
        """
        Adds a measurement of time (in seconds) that a user spent on a task.
        """
        if seconds < 0:
            raise ValueError("Time on task cannot be negative.")
        super().add_measurement(seconds)

```

```swarmauri/standard/metrics/concrete/StaticValueMetric.py

from swarmauri.standard.metrics.base.MetricBase import MetricBase

# Implementing a StaticValueMetric class
class StaticValueMetric(MetricBase):
    """
    A static metric that always returns a fixed, predefined value.
    
    Attributes:
        name (str): The name of the metric.
        unit (str): The unit of measurement for the metric.
        _value (Any): The static value of the metric.
    """
    def __init__(self, name: str, unit: str, value):
        """
        Initialize the static metric with its name, unit, and static value.

        Args:
            name (str): The name identifier for the metric.
            unit (str): The unit of measurement for the metric.
            value: The static value for this metric.
        """
        # Initialize attributes from the base class
        super().__init__(name, unit)
        # Assign the static value
        self._value = value

    # Overriding the 'value' property to always return the static value
    @property
    def value(self):
        """
        Overridden to return the predefined static value for this metric.
        """
        return self._value

```

```swarmauri/standard/metrics/concrete/MeanMetric.py

from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class MeanMetric(AggregateMetricBase):
    """
    A metric that calculates the mean (average) of a list of numerical values.

    Attributes:
        name (str): The name of the metric.
        unit (str): The unit of measurement for the mean (e.g., "degrees", "points").
        _value (float): The calculated mean of the measurements.
        _measurements (list): A list of measurements (numerical values) to average.
    """
    def __init__(self, name: str, unit: str):
        """
        Initialize the MeanMetric with its name and unit.

        Args:
            name (str): The name identifier for the metric.
            unit (str): The unit of measurement for the mean.
        """
        # Calling the constructor of the base class
        super().__init__(name, unit)
    
    def add_measurement(self, measurement) -> None:
        """
        Adds a measurement to the internal list of measurements.

        Args:
            measurement (float): A numerical value to be added to the list of measurements.
        """
        # Append the measurement to the internal list
        self._measurements.append(measurement)

    def calculate(self) -> float:
        """
        Calculate the mean of all added measurements.
        
        Returns:
            float: The mean of the measurements or None if no measurements have been added.
        """
        if not self._measurements:
            return None  # Return None if there are no measurements
        # Calculate the mean
        mean = sum(self._measurements) / len(self._measurements)
        # Update the metric's value
        self.update(mean)
        # Return the calculated mean
        return mean

```

```swarmauri/standard/metrics/concrete/ThresholdMeanMetric.py

from swarmauri.standard.metrics.base.ThresholdMetricBase import ThresholdMetricBase

class ThresholdMeanMetric(ThresholdMetricBase):
    """
    Calculates the mean of measurements that fall within a specified threshold from the current mean.
    """

    def is_within_threshold(self, measurement: float) -> bool:
        if self._value is None:  # If there's no current value, accept the measurement
            return True
        return abs(measurement - self._value) <= self.threshold
    
    def calculate(self) -> float:
        # Filtering the measurements based on the threshold
        filtered_measurements = [m for m in self._measurements if self.is_within_threshold(m)]

        # Calculate the mean of filtered measurements
        if not filtered_measurements:
            return None  # Return None if there are no measurements within the threshold

        mean_value = sum(filtered_measurements) / len(filtered_measurements)
        self.update(mean_value)
        return mean_value

```

```swarmauri/standard/metrics/concrete/ZeroMetric.py

from swarmauri.standard.metrics.base.MetricBase import MetricBase

class ZeroMetric(MetricBase):
    """
    A concrete implementation of MetricBase that statically represents the value 0.
    This can be used as a placeholder or default metric where dynamic calculation is not required.
    """

    def __init__(self):
        super().__init__(name="ZeroMetric", unit="unitless")

    @property
    def value(self):
        """
        Overrides the value property to always return 0.
        """
        return 0



```

```swarmauri/standard/metrics/concrete/SystemUsabilityScaleMetric.py

from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class SystemUsabilityScaleMetric(AggregateMetricBase):
    """
    Metric calculating the System Usability Scale (SUS) score based on a set of questionnaire responses.
    """
    
    def __init__(self):
        super().__init__(name="SystemUsabilityScale", unit="SUS score")

    def add_measurement(self, measurement) -> None:
        """
        Adds individual SUS questionnaire item scores (ranging from 0-4) to the measurements.
        """
        if isinstance(measurement, list) and all(isinstance(item, int) and 0 <= item <= 4 for item in measurement):
            self._measurements.extend(measurement)
        else:
            raise ValueError("Each measurement must be a list of integers between 0 and 4.")

    def calculate(self, **kwargs) -> float:
        """
        Calculate the SUS score from the current measurements.
        
        Returns:
            float: The calculated SUS score.
        """
        if len(self._measurements) != 10:
            raise ValueError("Exactly 10 measurements are required to calculate the SUS score.")
        
        # Adjust scores for negative items: subtract each score from 4
        adjusted_scores = [self._measurements[i] if i % 2 == 0 else 4 - self._measurements[i] for i in range(10)]
        
        # Calculate the SUS score: multiply the sum of scores by 2.5
        sus_score = sum(adjusted_scores) * 2.5
        self.update(sus_score)
        return self.value

```

```swarmauri/standard/metrics/concrete/FirstImpressionMetric.py

from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class FirstImpressionMetric(AggregateMetricBase):
    """
    Metric for capturing the first impression score from a set of scores.
    """

    def __init__(self, name="FirstImpressionScore", unit="points"):
        super().__init__(name=name, unit=unit)
        self._first_impression = None

    def add_measurement(self, measurement) -> None:
        """
        Adds a new score as a measurement. Only the first score is considered as the first impression.
        """
        if self._first_impression is None:
            if isinstance(measurement, (int, float)):
                self._first_impression = measurement
                self._measurements.append(measurement)
            else:
                raise ValueError("Measurement must be a numerical value.")
    
    def calculate(self) -> float:
        """
        Returns the first impression score.

        Returns:
            float: The first impression score.
        """
        if self._first_impression is None:
            raise ValueError("No measurement added. Unable to calculate first impression score.")
        
        self.update(self._first_impression)
        return self.value

```

```swarmauri/standard/metrics/concrete/HitRateAtK.py

from typing import List, Tuple, Any
from swarmauri.standard.metrics.base.ThresholdMetricBase import ThresholdMetricBase

class HitRateAtK(ThresholdMetricBase):
    """
    Hit Rate at K (HR@K) metric calculates the proportion of times an item of interest 
    appears in the top-K recommendations.
    """

    def __init__(self, name="HitRate@K", unit="ratio", k: int = 5):
        """
        Initializes the Hit Rate at K metric with a specified k value, name, and unit 
        of measurement.
        
        Args:
            k (int): The k value for the top-K recommendations.
            name (str): The name of the metric.
            unit (str): The unit of measurement for the metric.
        """
        super().__init__(name=name, unit=unit, k=k)

    def add_measurement(self, measurement: Tuple[List[Any], Any]) -> None:
        """
        Adds a measurement for HR@K calculation. The measurement should be a tuple
        (recommendations, target), where recommendations is a list of recommended items, 
        and target is the item of interest.

        Args:
            measurement (Tuple[List[Any], Any]): List of recommended items and the target item.
        """
        if len(measurement) != 2 or not isinstance(measurement[0], list):
            raise ValueError("Measurement must be a tuple (recommendations, target).")
        self._measurements.append(measurement)

    def calculate(self) -> Any:
        """
        Calculate the HR@K based on the provided measurements.

        Returns:
            Any: The HR@K score as a floating point number.
        """
        if not self._measurements:
            raise ValueError("No measurements added to calculate HR@K.")

        hits = 0
        for recommendations, target in self._measurements:
            hits += 1 if target in recommendations[:self.k] else 0

        hit_rate_at_k = hits / len(self._measurements)

        self.update(hit_rate_at_k)
        return self.value

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        super().reset()

```

```swarmauri/standard/metrics/concrete/ImpressionAtK.py

from swarmauri.standard.metrics.base.ThresholdMetricBase import ThresholdMetricBase

class ImpressionAtKMetric(ThresholdMetricBase):
    def __init__(self, k: int):
        super().__init__(name="Impression at K", unit="count", k=k)
    
    def calculate(self, impressions, **kwargs):
        if not isinstance(impressions, list):
            raise ValueError("Impressions should be provided as a list")
        
        k_impressions = impressions[:self._k] if len(impressions) >= self._k else impressions

        self._value = len([imp for imp in k_impressions if imp > 0])
        return self._value

    def reset(self):
        self._value = 0
    
    def update(self, value):
        raise NotImplementedError("This Metric does not support update operation directly.")
    
    def __call__(self, **kwargs):
        """
        Retrieves the current value of the metric.
        
        Returns:
            The current value of the metric if calculated; otherwise, triggers a calculation.
        """
        if 'impressions' in kwargs:
            return self.calculate(kwargs['impressions'])
        return self._value

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



``````swarmauri/community/__init__.py



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
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

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

import os
import base64
import json
from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

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

from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

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
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

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
from ...standard.tools.base.ToolBase import ToolBase
from ...standard.tools.concrete.Parameter import Parameter

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

from ....core.tools.ITool import ITool
from ....standard.tools.concrete.Parameter import Parameter  # Update import path as necessary
import numpy as np
import pacmap  # Ensure pacmap is installed

class PaCMAPTool(ITool):
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