from typing import Any, cast

from tfdslib.config_api import get_config_from_api, is_api_avaiable
from tfdslib.config_file import get_config_from_file


def get_config(config_name: str) -> dict[str, Any]:
    """Get a config, from api server if available or from file if avaiable."""
    if not config_name:
        raise ValueError("A config_name must be provided.")

    if is_api_avaiable():
        cfg = get_config_from_api(config_name)
    else:
        cfg = get_config_from_file(config_name)
    # Tthose functions are typed correctly, but mypy still won't accept it.
    # Try to remove the cast when we're on newer python
    return cast(dict[str, Any], cfg)
