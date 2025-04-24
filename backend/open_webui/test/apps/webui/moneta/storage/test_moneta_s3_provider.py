import io
import os
import time
import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from open_webui.moneta.storage.moneta_s3_provider import MonetaS3StorageProvider
from open_webui.moneta.storage.local_file_utils import upload_file, delete_file, delete_all_files


def mock_upload_dir(monkeypatch, tmp_path):
    """Fixture to monkey-patch the UPLOAD_DIR and create a temporary directory."""
    directory = tmp_path / "uploads"
    directory.mkdir()
    monkeypatch.setattr("open_webui.config.UPLOAD_DIR", str(directory))
    return directory


@mock_aws
class TestMonetaS3StorageProvider:

    def __init__(self):
        self.Storage = MonetaS3StorageProvider()
        self.Storage.bucket_name = "moneta-test-bucket"
        self.s3_client = boto3.resource("s3", region_name="us-east-1")
        self.file_content = b"test content"
        self.filename = "test.txt"
        self.filename_extra = "test_extra.txt"
        self.file_bytesio_empty = io.BytesIO()
        super().__init__()

    def test_upload_file(self, monkeypatch, tmp_path):
        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        # S3 checks
        with pytest.raises(Exception):
            self.Storage.upload_file(io.BytesIO(self.file_content), self.filename)
        self.s3_client.create_bucket(Bucket=self.Storage.bucket_name)
        contents, s3_file_path = self.Storage.upload_file(
            io.BytesIO(self.file_content), self.filename
        )
        object = self.s3_client.Object(self.Storage.bucket_name, self.filename)
        assert self.file_content == object.get()["Body"].read()
        # local checks
        assert (upload_dir / self.filename).exists()
        assert (upload_dir / self.filename).read_bytes() == self.file_content
        assert contents == self.file_content
        assert s3_file_path == f"s3://{self.Storage.bucket_name}/{self.filename}"
        with pytest.raises(ValueError):
            self.Storage.upload_file(self.file_bytesio_empty, self.filename)

    def test_get_file(self, monkeypatch, tmp_path):
        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        self.s3_client.create_bucket(Bucket=self.Storage.bucket_name)
        contents, s3_file_path = self.Storage.upload_file(
            io.BytesIO(self.file_content), self.filename
        )
        file_path = self.Storage.get_file(s3_file_path)
        assert file_path == str(upload_dir / self.filename)
        assert (upload_dir / self.filename).exists()

    def test_delete_file(self, monkeypatch, tmp_path):
        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        self.s3_client.create_bucket(Bucket=self.Storage.bucket_name)
        contents, s3_file_path = self.Storage.upload_file(
            io.BytesIO(self.file_content), self.filename
        )
        assert (upload_dir / self.filename).exists()
        self.Storage.delete_file(s3_file_path)
        assert not (upload_dir / self.filename).exists()
        with pytest.raises(ClientError) as exc:
            self.s3_client.Object(self.Storage.bucket_name, self.filename).load()
        error = exc.value.response["Error"]
        assert error["Code"] == "404"
        assert error["Message"] == "Not Found"

    def test_delete_all_files(self, monkeypatch, tmp_path):
        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        self.s3_client.create_bucket(Bucket=self.Storage.bucket_name)
        # Upload multiple files
        self.Storage.upload_file(io.BytesIO(self.file_content), self.filename)
        self.Storage.upload_file(io.BytesIO(self.file_content), self.filename_extra)

        # Verify files exist
        assert (upload_dir / self.filename).exists()
        assert (upload_dir / self.filename_extra).exists()

        # Delete all files
        self.Storage.delete_all_files()

        # Verify files are deleted
        assert not (upload_dir / self.filename).exists()
        assert not (upload_dir / self.filename_extra).exists()

        # Verify S3 objects are deleted
        with pytest.raises(ClientError) as exc:
            self.s3_client.Object(self.Storage.bucket_name, self.filename).load()
        error = exc.value.response["Error"]
        assert error["Code"] == "404"

        with pytest.raises(ClientError) as exc:
            self.s3_client.Object(self.Storage.bucket_name, self.filename_extra).load()
        error = exc.value.response["Error"]
        assert error["Code"] == "404"

    def test_extract_s3_key(self):
        # Test with standard S3 URI
        s3_uri = f"s3://{self.Storage.bucket_name}/path/to/file.txt"
        assert self.Storage._extract_s3_key(s3_uri) == "path/to/file.txt"

        # Test with URI that has no path
        s3_uri = f"s3://{self.Storage.bucket_name}"
        assert self.Storage._extract_s3_key(s3_uri) == ""

        # Test with URI that has leading slash
        s3_uri = f"s3://{self.Storage.bucket_name}/file.txt"
        assert self.Storage._extract_s3_key(s3_uri) == "file.txt"

        # Test fallback with malformed URI
        s3_uri = f"s3:{self.Storage.bucket_name}/file.txt"
        assert self.Storage._extract_s3_key(s3_uri) == f"{self.Storage.bucket_name}/file.txt"

    def test_batch_delete(self, monkeypatch, tmp_path):
        self.s3_client.create_bucket(Bucket=self.Storage.bucket_name)

        # Create a list of objects to delete
        objects = [{"Key": "file1.txt"}, {"Key": "file2.txt"}]

        # Upload the files first
        self.s3_client.Object(self.Storage.bucket_name, "file1.txt").put(Body=b"test")
        self.s3_client.Object(self.Storage.bucket_name, "file2.txt").put(Body=b"test")

        # Delete the objects
        self.Storage._delete_objects_batch(objects)

        # Verify objects are deleted
        with pytest.raises(ClientError) as exc:
            self.s3_client.Object(self.Storage.bucket_name, "file1.txt").load()
        error = exc.value.response["Error"]
        assert error["Code"] == "404"

        with pytest.raises(ClientError) as exc:
            self.s3_client.Object(self.Storage.bucket_name, "file2.txt").load()
        error = exc.value.response["Error"]
        assert error["Code"] == "404"

    def test_init_without_credentials(self, monkeypatch):
        """Test that MonetaS3StorageProvider can initialize without explicit credentials."""
        # Temporarily unset the environment variables
        monkeypatch.setattr("open_webui.config.S3_ACCESS_KEY_ID", None)
        monkeypatch.setattr("open_webui.config.S3_SECRET_ACCESS_KEY", None)

        # Should not raise an exception
        storage = MonetaS3StorageProvider()
        assert storage.s3_client is not None
        assert storage.bucket_name == "moneta-test-bucket"  # Using the test bucket name

    def test_upload_file_non_blocking(self, monkeypatch, tmp_path):
        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        self.s3_client.create_bucket(Bucket=self.Storage.bucket_name)

        # Create a callback to capture the result
        result = {"success": None, "data": None}

        def callback(success, data):
            result["success"] = success
            result["data"] = data

        # Start the non-blocking upload
        thread = self.Storage.upload_file_non_blocking(
            io.BytesIO(self.file_content), "non_blocking_test.txt", callback
        )

        # Wait for the thread to complete (with timeout)
        thread.join(timeout=5)

        # Check that the thread completed
        assert not thread.is_alive()

        # Check the result
        assert result["success"] is True
        assert result["data"] == f"s3://{self.Storage.bucket_name}/non_blocking_test.txt"

        # Verify the file was uploaded to S3
        object = self.s3_client.Object(self.Storage.bucket_name, "non_blocking_test.txt")
        assert self.file_content == object.get()["Body"].read()

    def test_get_file_non_blocking(self, monkeypatch, tmp_path):
        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        self.s3_client.create_bucket(Bucket=self.Storage.bucket_name)

        # First upload a file
        contents, s3_file_path = self.Storage.upload_file(
            io.BytesIO(self.file_content), "non_blocking_download_test.txt"
        )

        # Create a callback to capture the result
        result = {"success": None, "data": None}

        def callback(success, data):
            result["success"] = success
            result["data"] = data

        # Start the non-blocking download
        thread = self.Storage.get_file_non_blocking(s3_file_path, callback)

        # Wait for the thread to complete (with timeout)
        thread.join(timeout=5)

        # Check that the thread completed
        assert not thread.is_alive()

        # Check the result
        assert result["success"] is True
        assert os.path.exists(result["data"])

        # Verify the file content
        with open(result["data"], "rb") as f:
            assert f.read() == self.file_content
