"""
Factory for creating cloud client instances.
Implements Dependency Inversion Principle by depending on abstractions.
"""

from typing import Dict, Type

from loguru import logger

from cloud.base import BaseCloudClient
from cloud.cloud_client import CloudClient
from cloud.mock_client import MockCloudClient
from exceptions import ConfigurationError


class CloudClientFactory:
    """
    Factory for creating cloud client instances.

    Allows switching between different cloud implementations
    without changing the main application code.
    """

    _clients: Dict[str, Type[BaseCloudClient]] = {
        'mock': MockCloudClient,
        'production': CloudClient,
    }

    @classmethod
    def create(cls, client_type: str, token: str, remote_folder: str) -> BaseCloudClient:
        """
        Create a cloud client instance based on type.

        Args:
            client_type: Type of client ('mock' or 'production')
            token: API authentication token
            remote_folder: Name of the remote folder

        Returns:
            BaseCloudClient: Instance of the requested cloud client

        Raises:
            ConfigurationError: If client_type is not supported
        """
        client_class = cls._clients.get(client_type.lower())

        if not client_class:
            available = ', '.join(cls._clients.keys())
            raise ConfigurationError(
                f"Unknown cloud client type: '{client_type}'. "
                f"Available types: {available}"
            )

        logger.info(f"Creating cloud client: {client_type}")
        return client_class(token=token, remote_folder=remote_folder)

    @classmethod
    def register_client(cls, name: str, client_class: Type[BaseCloudClient]) -> None:
        """
        Register a new cloud client type.

        Args:
            name: Name for the client type
            client_class: Cloud client class (must inherit from BaseCloudClient)
        """
        if not issubclass(client_class, BaseCloudClient):
            raise ValueError(f"{client_class} must inherit from BaseCloudClient")

        cls._clients[name.lower()] = client_class
        logger.info(f"Registered cloud client: {name}")
