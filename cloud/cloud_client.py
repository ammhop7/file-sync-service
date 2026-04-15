"""
Cloud storage client implementation using HTTP API.
Handles all interactions with the remote cloud storage service.
"""

import os
from pathlib import Path
from typing import Dict, Any

import requests
from loguru import logger

from cloud.base import BaseCloudClient


class CloudClient(BaseCloudClient):
    """
    Cloud storage client for file synchronization.

    This implementation uses a REST API to interact with cloud storage.
    All cloud-specific logic is isolated here for easy extensibility.
    """

    def __init__(self, token: str, remote_folder: str):
        """
        Initialize cloud client with authentication.

        Args:
            token: API authentication token
            remote_folder: Name of the remote folder to sync with
        """
        self.token = token
        self.remote_folder = remote_folder
        self.base_url = "https://api.cloudprovider.com/v1"  # Example API endpoint
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Validate connection on initialization
        self._validate_connection()

    def _validate_connection(self) -> None:
        """
        Validate API token and connection to cloud service.

        Raises:
            SystemExit: If token is invalid or connection fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/auth/validate",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 401:
                logger.error("Invalid API token - authentication failed")
                raise SystemExit(1)

            if response.status_code != 200:
                logger.error(f"Cloud service connection failed: {response.status_code}")
                raise SystemExit(1)

            logger.info("Cloud connection validated successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to cloud service: {e}")
            raise SystemExit(1)

    def load(self, file_path: str) -> bool:
        """
        Upload a new file to cloud storage.

        Args:
            file_path: Path to the local file to upload

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            path = Path(file_path)
            filename = path.name

            with open(file_path, 'rb') as file:
                files = {'file': (filename, file)}
                data = {'folder': self.remote_folder}

                response = requests.post(
                    f"{self.base_url}/files/upload",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code in (200, 201):
                logger.info(f"Uploaded: {filename}")
                return True

            logger.error(f"Upload failed for {filename}: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Error uploading {file_path}: {e}")
            return False

    def reload(self, file_path: str) -> bool:
        """
        Re-upload (overwrite) an existing file in cloud storage.

        Args:
            file_path: Path to the local file to re-upload

        Returns:
            bool: True if re-upload successful, False otherwise
        """
        try:
            path = Path(file_path)
            filename = path.name

            with open(file_path, 'rb') as file:
                files = {'file': (filename, file)}
                data = {
                    'folder': self.remote_folder,
                    'overwrite': 'true'
                }

                response = requests.put(
                    f"{self.base_url}/files/{filename}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code == 200:
                logger.info(f"Re-uploaded: {filename}")
                return True

            logger.error(f"Re-upload failed for {filename}: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Error re-uploading {file_path}: {e}")
            return False

    def delete(self, filename: str) -> bool:
        """
        Delete a file from cloud storage.

        Args:
            filename: Name of the file to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/files/{filename}",
                headers=self.headers,
                params={'folder': self.remote_folder},
                timeout=10
            )

            if response.status_code in (200, 204):
                logger.info(f"Deleted: {filename}")
                return True

            logger.error(f"Deletion failed for {filename}: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Error deleting {filename}: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about all files in the remote folder.

        Returns:
            Dict mapping filename to metadata dict with 'modified_time' key
        """
        try:
            response = requests.get(
                f"{self.base_url}/files",
                headers=self.headers,
                params={'folder': self.remote_folder},
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Failed to get remote file info: {response.status_code}")
                return {}

            files_data = response.json().get('files', [])

            # Convert API response to standardized format
            file_info = {}
            for file_data in files_data:
                filename = file_data.get('name')
                modified_time = file_data.get('modified_timestamp', 0)

                if filename:
                    file_info[filename] = {
                        'modified_time': modified_time
                    }

            return file_info

        except Exception as e:
            logger.error(f"Error getting remote file info: {e}")
            return {}
