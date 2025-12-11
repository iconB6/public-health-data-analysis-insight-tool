from src.service.repository import SQLiteRepository


def test_repository_save_and_load():
    repo = SQLiteRepository()

    record_id = repo.save_record({"data_source": "csv"})

    repo.save_dimensions(record_id, {"country": "UK", "city": "London"})
    repo.save_metrics(record_id, {"value": 10.5, "count": 3})

    record = repo.get_record(record_id)

    assert record["data_source"] == "csv"
    assert record["dimensions"]["country"] == "UK"
    assert record["metrics"]["value"] == 10.5
