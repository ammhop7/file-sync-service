"""
Mock cloud client for local testing and development.
Simulates cloud storage operations without requiring actual API.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any

from loguru import logger

from cloud.base import BaseCloudClient
from exceptions import CloudUploadError, CloudDeleteError


class MockCloudClient(BaseCloudClient):
    """
    Mock cloud storage client for testing.

    Stores files in a local directory to simulate cloud storage.
    Useful for development and testing without real API credentials.
    """

    def __init__(self, token: str, remote_folder: str):
        """
        Initialize mock cloud client.

        Args:
            token: API token (not validated in mock)
            remote_folder: Name of the remote folder
        """
        self.token = token
        self.remote_folder = remote_folder

        # Create mock cloud storage directory
        self.mock_storage_path = Path("mock_cloud_storage") / remote_folder
        self.mock_storage_path.mkdir(parents=True, exist_ok=True)

        # Metadata file to track file info
        self.metadata_file = self.mock_storage_path / ".metadata.json"
        self._load_metadata()

        logger.info(f"Mock cloud client initialized at: {self.mock_storage_path}")

    def _load_metadata(self) -> None:
        """Load metadata from file or create empty metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
            self._save_metadata()

    def _save_metadata(self) -> None:
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def load(self, file_path: str) -> bool:
        """
        Upload a new file to mock cloud storage.

        Args:
            file_path: Path to the local file to upload

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            path = Path(file_path)
            filename = path.name

            # Copy file to mock storage
            destination = self.mock_storage_path / filename
            shutil.copy2(file_path, destination)

            # Update metadata
            self.metadata[filename] = {
                'modified_time': path.stat().st_mtime
            }
            self._save_metadata()

            logger.info(f"Uploaded: {filename}")
            return True

        except Exception as e:
            logger.error(f"Error uploading {file_path}: {e}")
            return False

    def reload(self, file_path: str) -> bool:
        """
        Re-upload (overwrite) an existing file in mock cloud storage.

        Args:
            file_path: Path to the local file to re-upload

        Returns:
            bool: True if re-upload successful, False otherwise
        """
        try:
            path = Path(file_path)
            filename = path.name

            # Copy file to mock storage (overwrite)
            destination = self.mock_storage_path / filename
            shutil.copy2(file_path, destination)

            # Update metadata
            self.metadata[filename] = {
                'modified_time': path.stat().st_mtime
            }
            self._save_metadata()

            logger.info(f"Re-uploaded: {filename}")
            return True

        except Exception as e:
            logger.error(f"Error re-uploading {file_path}: {e}")
            return False

    def delete(self, filename: str) -> bool:
        """
        Delete a file from mock cloud storage.

        Args:
            filename: Name of the file to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            file_path = self.mock_storage_path / filename

            if file_path.exists():
                file_path.unlink()

            # Remove from metadata
            if filename in self.metadata:
                del self.metadata[filename]
                self._save_metadata()

            logger.info(f"Deleted: {filename}")
            return True

        except Exception as e:
            logger.error(f"Error deleting {filename}: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about all files in mock cloud storage.

        Returns:
            Dict mapping filename to metadata dict with 'modified_time' key
        """
        try:
            return self.metadata.copy()
        except Exception as e:
            logger.error(f"Error getting remote file info: {e}")
            return {}
