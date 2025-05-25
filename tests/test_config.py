from unittest.mock import patch

import pytest

from tfdslib.config.config import get_config


@pytest.fixture
def mock_api_config():
    return {"foo": "bar"}


@pytest.fixture
def mock_file_config():
    return {"bar": "baz"}


def test_get_config_api(monkeypatch, mock_api_config):
    with (
        patch("tfdslib.config.config.is_api_avaiable", return_value=True),
        patch("tfdslib.config.config.get_config_from_api", return_value=mock_api_config),
    ):
        result = get_config("myconfig")
        assert result == mock_api_config


def test_get_config_file(monkeypatch, mock_file_config):
    with (
        patch("tfdslib.config.config.is_api_avaiable", return_value=False),
        patch("tfdslib.config.config.get_config_from_file", return_value=mock_file_config),
    ):
        result = get_config("myconfig")
        assert result == mock_file_config


def test_get_config_raises_on_none():
    with pytest.raises(ValueError, match="A config_name must be provided."):
        get_config(None)


def test_get_config_raises_on_empty():
    with pytest.raises(ValueError, match="A config_name must be provided."):
        get_config("")
