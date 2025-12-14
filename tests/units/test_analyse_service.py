import pytest
from unittest.mock import MagicMock

'''
AnalyseService tests verify:
- filter triggers summary preview automatically
- trend generates and previews a figure
- only latest summary and trend previews are kept
- export uses current preview
- errors are raised when exporting without preview
'''

# ========== FIXTURES ==========

@pytest.fixture
def filter_service():
    svc = MagicMock()
    svc.filter.return_value = [{"A": 1}]
    return svc


@pytest.fixture
def summary_service():
    svc = MagicMock()
    svc.summarize.return_value = {"total_count": 1}
    return svc


@pytest.fixture
def trend_service():
    svc = MagicMock()
    svc.generate.return_value = {"date": [], "value": []}
    return svc


@pytest.fixture
def visualizer():
    v = MagicMock()
    v.plot_trend.return_value = object()
    return v


@pytest.fixture
def analyse_service(filter_service, summary_service, trend_service, visualizer):
    from src.application.analyse_service import AnalyseService

    return AnalyseService(
        filter_service=filter_service,
        summary_service=summary_service,
        trend_service=trend_service,
        visualizer=visualizer,
    )

# ========== Normal cases ==========

def test_filter_triggers_summary_preview(analyse_service, visualizer):
    rows = analyse_service.run_filter()

    assert rows == [{"A": 1}]
    visualizer.print_table.assert_called_once_with({"total_count": 1})


def test_trend_generates_preview_figure(analyse_service, visualizer):
    trend_data = analyse_service.run_trend("DATE", "COUNT")

    assert trend_data == {"date": [], "value": []}
    visualizer.plot_trend.assert_called_once()
    visualizer.show.assert_called_once()

# ========== State management cases ==========

def test_only_latest_summary_is_kept(analyse_service):
    analyse_service.run_filter()
    first = analyse_service._summary_preview

    analyse_service.summary_service.summarize.return_value = {"total_count": 2}
    analyse_service.run_filter()
    second = analyse_service._summary_preview

    assert first != second


def test_only_latest_trend_is_kept(analyse_service, visualizer):
    visualizer.plot_trend.side_effect = [object(), object()]

    analyse_service.run_trend("DATE", "COUNT")
    first = analyse_service._trend_figure_preview

    analyse_service.run_trend("DATE", "COUNT")
    second = analyse_service._trend_figure_preview

    assert first is not second


# ========== Export cases ==========

def test_export_summary_uses_latest_preview(analyse_service, visualizer):
    analyse_service.run_filter()

    analyse_service.export_summary("out.csv")

    visualizer.export_table.assert_called_once_with(
        {"total_count": 1}, "out.csv"
    )


def test_export_trend_uses_latest_preview(analyse_service, visualizer):
    analyse_service.run_trend("DATE", "COUNT")
