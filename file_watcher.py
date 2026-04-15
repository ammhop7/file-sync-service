"""
File watcher module for tracking local file changes.
Detects new, modified, and deleted files by comparing snapshots.
"""

import os
from pathlib import Path
from typing import Dict, Set, Tuple

from loguru import logger


class FileWatcher:
    """
    Tracks changes in a local folder by comparing file snapshots.

    Uses file modification times to detect changes efficiently.
    """

    def __init__(self, folder_path: Path):
        """
        Initialize file watcher for a specific folder.

        Args:
            folder_path: Path to the folder to watch
        """
        self.folder_path = folder_path
        self.file_snapshot: Dict[str, float] = {}

    def get_current_files(self) -> Dict[str, float]:
        """
        Get current state of all files in the watched folder.

        Returns:
            Dict mapping filename to modification timestamp
        """
        current_files = {}

        try:
            for entry in os.scandir(self.folder_path):
                if entry.is_file():
                    stat = entry.stat()
                    current_files[entry.name] = stat.st_mtime

        except Exception as e:
            logger.error(f"Error scanning folder {self.folder_path}: {e}")

        return current_files

    def detect_changes(self) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Detect changes since last snapshot.

        Compares current file state with stored snapshot to identify:
        - New files (present now, not in snapshot)
        - Modified files (present in both, different modification time)
        - Deleted files (in snapshot, not present now)

        Returns:
            Tuple of (new_files, modified_files, deleted_files)
        """
        current_files = self.get_current_files()

        new_files = self._find_new_files(current_files)
        modified_files = self._find_modified_files(current_files)
        deleted_files = self._find_deleted_files(current_files)

        return new_files, modified_files, deleted_files

    def _find_new_files(self, current_files: Dict[str, float]) -> Set[str]:
        """
        Find files that are new (not in previous snapshot).

        Args:
            current_files: Current file state

        Returns:
            Set of new filenames
        """
        current_names = set(current_files.keys())
        snapshot_names = set(self.file_snapshot.keys())
        return current_names - snapshot_names

    def _find_modified_files(self, current_files: Dict[str, float]) -> Set[str]:
        """
        Find files that have been modified (different modification time).

        Args:
            current_files: Current file state

        Returns:
            Set of modified filenames
        """
        modified = set()

        for filename, current_mtime in current_files.items():
            if filename in self.file_snapshot:
                snapshot_mtime = self.file_snapshot[filename]
                if current_mtime > snapshot_mtime:
                    modified.add(filename)

        return modified

    def _find_deleted_files(self, current_files: Dict[str, float]) -> Set[str]:
        """
        Find files that have been deleted (in snapshot but not current).

        Args:
            current_files: Current file state

        Returns:
            Set of deleted filenames
        """
        current_names = set(current_files.keys())
        snapshot_names = set(self.file_snapshot.keys())
        return snapshot_names - current_names

    def update_snapshot(self) -> None:
        """
        Update the stored snapshot to current file state.

        Call this after processing changes to establish new baseline.
        """
        self.file_snapshot = self.get_current_files()

    def initialize_snapshot(self) -> None:
        """
        Initialize snapshot with current file state.

        Use this on startup to establish initial baseline.
        """
        self.file_snapshot = self.get_current_files()
        logger.info(f"Initialized file snapshot with {len(self.file_snapshot)} files")
