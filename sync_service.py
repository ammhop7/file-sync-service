"""
Synchronization service for managing file sync operations.
Coordinates file watching and cloud operations.
"""

import time
from pathlib import Path

from loguru import logger

from cloud.cloud_client import CloudClient
from file_watcher import FileWatcher


class SyncService:
    """
    Manages synchronization between local folder and cloud storage.

    Coordinates file watching, change detection, and cloud operations.
    """

    def __init__(self, local_folder: Path, cloud_client: CloudClient):
        """
        Initialize sync service.

        Args:
            local_folder: Path to local folder to sync
            cloud_client: Cloud client for remote operations
        """
        self.local_folder = local_folder
        self.cloud_client = cloud_client
        self.file_watcher = FileWatcher(local_folder)

    def perform_initial_sync(self) -> None:
        """
        Perform initial full synchronization on startup.

        Compares local files with remote files and syncs differences.
        """
        logger.info("Starting initial synchronization...")

        local_files = self.file_watcher.get_current_files()
        remote_files = self.cloud_client.get_info()

        self._sync_initial_state(local_files, remote_files)

        self.file_watcher.initialize_snapshot()
        logger.info("Initial synchronization completed")

    def _sync_initial_state(
        self,
        local_files: dict,
        remote_files: dict
    ) -> None:
        """
        Sync initial state between local and remote.

        Args:
            local_files: Dict of local filename -> modification time
            remote_files: Dict of remote filename -> metadata
        """
        local_names = set(local_files.keys())
        remote_names = set(remote_files.keys())

        files_to_upload = self._find_files_to_upload(
            local_names,
            remote_names,
            local_files,
            remote_files
        )
        files_to_delete = self._find_files_to_delete(local_names, remote_names)

        self._upload_files(files_to_upload)
        self._delete_files(files_to_delete)

    def _find_files_to_upload(
        self,
        local_names: set,
        remote_names: set,
        local_files: dict,
        remote_files: dict
    ) -> set:
        """
        Find files that need to be uploaded.

        Files need upload if:
        - They exist locally but not remotely
        - They exist in both but local is newer

        Args:
            local_names: Set of local filenames
            remote_names: Set of remote filenames
            local_files: Local file metadata
            remote_files: Remote file metadata

        Returns:
            Set of filenames to upload
        """
        files_to_upload = set()

        # Files only in local
        files_to_upload.update(local_names - remote_names)

        # Files in both - check modification time
        common_files = local_names & remote_names
        for filename in common_files:
            local_mtime = local_files[filename]
            remote_mtime = remote_files[filename].get('modified_time', 0)

            if local_mtime > remote_mtime:
                files_to_upload.add(filename)

        return files_to_upload

    def _find_files_to_delete(self, local_names: set, remote_names: set) -> set:
        """
        Find files that need to be deleted from remote.

        Files need deletion if they exist remotely but not locally.

        Args:
            local_names: Set of local filenames
            remote_names: Set of remote filenames

        Returns:
            Set of filenames to delete
        """
        return remote_names - local_names

    def _upload_files(self, filenames: set) -> None:
        """
        Upload multiple files to cloud.

        Args:
            filenames: Set of filenames to upload
        """
        for filename in filenames:
            file_path = self.local_folder / filename
            self.cloud_client.load(str(file_path))

    def _delete_files(self, filenames: set) -> None:
        """
        Delete multiple files from cloud.

        Args:
            filenames: Set of filenames to delete
        """
        for filename in filenames:
            self.cloud_client.delete(filename)

    def perform_sync(self) -> None:
        """
        Perform periodic synchronization.

        Detects changes since last sync and applies them to cloud.
        """
        new_files, modified_files, deleted_files = self.file_watcher.detect_changes()

        if not any([new_files, modified_files, deleted_files]):
            logger.info("No changes detected")
            return

        self._process_new_files(new_files)
        self._process_modified_files(modified_files)
        self._process_deleted_files(deleted_files)

        self.file_watcher.update_snapshot()

    def _process_new_files(self, new_files: set) -> None:
        """
        Process newly created files.

        Args:
            new_files: Set of new filenames
        """
        for filename in new_files:
            file_path = self.local_folder / filename
            self.cloud_client.load(str(file_path))

    def _process_modified_files(self, modified_files: set) -> None:
        """
        Process modified files.

        Args:
            modified_files: Set of modified filenames
        """
        for filename in modified_files:
            file_path = self.local_folder / filename
            self.cloud_client.reload(str(file_path))

    def _process_deleted_files(self, deleted_files: set) -> None:
        """
        Process deleted files.

        Args:
            deleted_files: Set of deleted filenames
        """
        for filename in deleted_files:
            self.cloud_client.delete(filename)

    def run(self, sync_interval: int) -> None:
        """
        Run continuous synchronization loop.

        Args:
            sync_interval: Time between syncs in seconds
        """
        logger.info(f"Starting sync loop (interval: {sync_interval}s)")

        try:
            while True:
                time.sleep(sync_interval)
                logger.info("Running periodic sync...")
                self.perform_sync()

        except KeyboardInterrupt:
            logger.info("Sync service stopped by user")
        except Exception as e:
            logger.error(f"Sync loop error: {e}")
