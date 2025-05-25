from unittest import mock

import pytest

import tfdslib.spark as spark_mod

MOCK_CONFIG = {"access_key": "AKIA_TEST", "secret_key": "SECRET_TEST"}


@pytest.fixture
def patch_get_config():
    with mock.patch("tfdslib.spark.spark.get_config", return_value=MOCK_CONFIG):
        yield


@pytest.fixture
def mock_spark_conf():
    conf = mock.Mock()
    conf.setAppName.return_value = conf
    conf.set.return_value = conf
    conf.setMaster.return_value = conf
    return conf


@pytest.fixture
def mock_spark_builder(mock_spark_conf):
    builder = mock.Mock()
    builder.config.return_value = builder
    return builder


@pytest.fixture
def patch_pyspark_and_delta(monkeypatch, mock_spark_conf, mock_spark_builder):
    monkeypatch.setattr("pyspark.conf.SparkConf", lambda: mock_spark_conf)
    monkeypatch.setattr("pyspark.sql.SparkSession.builder", mock_spark_builder)
    delta_mock = mock.Mock()
    delta_mock.return_value.getOrCreate.return_value = "spark_session"
    monkeypatch.setattr("tfdslib.spark.spark.configure_spark_with_delta_pip", delta_mock)
    return delta_mock


def test_get_spark_session_local(patch_get_config, patch_pyspark_and_delta, mock_spark_conf, mock_spark_builder):
    session = spark_mod.get_spark_session("test_app", use_local=True)
    assert session == "spark_session"
    mock_spark_conf.setAppName.assert_called_with("test_app")
    mock_spark_conf.setMaster.assert_called_with("local[*]")
    mock_spark_conf.set.assert_any_call("spark.hadoop.fs.s3a.access.key", "AKIA_TEST")
    mock_spark_conf.set.assert_any_call("spark.hadoop.fs.s3a.secret.key", "SECRET_TEST")


def test_get_spark_session_cluster(patch_get_config, patch_pyspark_and_delta, mock_spark_conf, mock_spark_builder):
    session = spark_mod.get_spark_session("test_app", use_local=False)
    assert session == "spark_session"
    mock_spark_conf.setAppName.assert_called_with("test_app")
    mock_spark_conf.setMaster.assert_not_called()
    mock_spark_conf.set.assert_any_call("spark.hadoop.fs.s3a.access.key", "AKIA_TEST")
    mock_spark_conf.set.assert_any_call("spark.hadoop.fs.s3a.secret.key", "SECRET_TEST")


def test_show_cfg_prints(monkeypatch):
    mock_conf = mock.Mock()
    mock_conf.getAll.return_value = [
        ("spark.app.name", "test_app"),
        ("spark.hadoop.fs.s3a.access.key", "AKIA_TEST"),
        ("spark.submit.pyFiles", "file1.py,file2.py"),
    ]
    mock_spark_session = mock.Mock()
    mock_spark_session.sparkContext.getConf.return_value = mock_conf
    with mock.patch("builtins.print") as mock_print:
        spark_mod.show_cfg(mock_spark_session)
        assert mock_print.call_count > 0


def test_show_spark_info_prints(monkeypatch):
    mock_conf = mock.Mock()
    mock_conf.get.side_effect = lambda k: {
        "spark.app.name": "test_app",
        "spark.master": "local[*]",
        "spark.sql.warehouse.dir": "/tmp/warehouse",
        "spark.hadoop.fs.s3a.endpoint": "s3.amazonaws.com",
    }[k]
    mock_spark_session = mock.Mock()
    mock_spark_session.sparkContext.getConf.return_value = mock_conf
    with mock.patch("builtins.print") as mock_print:
        spark_mod.show_spark_info(mock_spark_session)
        assert mock_print.call_count > 0


def test_show_db_prints(monkeypatch):
    db1 = mock.Mock()
    db1.name = "db1"
    db2 = mock.Mock()
    db2.name = "db2"
    tbl1 = mock.Mock()
    tbl1.name = "table1"
    tbl2 = mock.Mock()
    tbl2.name = "table2"
    mock_spark_session = mock.Mock()
    mock_spark_session.catalog.listDatabases.return_value = [db1, db2]
    mock_spark_session.catalog.listTables.side_effect = lambda db: [tbl1] if db == "db1" else [tbl2]
    with mock.patch("builtins.print") as mock_print:
        spark_mod.show_dbs(mock_spark_session)
        assert mock_print.call_count > 0
