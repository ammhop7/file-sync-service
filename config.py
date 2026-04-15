"""
Configuration module for file sync service.
Loads and validates environment variables from .env file.
"""

import os
import sys
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv
from loguru import logger


class Config(NamedTuple):
    """Configuration container with validated settings."""
    local_folder_path: Path
    remote_folder_name: str
    api_token: str
    sync_interval: int
    log_file_path: str


def load_config() -> Config:
    """
    Load and validate configuration from environment variables.

    Returns:
        Config: Validated configuration object

    Raises:
        SystemExit: If configuration is invalid or missing
    """
    load_dotenv()

    local_folder = _get_required_env("LOCAL_FOLDER_PATH")
    remote_folder = _get_required_env("REMOTE_FOLDER_NAME")
    api_token = _get_required_env("API_TOKEN")
    sync_interval = _get_required_env("SYNC_INTERVAL")
    log_file = os.getenv("LOG_FILE_PATH", "sync_service.log")

    local_path = _validate_local_folder(local_folder)
    interval = _validate_sync_interval(sync_interval)
    _validate_api_token(api_token)

    return Config(
        local_folder_path=local_path,
        remote_folder_name=remote_folder,
        api_token=api_token,
        sync_interval=interval,
        log_file_path=log_file
    )


def _get_required_env(key: str) -> str:
    """
    Get required environment variable or exit with error.

    Args:
        key: Environment variable name

    Returns:
        str: Environment variable value
    """
    value = os.getenv(key)
    if not value:
        logger.error(f"Missing required environment variable: {key}")
        logger.error("Please check your .env file")
        sys.exit(1)
    return value


def _validate_local_folder(path: str) -> Path:
    """
    Validate that local folder exists and is accessible.

    Args:
        path: Local folder path string

    Returns:
        Path: Validated Path object
    """
    folder_path = Path(path).resolve()

    if not folder_path.exists():
        logger.error(f"Local folder does not exist: {folder_path}")
        sys.exit(1)

    if not folder_path.is_dir():
        logger.error(f"Path is not a directory: {folder_path}")
        sys.exit(1)

    return folder_path


def _validate_sync_interval(interval: str) -> int:
    """
    Validate sync interval is a positive integer.

    Args:
        interval: Sync interval as string

    Returns:
        int: Validated interval in seconds
    """
    try:
        interval_int = int(interval)
    except ValueError:
        logger.error(f"SYNC_INTERVAL must be an integer, got: {interval}")
        sys.exit(1)

    if interval_int <= 0:
        logger.error(f"SYNC_INTERVAL must be positive, got: {interval_int}")
        sys.exit(1)

    return interval_int


def _validate_api_token(token: str) -> None:
    """
    Validate API token is not empty or placeholder.

    Args:
        token: API token string
    """
    if token in ("your_api_token_here", ""):
        logger.error("Invalid API_TOKEN: Please set a valid token in .env file")
        sys.exit(1)
