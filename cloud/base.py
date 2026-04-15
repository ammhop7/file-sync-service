"""
Base interface for cloud storage clients.
Defines the contract that all cloud storage implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseCloudClient(ABC):
    """Abstract base class for cloud storage clients."""

    @abstractmethod
    def load(self, file_path: str) -> bool:
        """
        Upload a new file to cloud storage.

        Args:
            file_path: Path to the local file to upload

        Returns:
            bool: True if upload successful, False otherwise
        """
        pass

    @abstractmethod
    def reload(self, file_path: str) -> bool:
        """
        Re-upload (overwrite) an existing file in cloud storage.

        Args:
            file_path: Path to the local file to re-upload

        Returns:
            bool: True if re-upload successful, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, filename: str) -> bool:
        """
        Delete a file from cloud storage.

        Args:
            filename: Name of the file to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about remote files.

        Returns:
            Dict mapping filename to file metadata (e.g., modification time)
        """
        pass
