from abc import ABC, abstractmethod


class ITransactional(ABC):
    @abstractmethod
    def begin_transaction(self):
        """
        Initiates a transaction for a series of vector store operations.
        """

    @abstractmethod
    def commit_transaction(self):
        """
        Commits the current transaction, making all operations within the
        transaction permanent.
        """

    @abstractmethod
    def abort_transaction(self):
        """
        Aborts the current transaction, reverting all operations performed
        within the transaction.
        """
