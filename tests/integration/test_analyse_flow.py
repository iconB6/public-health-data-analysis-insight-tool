"""
Integration test for AnalyseService:
Ensure filter → summary → trend → visualization works together
using real repository and services, keeping only latest previews.
"""

# ========== TEST DATA ==========

RECORDS = [
    {"RECORD_ID": 1, "COUNTRY": "UK", "DATE": "2020-01-01", "VALUE": 10},
    {"RECORD_ID": 2, "COUNTRY": "UK", "DATE": "2021-01-01", "VALUE": 20},
    {"RECORD_ID": 3, "COUNTRY": "US", "DATE": "2021-01-01", "VALUE": 30},
]

RECORD_TABLE = "records"

RECORD_SCHEMA = {
    "RECORD_ID": "INTEGER",
    "COUNTRY": "TEXT",
    "DATE": "TEXT",
    "VALUE": "REAL",
}


# ========= EXPECTED RESULTS ==========

EXPECTED_SUMMARY_COUNT = 2

# ========= FIXTURES ==========

import pytest
from pathlib import Path

from src.application.analyse_service import AnalyseService
from src.service.filter_service import FilterService
from src.service.summary_service import SummaryService
from src.service.trend_service import TrendService
from src.infrastructure.sqlite_repository import SQLiteRepository


class SpyVisualizer:
    def __init__(self):
        self.printed = False
        self.plotted = False

    def print_table(self, summary):
        self.printed = True
        self.summary = summary

    def plot_trend(self, trend_data):
        self.plotted = True
        return object()

    def show(self, figure):
        self.figure = figure

    def export_table(self, summary, path):
        pass

    def export_figure(self, figure, path):
        pass


@pytest.fixture
def analyse_service(tmp_path: Path):
    db_path = tmp_path / "test.db"
    repo = SQLiteRepository(db_path)
    repo.connect()

    repo.ensure_table(
        table=RECORD_TABLE,
        schema=RECORD_SCHEMA,
    )

    repo.insert_rows(
    table="records",
    rows=RECORDS,
    columns=["COUNTRY", "DATE", "VALUE"],
)

    visualizer = SpyVisualizer()

    service = AnalyseService(
        filter_service=FilterService(repo),
        summary_service=SummaryService(repo),
        trend_service=TrendService(repo),
        visualizer=visualizer,
    )

    return service, visualizer


# ========== Normal cases ==========

def test_full_filter_summary_trend_flow(analyse_service):
    service, visualizer = analyse_service

    rows = service.run_filter(
        conditions={"COUNTRY": {"eq": "UK"}}
    )

    assert len(rows) == 2
    assert visualizer.printed is True
    assert service._summary_preview["meta"] == {"total_records": EXPECTED_SUMMARY_COUNT}

    trend = service.run_trend(
        date_field="DATE",
        metric_field="VALUE",
    )

    assert visualizer.plotted is True
    assert "date" in trend
    assert "value" in trend


# ========== Edge cases ==========

def test_filter_returns_empty_still_generates_summary(analyse_service):
    service, visualizer = analyse_service

    rows = service.run_filter(
        conditions={"COUNTRY": {"eq": "FR"}}
    )

    assert rows == []
    assert service._summary_preview["meta"] == {"total_records": 0}


# ========== Invalid cases ==========


# ========== Exception cases ==========

def test_repository_error_bubbles_up(monkeypatch, analyse_service):
    service, _ = analyse_service

    def broken_query(*args, **kwargs):
        raise RuntimeError("DB broken")

    monkeypatch.setattr(
        service.filter_service._repo,
        "query",
        broken_query
    )

    with pytest.raises(RuntimeError):
        service.run_filter()
