from abc import ABC, abstractmethod


class IDataConnector(ABC):
    """
    Abstract base class for data connectors.
    Defines the interface for all concrete data connector implementations.
    """

    @abstractmethod
    def authenticate(self, **kwargs):
        """
        Authenticate with the data source.
        This method should handle any required authentication process.

        :param kwargs: Authentication parameters such as API keys, tokens, etc.
        """
        pass

    @abstractmethod
    def fetch_data(self, query: str, **kwargs):
        """
        Fetch data from the data source based on a query.

        :param query: Query string or parameters to fetch specific data.
        :param kwargs: Additional parameters for fetching data.
        :return: Data fetched from the source.
        """
        pass

    @abstractmethod
    def insert_data(self, data, **kwargs):
        """
        Insert data into the data source.

        :param data: Data to be inserted.
        :param kwargs: Additional parameters for inserting data.
        """
        pass

    @abstractmethod
    def update_data(self, identifier, data, **kwargs):
        """
        Update existing data in the data source.

        :param identifier: Unique identifier of the data to update.
        :param data: Updated data.
        :param kwargs: Additional parameters for updating data.
        """
        pass

    @abstractmethod
    def delete_data(self, identifier, **kwargs):
        """
        Delete data from the data source.

        :param identifier: Unique identifier of the data to delete.
        :param kwargs: Additional parameters for deleting data.
        """
        pass

    @abstractmethod
    def test_connection(self, **kwargs):
        """
        Test the connection to the data source.

        :param kwargs: Connection parameters.
        :return: Boolean indicating whether the connection is successful.
        """
        pass
