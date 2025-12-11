import pytest
from src.infrastructure.data_loader_factory import DataLoaderFactory
from src.infrastructure.csv_loader import CSVLoader


def test_factory_returns_csv_loader():
    loader = DataLoaderFactory.create_loader(
        source_type="csv",
        source_path="tests/data/sample.csv"
    )
    assert isinstance(loader, CSVLoader), "Factory must return a CSVLoader instance"


def test_factory_type_case_insensitive():
    loader = DataLoaderFactory.create_loader(
        source_type="CSV",
        source_path="tests/data/sample.csv"
    )
    assert isinstance(loader, CSVLoader)


def test_factory_invalid_type_raises_error():
    with pytest.raises(ValueError):
        DataLoaderFactory.create_loader(
            source_type="xml",
            source_path="fake_path.xml"
        )

def test_factory_missing_type_raises_error():
    with pytest.raises(ValueError):
        DataLoaderFactory.create_loader(
            source_type="",
            source_path="tests/data/sample.csv"
        )
