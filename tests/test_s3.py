import datetime as dt
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

import tfdslib.s3 as s3_mod

MOCK_CONFIG = {"access_key": "ak", "secret_key": "sk", "url": "http://localhost"}


@pytest.fixture
def mock_s3_client():
    return MagicMock()


def test_get_s3_client_success(monkeypatch):
    mock_client = MagicMock()
    monkeypatch.setattr("tfdslib.s3.s3.get_config", lambda *_: MOCK_CONFIG)
    monkeypatch.setattr("boto3.client", lambda *a, **k: mock_client)
    result = s3_mod.get_s3_client()
    assert result == mock_client


def test_get_s3_client_no_config(monkeypatch):
    monkeypatch.setattr("tfdslib.s3.s3.get_config", lambda *_: None)
    with pytest.raises(ValueError):
        s3_mod.get_s3_client()


def test_get_s3_client_no_url(monkeypatch):
    cfg = MOCK_CONFIG.copy()
    cfg.pop("url")
    monkeypatch.setattr("tfdslib.s3.s3.get_config", lambda *_: cfg)
    with pytest.raises(ValueError):
        s3_mod.get_s3_client()


def test_is_s3_service_available_true(monkeypatch, mock_s3_client):
    mock_s3_client.list_buckets.return_value = {}
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    assert s3_mod.is_s3_service_available()


def test_is_s3_service_available_false(monkeypatch):
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: (_ for _ in ()).throw(Exception("fail")))
    assert not s3_mod.is_s3_service_available()


def test_bucket_exists_true(monkeypatch, mock_s3_client):
    mock_s3_client.list_buckets.return_value = {"Buckets": [{"Name": "bucket1"}]}
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    assert s3_mod.bucket_exists("bucket1")


def test_bucket_exists_false(monkeypatch, mock_s3_client):
    mock_s3_client.list_buckets.return_value = {"Buckets": [{"Name": "bucket2"}]}
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    assert not s3_mod.bucket_exists("bucket1")


def test_create_s3_bucket_exists(monkeypatch):
    monkeypatch.setattr(s3_mod, "bucket_exists", lambda b: True)
    assert s3_mod.create_bucket("bucket1")


def test_create_s3_bucket_success(monkeypatch, mock_s3_client):
    monkeypatch.setattr("tfdslib.s3.s3.bucket_exists", lambda b: False)
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    assert s3_mod.create_bucket("bucket1")
    mock_s3_client.create_bucket.assert_called_once_with(Bucket="bucket1")


def test_create_s3_bucket_client_error(monkeypatch, mock_s3_client):
    monkeypatch.setattr("tfdslib.s3.s3.bucket_exists", lambda b: False)
    mock_s3_client.create_bucket.side_effect = ClientError({"Error": {}}, "CreateBucket")
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    assert not s3_mod.create_bucket("bucket1")


def test_delete_s3_bucket_exists(monkeypatch, mock_s3_client):
    monkeypatch.setattr("tfdslib.s3.s3.bucket_exists", lambda b: True)
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    s3_mod.delete_bucket("bucket1")
    mock_s3_client.delete_bucket.assert_called_once_with(Bucket="bucket1")


def test_delete_s3_bucket_not_exists(monkeypatch):
    monkeypatch.setattr("tfdslib.s3.s3.bucket_exists", lambda b: False)
    mock_get_s3_client = MagicMock()
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", mock_get_s3_client)
    s3_mod.delete_bucket("bucket1")
    mock_get_s3_client.assert_not_called()


def test_put_file_success(monkeypatch, mock_s3_client):
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    result = s3_mod.put_file(local_path="local.txt", bucket="bucket", prefix="prefix", file_name="file.txt")
    assert result
    mock_s3_client.upload_file.assert_called_once_with("local.txt", "bucket", "prefix/file.txt")


def test_put_file_failure(monkeypatch, mock_s3_client):
    mock_s3_client.upload_file.side_effect = Exception("fail")
    monkeypatch.setattr(s3_mod, "get_s3_client", lambda: mock_s3_client)
    result = s3_mod.put_file(local_path="local.txt", bucket="bucket", prefix="prefix", file_name="file.txt")
    assert not result


def test_get_file_success(monkeypatch, mock_s3_client):
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    result = s3_mod.get_file(local_path="local.txt", bucket="bucket", prefix="prefix", file_name="file.txt")
    assert result
    mock_s3_client.download_file.assert_called_once_with("bucket", "prefix/file.txt", "local.txt")


def test_get_file_failure(monkeypatch, mock_s3_client):
    mock_s3_client.download_file.side_effect = ClientError({"Error": {}}, "DownloadFile")
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_s3_client)
    result = s3_mod.get_file("local.txt", "bucket", "prefix", "file.txt")
    assert not result


def test_list_files_returns_keys(monkeypatch):
    mock_client = MagicMock()
    mock_paginator = MagicMock()
    mock_pages = [
        {"Contents": [{"Key": "prefix/file1.txt"}, {"Key": "prefix/file2.txt"}]},
        {"Contents": [{"Key": "prefix/file3.txt"}]},
    ]
    mock_paginator.paginate.return_value = mock_pages
    mock_client.get_paginator.return_value = mock_paginator

    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_client)

    result = s3_mod.list_files("prefix", "bucket")
    assert result == ["prefix/file1.txt", "prefix/file2.txt", "prefix/file3.txt"]


def test_make_date_prefix():
    date = dt.date(2024, 5, 25)
    prefix = s3_mod.make_date_prefix(date)
    assert prefix == "2024/2024-05/25/"


def test_list_files_empty(monkeypatch):
    mock_client = MagicMock()
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = []
    mock_client.get_paginator.return_value = mock_paginator
    monkeypatch.setattr("tfdslib.s3.s3.get_s3_client", lambda: mock_client)
    result = s3_mod.list_files("prefix", "bucket")
    assert result == []


def test_list_files_for_dates(monkeypatch):
    # Patch make_prefix to return a predictable prefix
    monkeypatch.setattr("tfdslib.s3.s3.make_date_prefix", lambda date: f"prefix/{date}")
    # Patch list_files to return predictable files
    monkeypatch.setattr(
        "tfdslib.s3.s3.list_files", lambda prefix, bucket: [f"{prefix}/file1.txt", f"{prefix}/file2.txt"]
    )
    dates = [dt.date(2024, 5, 25), dt.date(2024, 5, 26)]
    bucket = "mybucket"
    result = s3_mod.list_files_for_dates(dates, bucket)
    expected = [
        "s3a://mybucket/prefix/2024-05-25/file1.txt",
        "s3a://mybucket/prefix/2024-05-25/file2.txt",
        "s3a://mybucket/prefix/2024-05-26/file1.txt",
        "s3a://mybucket/prefix/2024-05-26/file2.txt",
    ]
    assert result == expected
