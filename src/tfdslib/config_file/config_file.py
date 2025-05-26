"""Configuration file access functions"""

import fcntl
import os
from typing import Any, cast

import yaml


def strip_yaml(config_name: str) -> str:
    """Strip the .yaml or .yml extension from the config name."""
    if config_name.endswith(".yaml"):
        return config_name[:-5]
    if config_name.endswith(".yml"):
        return config_name[:-4]
    return config_name


def get_root_folder() -> str:
    """Get the tfds root folder (defaulting to /opt/tfds)."""
    return os.environ.get("TFDS_ROOT_PATH", "/opt/tfds/")


def get_file_name(config_name: str) -> str:
    """Get a file path for a config, searching in secrets and config folders."""
    config_name = strip_yaml(config_name)
    attempt = os.path.join(get_root_folder(), "secrets", config_name + ".yaml")
    if os.path.isfile(attempt):
        return attempt
    return os.path.join(get_root_folder(), "config", config_name + ".yaml")


def config_exists(config_name: str) -> bool:
    """Check if a config file exists."""
    if config_name is None:
        raise ValueError("Config name cannot be None")
    file_path = get_file_name(config_name)
    return os.path.isfile(file_path)


def read_config(config_name: str) -> dict[str, Any]:
    """Read a configuration file, returning the config data as a dict."""
    if config_name is None:
        raise ValueError("Config name cannot be None")
    file_path = get_file_name(config_name)
    if not os.path.isfile(file_path):
        raise ValueError(f"Config '{config_name}' not found in config nor secrets.")

    with open(file_path, "r") as file:
        config: dict[str, str] = yaml.safe_load(file)
    if not config:
        raise ValueError(f"Config '{config_name}' in {file_path} is empty or invalid.")
    if config.get("config") is None:
        raise ValueError(f"Config '{config_name}' in {file_path} does not have a 'config' key.")
    return config


def write_config_to_file(config_name: str, config_data: dict[str, Any]) -> None:
    """Write a configuration file, meta key is stripped if present."""
    file_path = get_file_name(config_name)
    config_data.pop("meta", None)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        # Lock the file to prevent race conditions
        fcntl.flock(file, fcntl.LOCK_EX)
        yaml.dump(config_data, file, default_flow_style=False)
        fcntl.flock(file, fcntl.LOCK_UN)


def delete_config(config_name: str) -> None:
    """Delete a configuration file."""
    file_path = get_file_name(config_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f"Configuration '{file_path}' not found.")


def list_files(path: str) -> list[str]:
    """List all files in a directory."""
    try:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except FileNotFoundError:
        return []


def list_configs() -> list[str]:
    """List all available configurations (including the secrets)."""
    cfg_list = list_files(os.path.join(get_root_folder(), "config"))
    sec_list = list_files(os.path.join(get_root_folder(), "secrets"))
    return [strip_yaml(f) for f in cfg_list + sec_list if f.endswith(".yaml") or f.endswith(".yml")]


def get_config_from_file(config_name: str) -> dict[str, Any]:
    """Get the a config key from a file while validating the file."""
    cfg = read_config(config_name=config_name)["config"]
    return cast(dict[str, Any], cfg)
