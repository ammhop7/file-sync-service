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
from exceptions import (
    CloudAuthenticationError,
    CloudConnectionError,
    CloudTimeoutError,
    CloudUploadError,
    CloudDeleteError
)


class CloudClient(BaseCloudClient):
    """
    Cloud storage client for file synchronization.

    This implementation uses a REST API to interact with cloud storage.
    All cloud-specific logic is isolated here for easy extensibility.
    """

    # Timeout constants
    CONNECTION_TIMEOUT = 10  # seconds
    UPLOAD_TIMEOUT = 30  # seconds

    def __init__(self, token: str, remote_folder: str):
        """
        Initialize cloud client with authentication.

        Args:
            token: API authentication token
            remote_folder: Name of the remote folder to sync with

        Raises:
            CloudAuthenticationError: If authentication fails
            CloudConnectionError: If connection to cloud service fails
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
            CloudAuthenticationError: If token is invalid
            CloudConnectionError: If connection fails
            CloudTimeoutError: If request times out
        """
        try:
            response = requests.get(
                f"{self.base_url}/auth/validate",
                headers=self.headers,
                timeout=self.CONNECTION_TIMEOUT
            )

            if response.status_code == 401:
                raise CloudAuthenticationError(
                    "Invalid API token - authentication failed"
                )

            if response.status_code != 200:
                raise CloudConnectionError(
                    f"Cloud service connection failed with status {response.status_code}"
                )

            logger.info("Cloud connection validated successfully")

        except requests.exceptions.Timeout as e:
            raise CloudTimeoutError(
                f"Connection validation timed out after {self.CONNECTION_TIMEOUT}s: {e}"
            )
        except requests.exceptions.ConnectionError as e:
            raise CloudConnectionError(
                f"Failed to connect to cloud service: {e}"
            )
        except requests.exceptions.RequestException as e:
            raise CloudConnectionError(
                f"Request failed during connection validation: {e}"
            )

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
                    timeout=self.UPLOAD_TIMEOUT
                )

            if response.status_code in (200, 201):
                logger.info(f"Uploaded: {filename}")
                return True

            logger.error(f"Upload failed for {filename}: HTTP {response.status_code}")
            return False

        except requests.exceptions.Timeout:
            logger.error(f"Upload timeout for {file_path} after {self.UPLOAD_TIMEOUT}s")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error uploading {file_path}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error uploading {file_path}: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading {file_path}: {e}")
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
                    timeout=self.UPLOAD_TIMEOUT
                )

            if response.status_code == 200:
                logger.info(f"Re-uploaded: {filename}")
                return True

            logger.error(f"Re-upload failed for {filename}: HTTP {response.status_code}")
            return False

        except requests.exceptions.Timeout:
            logger.error(f"Re-upload timeout for {file_path} after {self.UPLOAD_TIMEOUT}s")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error re-uploading {file_path}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error re-uploading {file_path}: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error re-uploading {file_path}: {e}")
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
                timeout=self.CONNECTION_TIMEOUT
            )

            if response.status_code in (200, 204):
                logger.info(f"Deleted: {filename}")
                return True

            logger.error(f"Deletion failed for {filename}: HTTP {response.status_code}")
            return False

        except requests.exceptions.Timeout:
            logger.error(f"Delete timeout for {filename} after {self.CONNECTION_TIMEOUT}s")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error deleting {filename}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error deleting {filename}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting {filename}: {e}")
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
                timeout=self.CONNECTION_TIMEOUT
            )

            if response.status_code != 200:
                logger.error(f"Failed to get remote file info: HTTP {response.status_code}")
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

        except requests.exceptions.Timeout:
            logger.error(f"Timeout getting remote file info after {self.CONNECTION_TIMEOUT}s")
            return {}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error getting remote file info: {e}")
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error getting remote file info: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting remote file info: {e}")
            return {}
