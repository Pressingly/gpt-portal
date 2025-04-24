import os
import logging
import threading
from typing import BinaryIO, Tuple, Optional, Dict, Any, List, Callable
from urllib.parse import urlparse
# Import only StorageProvider to avoid circular imports
from open_webui.storage.provider import StorageProvider
# Import local file utilities to avoid circular imports
from open_webui.moneta.storage.local_file_utils import upload_file, delete_file, delete_all_files
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import mimetypes

from open_webui.config import (
    S3_ACCESS_KEY_ID,
    S3_BUCKET_NAME,
    S3_ENDPOINT_URL,
    S3_KEY_PREFIX,
    S3_REGION_NAME,
    S3_SECRET_ACCESS_KEY,
    S3_USE_ACCELERATE_ENDPOINT,
    S3_ADDRESSING_STYLE,
    UPLOAD_DIR,
)

# Set up logging
log = logging.getLogger(__name__)


class MonetaS3StorageProvider(StorageProvider):
    """
    S3 Storage Provider for Moneta.

    This class implements the StorageProvider interface for AWS S3 or S3-compatible storage.
    It supports both explicit credentials and IAM role-based authentication.
    """

    def __init__(self):
        """
        Initialize the S3 storage provider with the configured settings.

        Creates an S3 client using either explicit credentials or IAM role-based authentication.
        """
        config = Config(
            s3={
                "use_accelerate_endpoint": S3_USE_ACCELERATE_ENDPOINT,
                "addressing_style": S3_ADDRESSING_STYLE,
            },
        )

        # If access key and secret are provided, use them for authentication
        if S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                "s3",
                region_name=S3_REGION_NAME,
                endpoint_url=S3_ENDPOINT_URL,
                aws_access_key_id=S3_ACCESS_KEY_ID,
                aws_secret_access_key=S3_SECRET_ACCESS_KEY,
                config=config,
            )
        else:
            # If no explicit credentials are provided, fall back to default AWS credentials
            # This supports workload identity (IAM roles for EC2, EKS, etc.)
            self.s3_client = boto3.client(
                "s3",
                region_name=S3_REGION_NAME,
                endpoint_url=S3_ENDPOINT_URL,
                config=config,
            )

        self.bucket_name = S3_BUCKET_NAME
        self.key_prefix = S3_KEY_PREFIX if S3_KEY_PREFIX else ""

        log.info(f"Initialized MonetaS3StorageProvider with bucket: {self.bucket_name}, prefix: {self.key_prefix}")

    def upload_file(self, file: BinaryIO, filename: str) -> Tuple[bytes, str]:
        """
        Upload a file to S3 storage.

        Args:
            file: The file-like object to upload
            filename: The name to give the file in storage

        Returns:
            Tuple containing the file contents as bytes and the S3 URI

        Raises:
            RuntimeError: If there's an error uploading to S3
        """
        log.debug(f"Uploading file {filename} to S3")
        _, file_path = upload_file(file, filename)

        try:
            s3_key = os.path.join(self.key_prefix, filename)

            # Determine content type based on file extension
            content_type = mimetypes.guess_type(filename)[0]
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            # Use with statement to ensure file is properly closed
            with open(file_path, "rb") as f:
                file_contents = f.read()

            s3_uri = f"s3://{self.bucket_name}/{s3_key}"
            log.info(f"Successfully uploaded file to {s3_uri}")
            return (file_contents, s3_uri)
        except ClientError as e:
            log.error(f"Error uploading file to S3: {e}")
            raise RuntimeError(f"Error uploading file to S3: {e}")

    def get_file(self, file_path: str) -> str:
        """
        Download a file from S3 storage.

        Args:
            file_path: The S3 URI of the file to download

        Returns:
            The local path where the file was downloaded

        Raises:
            RuntimeError: If there's an error downloading from S3
        """
        log.debug(f"Downloading file {file_path} from S3")
        try:
            s3_key = self._extract_s3_key(file_path)
            local_file_path = self._get_local_file_path(s3_key)
            self.s3_client.download_file(self.bucket_name, s3_key, local_file_path)
            log.info(f"Successfully downloaded file to {local_file_path}")
            return local_file_path
        except ClientError as e:
            log.error(f"Error downloading file from S3: {e}")
            raise RuntimeError(f"Error downloading file from S3: {e}")

    def delete_file(self, file_path: str) -> None:
        """
        Delete a file from S3 storage.

        Args:
            file_path: The S3 URI of the file to delete

        Raises:
            RuntimeError: If there's an error deleting from S3
        """
        log.debug(f"Deleting file {file_path} from S3")
        try:
            s3_key = self._extract_s3_key(file_path)
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            log.info(f"Successfully deleted file {s3_key} from S3")
        except ClientError as e:
            log.error(f"Error deleting file from S3: {e}")
            raise RuntimeError(f"Error deleting file from S3: {e}")

        # Always delete from local storage
        delete_file(file_path)

    def delete_all_files(self) -> None:
        """
        Delete all files from S3 storage that match the configured key prefix.

        This method handles pagination to ensure all objects are deleted.

        Raises:
            RuntimeError: If there's an error deleting from S3
        """
        log.info(f"Deleting all files with prefix {self.key_prefix} from S3 bucket {self.bucket_name}")
        try:
            # Use pagination to handle buckets with more than 1000 objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name)

            objects_to_delete: List[Dict[str, str]] = []

            for page in pages:
                if "Contents" in page:
                    for content in page["Contents"]:
                        # Skip objects that were not uploaded from open-webui in the first place
                        if not content["Key"].startswith(self.key_prefix):
                            continue

                        objects_to_delete.append({"Key": content["Key"]})

                        # S3 delete_objects can only handle 1000 objects at a time
                        if len(objects_to_delete) >= 1000:
                            self._delete_objects_batch(objects_to_delete)
                            objects_to_delete = []

            # Delete any remaining objects
            if objects_to_delete:
                self._delete_objects_batch(objects_to_delete)

            log.info(f"Successfully deleted all files with prefix {self.key_prefix}")
        except ClientError as e:
            log.error(f"Error deleting all files from S3: {e}")
            raise RuntimeError(f"Error deleting all files from S3: {e}")

        # Always delete from local storage
        delete_all_files()

    def _delete_objects_batch(self, objects: List[Dict[str, str]]) -> None:
        """
        Delete a batch of objects from S3.

        Args:
            objects: List of objects to delete in the format [{"Key": "key1"}, {"Key": "key2"}]
        """
        if not objects:
            return

        try:
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={"Objects": objects}
            )
        except ClientError as e:
            log.error(f"Error batch deleting objects from S3: {e}")
            raise RuntimeError(f"Error batch deleting objects from S3: {e}")

    # The s3 key is the name assigned to an object. It excludes the bucket name, but includes the internal path and the file name.
    def _extract_s3_key(self, full_file_path: str) -> str:
        """
        Extract the S3 key from a full S3 URI.

        Args:
            full_file_path: The full S3 URI (e.g., s3://bucket-name/path/to/file.txt)

        Returns:
            The S3 key (e.g., path/to/file.txt)
        """
        try:
            # Use urlparse for more robust parsing
            parsed_url = urlparse(full_file_path)
            if parsed_url.scheme != 's3':
                raise ValueError(f"Not an S3 URI: {full_file_path}")

            # Remove leading slash if present
            path = parsed_url.path
            if path.startswith('/'):
                path = path[1:]

            return path
        except Exception as e:
            # Fall back to the original implementation if parsing fails
            log.warning(f"Error parsing S3 URI with urlparse, falling back: {e}")
            return "/".join(full_file_path.split("//")[1].split("/")[1:])

    def _get_local_file_path(self, s3_key: str) -> str:
        """
        Get the local file path for an S3 key.

        Args:
            s3_key: The S3 key

        Returns:
            The local file path
        """
        # Extract just the filename from the S3 key
        filename = os.path.basename(s3_key)
        return os.path.join(UPLOAD_DIR, filename)

    def upload_file_non_blocking(self, file: BinaryIO, filename: str, callback: Callable = None) -> None:
        """
        Upload a file to S3 storage in a non-blocking way using threading.

        Args:
            file: The file-like object to upload
            filename: The name to give the file in storage
            callback: Optional callback function to call when upload is complete
                     The callback will receive (success, result) where success is a boolean
                     and result is either the S3 URI or the error message
        """
        def _upload_thread():
            try:
                result = self.upload_file(file, filename)
                if callback:
                    callback(True, result[1])  # Pass the S3 URI
            except Exception as e:
                log.error(f"Error in threaded upload to S3: {e}")
                if callback:
                    callback(False, str(e))

        thread = threading.Thread(target=_upload_thread)
        thread.daemon = True  # Thread will exit when main thread exits
        thread.start()
        return thread

    def get_file_non_blocking(self, file_path: str, callback: Callable = None) -> None:
        """
        Download a file from S3 storage in a non-blocking way using threading.

        Args:
            file_path: The S3 URI of the file to download
            callback: Optional callback function to call when download is complete
                     The callback will receive (success, result) where success is a boolean
                     and result is either the local file path or the error message
        """
        def _download_thread():
            try:
                local_path = self.get_file(file_path)
                if callback:
                    callback(True, local_path)
            except Exception as e:
                log.error(f"Error in threaded download from S3: {e}")
                if callback:
                    callback(False, str(e))

        thread = threading.Thread(target=_download_thread)
        thread.daemon = True  # Thread will exit when main thread exits
        thread.start()
        return thread
