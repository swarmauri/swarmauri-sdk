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
