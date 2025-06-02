import datetime as dt
import logging
import sys
from typing import Optional, Union


def parse_execution_date(execution_date: Union[str, dt.date, dt.datetime]) -> dt.datetime:
    """Parse an airflow execution (iso format) date to a datetime object, accepts date and datetime as well, always returning a datetime."""
    if isinstance(execution_date, dt.datetime):
        return execution_date
    if isinstance(execution_date, dt.date):
        # Convert date to datetime at midnight
        return dt.datetime.combine(execution_date, dt.time())

    return dt.datetime.fromisoformat(execution_date)


def date_range(execution_date: Union[str, dt.datetime, dt.date], length: int) -> list[dt.datetime]:
    """Return a series of <length> datetimes, ending with execution_date."""
    start_date = parse_execution_date(execution_date)
    return [start_date - dt.timedelta(days=i) for i in reversed(range(length))]


def setup_logging(
    tfds_package_names: list[str] = ["tfdslib", "tfds"],
    current_module: Optional[str] = None,
    tfds_level: int = logging.DEBUG,
    global_level: int = logging.WARNING,
) -> None:
    root_logger = logging.getLogger()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # other packages
    root_logger.setLevel(global_level)  # Third-party default: only warn and up

    # our packages
    pkg_lst = tfds_package_names.copy()
    if current_module:
        pkg_lst.append(current_module.split(".")[0])

    for pkg in pkg_lst:
        package_logger = logging.getLogger(pkg)
        package_logger.setLevel(tfds_level)
