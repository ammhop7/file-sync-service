"""
Custom exceptions for file synchronization service.
Provides clear error hierarchy for better error handling.
"""


class SyncServiceError(Exception):
    """Base exception for all sync service errors."""
    pass


class ConfigurationError(SyncServiceError):
    """Raised when configuration is invalid or missing."""
    pass


class CloudConnectionError(SyncServiceError):
    """Raised when connection to cloud service fails."""
    pass


class CloudAuthenticationError(CloudConnectionError):
    """Raised when cloud authentication fails."""
    pass


class CloudTimeoutError(CloudConnectionError):
    """Raised when cloud request times out."""
    pass


class CloudUploadError(SyncServiceError):
    """Raised when file upload to cloud fails."""
    pass


class CloudDeleteError(SyncServiceError):
    """Raised when file deletion from cloud fails."""
    pass


class FileWatcherError(SyncServiceError):
    """Raised when file watcher encounters an error."""
    pass


class LocalFolderError(SyncServiceError):
    """Raised when local folder operations fail."""
    pass
