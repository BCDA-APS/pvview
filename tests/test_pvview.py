"""Unit tests for pvview."""

import sys

import pytest


def test_import():
    """Test that pvview package can be imported."""
    import pvview

    assert pvview is not None


def test_version():
    """Test that pvview has a version attribute."""
    import pvview

    assert hasattr(pvview, "__version__")
    assert pvview.__version__ is not None


def test_pvview_module_attributes():
    """Test that pvview module has PVView class and main function."""
    from pvview import pvview

    assert hasattr(pvview, "PVView")
    assert hasattr(pvview, "main")


# ---------------------------------------------------------------------------
# Qt-dependent tests — skipped automatically when PyQt6 is not available
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def qt_app():
    """Provide a QApplication instance; skip if PySide6 is not available."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication(sys.argv)


def test_pvview_instantiation(qt_app):
    """Test that PVView can be created and has expected initial state."""
    from pvview.pvview import PVView

    view = PVView()
    assert view is not None
    assert view.db == {}
    assert view.windowTitle() == "EPICS PV View"


def test_pvview_grid_has_two_header_widgets(qt_app):
    """Test that PVView.__init__ adds the two header labels to the grid."""
    from pvview.pvview import PVView

    view = PVView()
    assert view.grid.count() == 2


def test_format_widget_default_shadow_is_sunken(qt_app):
    """Test that formatWidget uses Sunken shadow by default."""
    from PySide6.QtWidgets import QFrame
    from PySide6.QtWidgets import QLabel

    from pvview.pvview import PVView

    view = PVView()
    label = QLabel("test")
    view.formatWidget(label)
    assert label.frameShadow() == QFrame.Shadow.Sunken


def test_format_widget_raised_shadow(qt_app):
    """Test that formatWidget applies Raised shadow when requested."""
    from PySide6.QtWidgets import QFrame
    from PySide6.QtWidgets import QLabel

    from pvview.pvview import PVView

    view = PVView()
    label = QLabel("test")
    view.formatWidget(label, shadow=QFrame.Shadow.Raised)
    assert label.frameShadow() == QFrame.Shadow.Raised


def test_format_widget_panel_shape(qt_app):
    """Test that formatWidget sets Panel frame shape."""
    from PySide6.QtWidgets import QFrame
    from PySide6.QtWidgets import QLabel

    from pvview.pvview import PVView

    view = PVView()
    label = QLabel("test")
    view.formatWidget(label)
    assert label.frameShape() == QFrame.Shape.Panel


def test_format_widget_bold(qt_app):
    """Test that formatWidget applies bold font when requested."""
    from PySide6.QtWidgets import QLabel

    from pvview.pvview import PVView

    view = PVView()
    label = QLabel("test")
    view.formatWidget(label, bold=True)
    assert label.font().bold()


def test_format_widget_not_bold(qt_app):
    """Test that formatWidget leaves font non-bold by default."""
    from PySide6.QtWidgets import QLabel

    from pvview.pvview import PVView

    view = PVView()
    label = QLabel("test")
    view.formatWidget(label, bold=False)
    assert not label.font().bold()


def test_format_widget_line_width(qt_app):
    """Test that formatWidget sets line width to 2."""
    from PySide6.QtWidgets import QLabel

    from pvview.pvview import PVView

    view = PVView()
    label = QLabel("test")
    view.formatWidget(label)
    assert label.lineWidth() == 2


def test_pvview_add_deduplication(qt_app):
    """Test that add() skips a PV that is already tracked."""
    from pvview.pvview import PVView

    view = PVView()
    sentinel = object()
    view.db["test:pv"] = sentinel
    view.add("test:pv")  # should return early without modifying db
    assert view.db["test:pv"] is sentinel
    assert len(view.db) == 1


def test_pydmlabel_display_format_is_string(qt_app):
    """Test that labels added by add() use DisplayFormat.String for waveform decoding."""
    from pydm.widgets.display_format import DisplayFormat

    from pvview.pvview import PVView

    view = PVView()
    view.add("fake:pv")
    widget = view.db["fake:pv"]
    assert widget.displayFormat == DisplayFormat.String


def test_value_changed_sets_timestamp_tooltip(qt_app):
    """Test that value_changed sets the tooltip to an ISO-format timestamp."""
    import re

    from pvview.pvview import PVValueLabel

    widget = PVValueLabel()
    widget.value_changed(42)
    tip = widget.toolTip()
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", tip), f"unexpected tooltip: {tip!r}"


def test_main_raises_without_pv_args(qt_app, monkeypatch):
    """Test that main() raises RuntimeError when no PV names are provided."""
    from pvview.pvview import main

    monkeypatch.setattr(sys, "argv", ["pvview"])
    with pytest.raises(RuntimeError, match="Need one or more EPICS PVs"):
        main()
