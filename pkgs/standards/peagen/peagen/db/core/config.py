"""
Setting Configuration in the application.

This will define the Setting used for the application.

Classes:

    Settings

Instances:

    settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    A class to represent Settings.

    ...

    Attributes (More will be added as Needed!!)
    ----------
    database_url (str): The URL for the database.
    """

    database_url: str = "sqlite:///./dev.db"

    class Config:
        """
        A class to represent the Configuation of Settings.

        ...

        Attributes (More will be added as Needed!!)
        ----------
        env_file: The path to the environment variable.
        env_file_encoding: Default encoding to work on all OS
        """

        env_file = ".env"
        env_file_enoding = "utf-8"


settings = Settings()
