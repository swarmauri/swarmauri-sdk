![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_core" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/core">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/core&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_core" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/l/swarmauri_core" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/v/swarmauri_core?label=swarmauri_core&color=green" alt="PyPI - swarmauri_core"/></a>
</p>


# Swarmauri Core Library

The Core Library provides the foundational interfaces and abstract base classes necessary for developing scalable and flexible machine learning agents, models, and tools. It is designed to offer a standardized approach to implementing various components of machine learning systems, such as models, parsers, conversations, and vector stores.

## Features

- **LLMs Interface**: Define and interact with predictive models.

```python
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

    @abstractmethod
    async def apredict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
    ...
```

- **Agents Interface**: Build and manage intelligent agents for varied tasks.

```python
class IAgent(ABC):
    @abstractmethod
    def exec(self, input_data: Optional[Any], llm_kwargs: Optional[Dict]) -> Any:
        """
        Executive method that triggers the agent's action based on the input data.
        """
        pass
```

- **Tools Interface**: Develop tools with standardized execution and configuration.

```python
class ITool(ABC):
    @abstractmethod
    def call(self, *args, **kwargs):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        pass

```

- **Parsers and Conversations**: Handle and parse text data, manage conversations states.

```python
class IParser(ABC):
    """
    Abstract base class for parsers. It defines a public method to parse input data (str or Message) into documents,
    and relies on subclasses to implement the specific parsing logic through protected and private methods.
    """

    @abstractmethod
    def parse(self, data: Union[str, bytes, FilePath]) -> List[IDocument]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.

        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass
```

- **Vector Stores**: Interface for vector storage and similarity searches.

```python
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

    ...
```

- **Document Stores**: Manage the storage and retrieval of documents.

```python
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
```

## Getting Started

To start developing with the Core Library, include it as a module in your Python project. Ensure you have Python 3.10 or later installed.

### Steps to install via pypi

```sh
pip install swarmauri_core
```

### Usage Example

```python
# Example of using an abstract model interface from the Core Library
from swarmauri_core.llms.IPredict import IPredict

class MyModel(IPredict):
    # Implement the abstract methods here
    pass
```


## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, kindly go through the [contributions guidelines](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) first.

