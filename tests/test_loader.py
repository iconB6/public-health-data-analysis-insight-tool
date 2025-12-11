'''
sprint1: Implement CSVLoader and JSONLoader with unit tests
'''
import os
import pandas as pd
from src.loader.csv_loader import CSVLoader
from src.loader.db_writer import DBWriter
import sqlite3


def test_csv_loader_loads_data():
    loader = CSVLoader(filepath="tests/data/sample.csv")
    df = loader.load()
    assert not df.empty
    assert isinstance(df, pd.DataFrame)

    # automated detection of dimensions and metrics
    dims, metrics = loader.detect_fields(df)
    
    # restraints: at least one dimension and one metric
    assert len(dims) >= 1
    assert len(metrics) >= 1


def test_loader_saves_to_database(tmp_path):
    # prepare sample data
    df = pd.DataFrame({
        "country": ["BTN"],
        "group": ["ad_chronic"],
        "value_1": [0.0],
        "year": [2024],
    })

    # 1. prepare dimension and metric fields
    dimension_fields = ["country", "group", "year"]
    metric_fields = ["value_1"]

    # 2. create writer and save
    db_path = tmp_path / "test.db"
    writer = DBWriter(db_path=str(db_path))

    writer.init_schema()
    writer.write(df, dimension_fields, metric_fields)

    # 3. validate saved data
    conn = sqlite3.connect(str(db_path))

    rec_count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    assert rec_count == 1

    dim_count = conn.execute("SELECT COUNT(*) FROM record_dimensions").fetchone()[0]
    assert dim_count == 3

    metric_count = conn.execute("SELECT COUNT(*) FROM record_metrics").fetchone()[0]
    assert metric_count == 1

    conn.close()
