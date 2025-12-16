import pytest
from unittest.mock import MagicMock
from datetime import date

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
def fake_repository():
    repo = MagicMock()

    # for filter / summary
    repo.query.return_value = [
        {"DATE": date(2020, 1, 1), "VALUE": 1},
        {"DATE": date(2020, 1, 2), "VALUE": 2},
    ]

    repo.get_schema.return_value = {
        "DATE": "TEXT",
        "VALUE": "INTEGER",
    }

    # for trend
    repo.query_for_trend.return_value = [
        {"DATE": date(2020, 1, 1), "VALUE": 1},
        {"DATE": date(2020, 1, 2), "VALUE": 2},
    ]

    return repo


@pytest.fixture
def visualizer():
    v = MagicMock()
    v.plot_trend.return_value = object()
    return v


@pytest.fixture
def analyse_service(fake_repository, visualizer):
    from src.application.analyse_service import AnalyseService

    return AnalyseService(
        repository=fake_repository,
        visualizer=visualizer,
    )


# ========== Normal cases ==========

def test_filter_triggers_summary_preview(analyse_service, visualizer):
    rows = analyse_service.run_filter()

    assert len(rows) == 2
    assert analyse_service._summary_preview["meta"]["total_records"] == 2
    visualizer.print_table.assert_called_once()


# ========== State management cases ==========

def test_only_latest_summary_is_kept(analyse_service, fake_repository):
    analyse_service.run_filter()
    first = analyse_service._summary_preview

    fake_repository.query.return_value = [
        {"DATE": date(2020, 1, 1), "VALUE": 10},
    ]

    analyse_service.run_filter()
    second = analyse_service._summary_preview

    assert first is not second
    assert second["meta"]["total_records"] == 1


def test_only_latest_trend_is_kept(analyse_service, visualizer):
    visualizer.plot_trend.side_effect = [object(), object()]

    analyse_service.run_trend(
        date_field="DATE",
        metric_field="VALUE",
    )
    first = analyse_service._trend_figure_preview

    analyse_service.run_trend(
        date_field="DATE",
        metric_field="VALUE",
    )
    second = analyse_service._trend_figure_preview

    assert first is not second


# ========== Export cases ==========

def test_export_summary_uses_latest_preview(analyse_service, visualizer):
    analyse_service.run_filter()

    analyse_service.export_summary("out.csv")

    visualizer.export_table.assert_called_once_with(
        analyse_service._summary_preview,
        "out.csv",
    )


def test_export_trend_uses_latest_preview(analyse_service, visualizer):
    analyse_service.run_trend(
        date_field="DATE",
        metric_field="VALUE",
    )

    analyse_service.export_trend("out.png")

    visualizer.export_figure.assert_called_once_with(
        analyse_service._trend_figure_preview,
        "out.png",
    )


# ========== Exception cases ==========

def test_export_summary_without_preview_raises(analyse_service):
    with pytest.raises(RuntimeError):
        analyse_service.export_summary("out.csv")


def test_export_trend_without_preview_raises(analyse_service):
    with pytest.raises(RuntimeError):
        analyse_service.export_trend("out.png")
