import os
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from tfdslib.config_file import config_file


@pytest.fixture
def temp_root(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setenv("TFDS_ROOT_PATH", temp_dir)
    os.makedirs(os.path.join(temp_dir, "config"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "secrets"), exist_ok=True)
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


def test_strip_yaml():
    assert config_file.strip_yaml("foo.yaml") == "foo"
    assert config_file.strip_yaml("foo.yml") == "foo"
    assert config_file.strip_yaml("foo.txt") == "foo.txt"
    assert config_file.strip_yaml("foo") == "foo"


def test_get_root_folder_env(monkeypatch):
    monkeypatch.setenv("TFDS_ROOT_PATH", "/tmp/testtfds")
    assert config_file.get_root_folder() == Path("/tmp/testtfds")


def test_get_root_folder_default(monkeypatch):
    monkeypatch.delenv("TFDS_ROOT_PATH", raising=False)
    assert config_file.get_root_folder() == Path("/opt/tfds/")


def test_get_file_name_prefers_secrets(temp_root):
    secrets_path = temp_root / "secrets" / "mycfg.yaml"
    with open(secrets_path, "w") as f:
        f.write("config: {foo: bar}")
    result = config_file.get_file_name("mycfg")
    assert result == secrets_path


def test_get_file_name_fallback_config(temp_root):
    config_path = temp_root / "config" / "mycfg.yaml"
    with open(config_path, "w") as f:
        f.write("config: {foo: bar}")
    result = config_file.get_file_name("mycfg")
    assert result == Path(config_path)


def test_config_exists_true(temp_root):
    config_path = temp_root / "config" / "exists.yaml"
    with open(config_path, "w") as f:
        f.write("config: {foo: bar}")
    assert config_file.config_exists("exists")


def test_config_exists_false(temp_root):
    assert not config_file.config_exists("doesnotexist")


def test_config_exists_none():
    with pytest.raises(ValueError):
        config_file.config_exists(None)


def test_read_config_success(temp_root):
    config_path = temp_root / "config" / "mycfg.yaml"
    data = {"config": {"foo": "bar"}}
    with open(config_path, "w") as f:
        yaml.dump(data, f)
    result = config_file.read_config("mycfg")
    assert result["config"]["foo"] == "bar"


def test_read_config_not_found(temp_root):
    with pytest.raises(ValueError):
        config_file.read_config("missing")


def test_read_config_empty_file(temp_root):
    config_path = os.path.join(temp_root, "config", "empty.yaml")
    with open(config_path, "w") as f:
        f.write("")
    with pytest.raises(ValueError):
        config_file.read_config("empty")


def test_read_config_no_config_key(temp_root):
    config_path = os.path.join(temp_root, "config", "nocfg.yaml")
    with open(config_path, "w") as f:
        yaml.dump({"notconfig": 123}, f)
    with pytest.raises(ValueError):
        config_file.read_config("nocfg")


def test_write_and_read_config(temp_root):
    data = {"config": {"foo": "bar"}, "meta": "should be removed"}
    config_file.write_config_to_file("mycfg", data.copy())
    path = os.path.join(temp_root, "config", "mycfg.yaml")
    with open(path) as f:
        loaded = yaml.safe_load(f)
    assert "meta" not in loaded
    assert loaded["config"]["foo"] == "bar"


def test_delete_config(temp_root, capsys):
    config_path = os.path.join(temp_root, "config", "todel.yaml")
    with open(config_path, "w") as f:
        f.write("config: {foo: bar}")
    config_file.delete_config("todel")
    assert not os.path.exists(config_path)


def test_delete_config_not_found(temp_root, capsys):
    config_file.delete_config("notfound")
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_list_files(temp_root):
    path = temp_root / "config"
    with open(path / "a.yaml", "w") as f:
        f.write("foo")
    with open(path / "b.txt", "w") as f:
        f.write("bar")
    files = config_file.list_files(path)
    assert Path(path / "a.yaml") in files
    assert Path(path / "b.txt") in files


def test_list_files_not_found():
    assert config_file.list_files("/nonexistent/path") == []


def test_list_configs(temp_root):
    with open(os.path.join(temp_root, "config", "a.yaml"), "w") as f:
        f.write("foo")
    with open(os.path.join(temp_root, "secrets", "b.yml"), "w") as f:
        f.write("bar")
    with open(os.path.join(temp_root, "config", "c.txt"), "w") as f:
        f.write("baz")
    configs = config_file.list_configs()
    assert "a" in configs
    assert "b" in configs
    assert "c" not in configs


def test_get_config_success(temp_root):
    config_path = os.path.join(temp_root, "config", "mycfg.yaml")
    data = {"config": {"foo": "bar"}}
    with open(config_path, "w") as f:
        yaml.dump(data, f)
    result = config_file.get_config_from_file("mycfg")
    assert result["foo"] == "bar"
