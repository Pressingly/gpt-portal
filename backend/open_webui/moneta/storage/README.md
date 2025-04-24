# Moneta Storage Providers

This directory contains storage providers specific to the Moneta project.

## MonetaS3StorageProvider

The `MonetaS3StorageProvider` is an enhanced S3 storage provider that extends the base `StorageProvider` interface with additional features:

### Features

1. **Non-blocking Operations**: Provides non-blocking methods for file uploads and downloads using threading.
2. **Content Type Detection**: Automatically detects and sets the appropriate content type for uploaded files.
3. **Improved S3 URI Parsing**: Uses `urlparse` for more robust S3 URI parsing with fallback to the original implementation.
4. **Batch Deletion**: Efficiently deletes multiple objects in batches of up to 1000 objects.
5. **Pagination Support**: Handles pagination for S3 list operations to support buckets with more than 1000 objects.
6. **Comprehensive Logging**: Detailed logging for all operations.
7. **Resource Management**: Properly closes file handles to prevent resource leaks.

### Configuration

The provider uses the following environment variables:

```
S3_ACCESS_KEY_ID - AWS access key ID
S3_SECRET_ACCESS_KEY - AWS secret access key
S3_BUCKET_NAME - S3 bucket name
S3_ENDPOINT_URL - S3 endpoint URL (for MinIO, etc.)
S3_KEY_PREFIX - Prefix for S3 keys
S3_REGION_NAME - AWS region name
S3_USE_ACCELERATE_ENDPOINT - Whether to use S3 accelerate endpoint
S3_ADDRESSING_STYLE - S3 addressing style (path or virtual)
UPLOAD_DIR - Local directory for temporary file storage
```

### Usage

```python
from open_webui.moneta.storage.moneta_s3_provider import MonetaS3StorageProvider

# Initialize the provider
storage = MonetaS3StorageProvider()

# Upload a file
with open('file.txt', 'rb') as f:
    contents, s3_uri = storage.upload_file(f, 'file.txt')

# Download a file
local_path = storage.get_file(s3_uri)

# Delete a file
storage.delete_file(s3_uri)

# Delete all files
storage.delete_all_files()

# Non-blocking upload with callback
def upload_callback(success, result):
    if success:
        print(f"Upload successful: {result}")
    else:
        print(f"Upload failed: {result}")

with open('file.txt', 'rb') as f:
    storage.upload_file_non_blocking(f, 'file.txt', upload_callback)

# Non-blocking download with callback
def download_callback(success, result):
    if success:
        print(f"Download successful: {result}")
    else:
        print(f"Download failed: {result}")

storage.get_file_non_blocking('s3://bucket/file.txt', download_callback)
```

### Testing

The provider includes comprehensive unit tests that use the `moto` library to mock AWS S3 services. Run the tests with:

```bash
pytest backend/open_webui/test/apps/webui/moneta/storage/test_moneta_s3_provider.py
```
