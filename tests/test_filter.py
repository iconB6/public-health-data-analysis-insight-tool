import pytest
from src.service.data_filter import DataFilter


def test_filter_single_dimension():
    rows = [
        {"country": "USA", "year": 2024, "value": 10},
        {"country": "FRA", "year": 2024, "value": 20},
    ]

    f = DataFilter()
    result = f.filter(rows, {"country": "USA"})

    assert len(result) == 1
    assert result[0]["country"] == "USA"


def test_filter_multiple_dimensions():
    rows = [
        {"country": "USA", "year": 2023, "value": 10},
        {"country": "USA", "year": 2024, "value": 30},
        {"country": "FRA", "year": 2024, "value": 20},
    ]

    f = DataFilter()
    result = f.filter(rows, {"country": "USA", "year": 2024})

    assert len(result) == 1
    assert result[0]["value"] == 30


def test_filter_no_criteria_returns_all():
    rows = [
        {"country": "USA", "year": 2024},
        {"country": "FRA", "year": 2023},
    ]

    f = DataFilter()
    result = f.filter(rows, {})  # no criteria

    assert len(result) == 2


def test_filter_missing_dimension_key():
    rows = [
        {"country": "USA", "year": 2024},
        {"country": "FRA", "year": 2024},
    ]

    f = DataFilter()
    result = f.filter(rows, {"non_existing": "XYZ"})

    # None match
    assert len(result) == 0
