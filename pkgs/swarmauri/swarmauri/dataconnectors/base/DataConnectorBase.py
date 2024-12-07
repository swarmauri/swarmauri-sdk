from swarmauri_core.dataconnectors.IDataConnector import IDataConnector


class DataConnectorBase(IDataConnector):
    """
    Base implementation of IDataConnector that raises NotImplementedError
    for all abstract methods, ensuring explicit implementation in child classes.
    """

    def authenticate(self, **kwargs):
        """
        Raises NotImplementedError to enforce implementation in child classes.

        :param kwargs: Authentication parameters
        :raises NotImplementedError: Always raised to require specific implementation
        """
        raise NotImplementedError(
            "Authenticate method must be implemented by child classes."
        )

    def fetch_data(self, query: str, **kwargs):
        """
        Raises NotImplementedError to enforce implementation in child classes.

        :param query: Query string or parameters
        :param kwargs: Additional parameters
        :raises NotImplementedError: Always raised to require specific implementation
        """
        raise NotImplementedError(
            "Fetch data method must be implemented by child classes."
        )

    def insert_data(self, data, **kwargs):
        """
        Raises NotImplementedError to enforce implementation in child classes.

        :param data: Data to be inserted
        :param kwargs: Additional parameters
        :raises NotImplementedError: Always raised to require specific implementation
        """
        raise NotImplementedError(
            "Insert data method must be implemented by child classes."
        )

    def update_data(self, identifier, data, **kwargs):
        """
        Raises NotImplementedError to enforce implementation in child classes.

        :param identifier: Unique identifier of the data to update
        :param data: Updated data
        :param kwargs: Additional parameters
        :raises NotImplementedError: Always raised to require specific implementation
        """
        raise NotImplementedError(
            "Update data method must be implemented by child classes."
        )

    def delete_data(self, identifier, **kwargs):
        """
        Raises NotImplementedError to enforce implementation in child classes.

        :param identifier: Unique identifier of the data to delete
        :param kwargs: Additional parameters
        :raises NotImplementedError: Always raised to require specific implementation
        """
        raise NotImplementedError(
            "Delete data method must be implemented by child classes."
        )

    def test_connection(self, **kwargs):
        """
        Raises NotImplementedError to enforce implementation in child classes.

        :param kwargs: Connection parameters
        :raises NotImplementedError: Always raised to require specific implementation
        """
        raise NotImplementedError(
            "Test connection method must be implemented by child classes."
        )
