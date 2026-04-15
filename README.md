# File Synchronization Service

A production-ready Python service that synchronizes files between a local folder and cloud storage. Built with clean architecture and best practices for backend development.

## Features

- **Automatic Synchronization**: Continuously monitors and syncs local folder changes to cloud storage
- **Change Detection**: Tracks new, modified, and deleted files using modification timestamps
- **Initial Full Sync**: Performs complete synchronization on startup
- **Robust Error Handling**: Logs errors without stopping the service
- **Configurable**: Easy configuration via environment variables
- **Extensible Architecture**: Modular design with abstract cloud client interface

## Project Structure

```
project/
├── main.py                 # Entry point and service orchestration
├── config.py              # Configuration loading and validation
├── sync_service.py        # Synchronization logic coordinator
├── file_watcher.py        # Local file change detection
├── cloud/
│   ├── __init__.py
│   ├── base.py           # Abstract cloud client interface
│   └── cloud_client.py   # Cloud API implementation
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
└── .gitignore            # Git ignore rules
```

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`:
```env
LOCAL_FOLDER_PATH=./sync_folder
REMOTE_FOLDER_NAME=my-sync-folder
API_TOKEN=your_actual_api_token
SYNC_INTERVAL=300
LOG_FILE_PATH=sync_service.log
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LOCAL_FOLDER_PATH` | Path to local folder to sync | Yes | - |
| `REMOTE_FOLDER_NAME` | Name of remote cloud folder | Yes | - |
| `API_TOKEN` | Cloud service API token | Yes | - |
| `SYNC_INTERVAL` | Sync interval in seconds | Yes | - |
| `LOG_FILE_PATH` | Path to log file | No | `sync_service.log` |

### Validation

The service validates configuration on startup:
- Local folder must exist
- API token must be valid
- Sync interval must be a positive integer

If validation fails, the service exits with a clear error message.

## Usage

Run the service:
```bash
python main.py
```

The service will:
1. Load and validate configuration
2. Connect to cloud storage
3. Perform initial full synchronization
4. Start continuous sync loop

Stop the service with `Ctrl+C`.

## How It Works

### Initial Sync
On startup, the service compares local and remote files:
- Files only in local → upload to cloud
- Files in both locations → upload if local is newer
- Files only in remote → delete from cloud

### Periodic Sync
Every `SYNC_INTERVAL` seconds, the service:
1. Detects changes since last sync
2. Uploads new files
3. Re-uploads modified files
4. Deletes removed files from cloud

### Change Detection
Uses file modification timestamps to efficiently detect:
- **New files**: Present locally but not in previous snapshot
- **Modified files**: Modification time changed since last snapshot
- **Deleted files**: In previous snapshot but no longer present

## Architecture

### Modular Design

- **config.py**: Handles all configuration loading and validation
- **file_watcher.py**: Tracks local file system changes
- **sync_service.py**: Coordinates synchronization operations
- **cloud/base.py**: Defines cloud client interface (extensibility)
- **cloud/cloud_client.py**: Implements cloud API interactions

### Design Principles

- Single Responsibility: Each module has one clear purpose
- No global variables: All state is encapsulated
- No nested loops: Uses sets and dictionaries for efficient comparisons
- Error isolation: Runtime errors don't stop the service
- PEP 8 compliant: Clean, readable Python code

## Logging

Uses `loguru` for structured logging:

- **Console**: Colored output with timestamps
- **File**: Rotated logs (10 MB max, 30 days retention)

Log levels:
- `INFO`: Successful operations and status updates
- `ERROR`: Failed operations (service continues)

Example log output:
```
2026-04-15 20:00:00 | INFO     | File Synchronization Service Started
2026-04-15 20:00:00 | INFO     | Local folder: /path/to/sync_folder
2026-04-15 20:00:01 | INFO     | Cloud connection validated successfully
2026-04-15 20:00:01 | INFO     | Uploaded: document.pdf
2026-04-15 20:00:02 | INFO     | Initial synchronization completed
```

## Error Handling

### Configuration Errors
Stop the service immediately:
- Missing required environment variables
- Invalid local folder path
- Invalid API token
- Invalid sync interval

### Runtime Errors
Log and continue:
- Network failures during upload/download
- Individual file operation failures
- Temporary cloud service issues

## Extending the Service

### Adding New Cloud Providers

1. Create a new class in `cloud/` that inherits from `BaseCloudClient`
2. Implement all abstract methods: `load()`, `reload()`, `delete()`, `get_info()`
3. Update `main.py` to use your new client

Example:
```python
from cloud.base import BaseCloudClient

class MyCloudClient(BaseCloudClient):
    def load(self, file_path: str) -> bool:
        # Your implementation
        pass
    
    # Implement other methods...
```

## Development

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Keep functions focused (single responsibility)

### Testing
Create a test folder and add files to see sync in action:
```bash
mkdir sync_folder
echo "test" > sync_folder/test.txt
python main.py
```

## License

MIT License - feel free to use this project for your portfolio or production use.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow the existing code style
4. Add tests if applicable
5. Submit a pull request

## Author

Built as a portfolio project demonstrating:
- Clean Python architecture
- Production-ready error handling
- Modular, extensible design
- Professional logging and configuration
- Backend development best practices
