import datetime as dt

import pytest

from tfdslib.utils import date_range, parse_execution_date


def test_parse_execution_date_from_datetime():
    d = dt.datetime(2024, 5, 25, 12, 30)
    result = parse_execution_date(d)
    assert result == d


def test_parse_execution_date_from_date():
    d = dt.date(2024, 5, 25)
    result = parse_execution_date(d)
    assert result == dt.datetime(2024, 5, 25, 0, 0)


def test_parse_execution_date_from_string_datetime():
    s = "2024-05-25T12:30:00"
    result = parse_execution_date(s)
    assert result == dt.datetime(2024, 5, 25, 12, 30)


def test_parse_execution_date_from_string_date():
    s = "2024-05-25"
    result = parse_execution_date(s)
    assert result == dt.datetime(2024, 5, 25, 0, 0)


def test_parse_execution_date_invalid_string():
    with pytest.raises(ValueError):
        parse_execution_date("not-a-date")


def test_date_range_with_datetime():
    end = dt.datetime(2024, 5, 25, 12, 0)
    result = date_range(end, 3)
    expected = [
        dt.datetime(2024, 5, 23, 12, 0),
        dt.datetime(2024, 5, 24, 12, 0),
        dt.datetime(2024, 5, 25, 12, 0),
    ]
    assert result == expected


def test_date_range_with_string():
    end = "2024-05-25T12:00:00"
    result = date_range(end, 2)
    expected = [
        dt.datetime(2024, 5, 24, 12, 0),
        dt.datetime(2024, 5, 25, 12, 0),
    ]
    assert result == expected


def test_date_range_with_date():
    end = dt.date(2024, 5, 25)
    result = date_range(end, 2)
    expected = [
        dt.datetime(2024, 5, 24, 0, 0),
        dt.datetime(2024, 5, 25, 0, 0),
    ]
    assert result == expected
