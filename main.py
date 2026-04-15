"""
File Synchronization Service

Main entry point for the file sync service.
Synchronizes a local folder with cloud storage.
"""

import sys
from datetime import datetime

from loguru import logger

from config import load_config
from cloud.cloud_client import CloudClient
from cloud.mock_client import MockCloudClient
from sync_service import SyncService


def setup_logging(log_file_path: str) -> None:
    """
    Configure logging with loguru.

    Args:
        log_file_path: Path to log file
    """
    logger.remove()  # Remove default handler

    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # File output
    logger.add(
        log_file_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days"
    )


def main() -> None:
    """
    Main entry point for the sync service.

    Loads configuration, initializes components, and starts sync loop.
    """
    # Load and validate configuration
    config = load_config()

    # Setup logging
    setup_logging(config.log_file_path)

    # Log startup information
    logger.info("=" * 60)
    logger.info("File Synchronization Service Started")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Local folder: {config.local_folder_path}")
    logger.info(f"Remote folder: {config.remote_folder_name}")
    logger.info(f"Sync interval: {config.sync_interval} seconds")
    logger.info("=" * 60)

    try:
        # Initialize cloud client (use MockCloudClient for local testing)
        cloud_client = MockCloudClient(
            token=config.api_token,
            remote_folder=config.remote_folder_name
        )

        # Initialize sync service
        sync_service = SyncService(
            local_folder=config.local_folder_path,
            cloud_client=cloud_client
        )

        # Perform initial full sync
        sync_service.perform_initial_sync()

        # Start continuous sync loop
        sync_service.run(sync_interval=config.sync_interval)

    except KeyboardInterrupt:
        logger.info("Service stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
