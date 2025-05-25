import os
from typing import Any, Union, cast

import requests

from tfdslib.config_file import strip_yaml


def get_config_url() -> str:
    """Get the config api server url."""
    return os.environ.get("TFDS_CONFIG_URL", "http://tfds-config:8005/api/configs")


def is_api_avaiable() -> bool:
    """Check if the config api server is available."""
    try:
        response = requests.head(get_config_url())
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_full_config_response(config_name: str) -> dict[str, Any]:
    """Get a config from the config api server."""
    if config_name is None:
        raise ValueError("Config name cannot be None")

    config_url = get_config_url() + "/" + strip_yaml(config_name)

    response = requests.get(config_url)
    response.raise_for_status()
    if response.json() is None:
        raise ValueError(f"Config '{config_name}' not found. config server response: {response.text}")
    # we're basically only checking for empty files, if there is a config element we assume it to be ok.
    return cast(dict[str, Any], response.json())


def get_config_from_api(config_name: str) -> dict[str, Any]:
    """Get the a config from the api as a dict."""
    response = get_full_config_response(config_name=config_name)
    cfg = response.get("config")
    if cfg is None:
        raise ValueError(f"Config '{config_name}' does not have a 'config' key. Got json: {response}")
    # we're basically only checking for empty files, if there is a config element we assume it to be ok.
    return cast(dict[str, Any], cfg)


def get_meta(config_name: str) -> Union[None, dict[str, Any]]:
    """Get the meta data from the config api response."""
    meta = get_full_config_response(config_name=config_name).get("meta")
    return cast(dict[str, Any], meta) if meta else None
