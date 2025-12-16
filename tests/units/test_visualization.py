import pytest
import datetime
from src.application.visualization import Visualizer

'''
Visualizer should:
- display summary data in tabular form
- generate trend preview figures without showing/exporting automatically
- export summary and figures on demand
- never mutate input data
'''

# ========== TEST DATA ==========

SUMMARY_DATA = {
    "total_count": 3,
    "category.country": {"US": 2, "UK": 1},
    "numeric.score": {"mean": 80, "min": 60, "max": 90},
}

TREND_DATA = {
    "date": [
        datetime.date(2024, 1, 1),
        datetime.date(2024, 2, 1),
    ],
    "value": [10, 20],
    "metric_field": "COUNT",
}

# ========= EXPECTED RESULTS ==========

EXPECTED_TABLE_KEYS = {"Metric", "Value"}

# ========= FIXTURES ==========

@pytest.fixture
def visualizer():
    return Visualizer()

# ========== Normal cases ==========

def test_print_table_does_not_raise(visualizer):
    visualizer.print_table(SUMMARY_DATA)


def test_plot_trend_returns_figure(visualizer):
    fig = visualizer.plot_trend(TREND_DATA)
    assert fig is not None


def test_show_does_not_raise(visualizer):
    fig = visualizer.plot_trend(TREND_DATA)
    visualizer.show(fig)

# ========== Edge cases ==========

def test_export_table_creates_file(tmp_path, visualizer):
    path = tmp_path / "summary.csv"
    visualizer.export_table(SUMMARY_DATA, str(path))
    assert path.exists()


def test_export_figure_creates_file(tmp_path, visualizer):
    fig = visualizer.plot_trend(TREND_DATA)
    path = tmp_path / "trend.png"
    visualizer.export_figure(fig, str(path))
    assert path.exists()

def test_export_table_creates_parent_dirs(tmp_path, visualizer):
    path = tmp_path / "not_exist_dir" / "summary.csv"

    visualizer.export_table(SUMMARY_DATA, str(path))

    assert path.exists()
    assert path.is_file()

def test_export_figure_creates_parent_dirs(tmp_path, visualizer):
    fig = visualizer.plot_trend(TREND_DATA)
    path = tmp_path / "not_exist_dir" / "trend.png"

    visualizer.export_figure(fig, str(path))

    assert path.exists()
    assert path.is_file()

# ========== Invalid cases ==========

def test_print_table_invalid_type(visualizer):
    with pytest.raises(AttributeError):
        visualizer.print_table("not a dict")


def test_plot_trend_missing_keys(visualizer):
    with pytest.raises(KeyError):
        visualizer.plot_trend({"date": [], "value_missing": []})

# ========== Exception cases ==========
