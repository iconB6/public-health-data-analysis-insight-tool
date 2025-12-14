import pytest
from src.application.analyse_service import AnalyseService


'''
AnalyseService tests verify application-level orchestration.

The service must:
- coordinate filter, summary, and trend services
- always generate summary preview after filtering
- generate trend preview before export
- cache only the latest preview item
- delegate visualization and export
- raise errors when exporting without preview
'''

# ========== TEST DATA ==========

FILTERED_ROWS = [
    {"DATE": "2024-01-01", "VALUE": 10},
    {"DATE": "2024-01-02", "VALUE": 20},
]

SUMMARY_RESULT = {
    "total_count": 2,
}

TREND_RESULT = {
    "date": ["2024-01-01", "2024-01-02"],
    "value": [10, 20],
}

FAKE_FIGURE = object()

# ========= EXPECTED RESULTS ==========

EXPECTED_SUMMARY = SUMMARY_RESULT
EXPECTED_TREND = TREND_RESULT

# ========= FIXTURES ==========

class FakeFilterService:
    def filter(self, **kwargs):
        return FILTERED_ROWS


class FakeSummaryService:
    def summarize(self, rows=None):
        return SUMMARY_RESULT


class FakeTrendService:
    def trend_over_time(self, **kwargs):
        return TREND_RESULT


class FakeVisualizer:
    def __init__(self):
        self.printed = False
        self.plotted = False
        self.exported = False

    def print_table(self, summary):
        self.printed = True

    def plot_trend(self, trend_data):
        self.plotted = True
        return FAKE_FIGURE

    def show(self, figure):
        pass

    def export_table(self, summary, path):
        self.exported = ("summary", path)

    def export_figure(self, figure, path):
        self.exported = ("trend", path)


@pytest.fixture
def analyse_service():

    return AnalyseService(
        filter_service=FakeFilterService(),
        summary_service=FakeSummaryService(),
        trend_service=FakeTrendService(),
        visualizer=FakeVisualizer(),
    )

# ========== Normal cases ==========

def test_filter_triggers_summary_preview(analyse_service):
    analyse_service.run_filter(country="UK")

    assert analyse_service._last_summary == EXPECTED_SUMMARY
    assert analyse_service._visualizer.printed is True


def test_trend_generates_preview_figure(analyse_service):
    analyse_service.run_trend(
        date_field="DATE",
        metric_field="VALUE",
    )

    assert analyse_service._last_trend_figure is FAKE_FIGURE
    assert analyse_service._visualizer.plotted is True


def test_export_summary(analyse_service):
    analyse_service.run_filter(country="UK")

    analyse_service.export(type="summary", path="out.csv")

    assert analyse_service._visualizer.exported == ("summary", "out.csv")


def test_export_trend(analyse_service):
    analyse_service.run_trend(
        date_field="DATE",
        metric_field="VALUE",
    )

    analyse_service.export(type="trend", path="trend.png")

    assert analyse_service._visualizer.exported == ("trend", "trend.png")

# ========== Edge cases ==========

def test_only_latest_summary_is_kept(analyse_service):
    analyse_service.run_filter(country="UK")
    first = analyse_service._last_summary

    analyse_service.run_filter(country="US")
    second = analyse_service._last_summary

    assert first is not second


def test_only_latest_trend_is_kept(analyse_service):
    analyse_service.run_trend(date_field="DATE", metric_field="VALUE")
    first = analyse_service._last_trend_figure

    analyse_service.run_trend(date_field="DATE", metric_field="VALUE")
    second = analyse_service._last_trend_figure

    assert first is not second

# ========== Invalid cases ==========

def test_export_summary_without_preview_raises(analyse_service):
    with pytest.raises(RuntimeError):
        analyse_service.export(type="summary", path="out.csv")


def test_export_trend_without_preview_raises(analyse_service):
    with pytest.raises(RuntimeError):
        analyse_service.export(type="trend", path="trend.png")


def test_export_invalid_type(analyse_service):
    with pytest.raises(ValueError):
        analyse_service.export(type="unknown", path="x")

# ========== Exception cases ==========

def test_filter_exception_propagates(monkeypatch, analyse_service):
    def broken_filter(**kwargs):
        raise RuntimeError("filter failed")

    analyse_service._filter.filter = broken_filter

    with pytest.raises(RuntimeError):
        analyse_service.run_filter(country="UK")


def test_trend_exception_propagates(monkeypatch, analyse_service):
    def broken_trend(**kwargs):
        raise RuntimeError("trend failed")

    analyse_service._trend.trend_over_time = broken_trend

    with pytest.raises(RuntimeError):
        analyse_service.run_trend(
            date_field="DATE",
            metric_field="VALUE",
        )
