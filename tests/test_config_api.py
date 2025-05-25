from unittest import mock

import pytest
import requests

import tfdslib.config_api as config_api


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    # Ensure environment variable is not set unless explicitly set in test
    monkeypatch.delenv("TFDS_CONFIG_URL", raising=False)


MOCK_CONFIG = {"config": {"foo": "bar"}, "meta": {"baz": "qux"}}


@pytest.fixture
def mock_requests_get_valid_config():
    """Mock config api server returning a valid config."""
    with mock.patch("requests.get") as mock_get:
        mock_response = mock.Mock()
        mock_response.json.return_value = MOCK_CONFIG
        mock_response.status_code = 200
        mock_response.raise_for_status = mock.Mock()
        mock_get.return_value = mock_response
        yield


def test_get_config_url_default():
    assert config_api.get_config_url() == "http://tfds-config:8005/api/configs"


def test_get_config_url_env(monkeypatch):
    monkeypatch.setenv("TFDS_CONFIG_URL", "http://custom-url")
    assert config_api.get_config_url() == "http://custom-url"


def test_is_api_avaiable_true(monkeypatch):
    with mock.patch("requests.head") as mock_head:
        mock_head.return_value.status_code = 200
        assert config_api.is_api_avaiable() is True


def test_is_api_avaiable_false(monkeypatch):
    with mock.patch("requests.head") as mock_head:
        mock_head.return_value.status_code = 404
        assert config_api.is_api_avaiable() is False


def test_is_api_avaiable_exception(monkeypatch):
    with mock.patch("requests.head", side_effect=requests.exceptions.RequestException):
        assert config_api.is_api_avaiable() is False


def test_get_full_config_response_success(monkeypatch, mock_requests_get_valid_config):
    result = config_api.get_full_config_response("myconfig.yaml")
    assert result == MOCK_CONFIG


def test_get_full_config_response_none(monkeypatch):
    with mock.patch("requests.get") as mock_get:
        mock_response = mock.Mock()
        mock_response.json.return_value = None
        mock_response.text = "not found"
        mock_response.raise_for_status = mock.Mock()
        mock_get.return_value = mock_response
        with pytest.raises(ValueError, match="Config 'myconfig' not found"):
            config_api.get_full_config_response("myconfig")


def test_get_full_config_response_none_name():
    with pytest.raises(ValueError, match="Config name cannot be None"):
        config_api.get_full_config_response(None)


def test_get_config_success(monkeypatch, mock_requests_get_valid_config):
    result = config_api.get_config_from_api("myconfig.yaml")
    assert result == MOCK_CONFIG["config"]


def test_get_config_no_config_key(monkeypatch):
    mock_json = MOCK_CONFIG.copy()
    mock_json.pop("config")
    with mock.patch("tfdslib.config_api.config_api.get_full_config_response", return_value=mock_json):
        with pytest.raises(ValueError, match="does not have a 'config' key"):
            config_api.get_config_from_api("myconfig.yaml")


def test_get_meta_success(monkeypatch, mock_requests_get_valid_config):
    result = config_api.get_meta("myconfig.yaml")
    assert result == MOCK_CONFIG["meta"]
