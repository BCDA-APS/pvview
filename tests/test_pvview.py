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
    """Test that pvview module has expected classes and main function."""
    from pvview import pvview

    assert hasattr(pvview, "PVNameLabel")
    assert hasattr(pvview, "PVValueLabel")
    assert hasattr(pvview, "PVView")
    assert hasattr(pvview, "main")


# ---------------------------------------------------------------------------
# Qt-dependent tests — skipped automatically when PySide6 is not available
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def qt_app():
    """Provide a QApplication instance; skip if PySide6 is not available."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    yield app
    import gc

    from pydm.data_plugins.epics_plugins.pyepics_plugin_component import PyEPICSPlugin
    from pydm.widgets.rules import RulesDispatcher

    gc.collect()
    if PyEPICSPlugin.thread_pool is not None:
        PyEPICSPlugin.thread_pool.shutdown(wait=True)
    rules_engine = RulesDispatcher().rules_engine
    if rules_engine.isRunning():
        rules_engine.requestInterruption()
        rules_engine.quit()
        rules_engine.wait(1000)


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


def test_pvnamelabel_tooltip_is_pvname(qt_app):
    """Test that PVNameLabel always shows the PV name as a tooltip."""
    from pvview.pvview import PVNameLabel

    label = PVNameLabel("fake:pv")
    assert label.toolTip() == "fake:pv"


def test_pvnamelabel_shows_pvname_when_disconnected(qt_app):
    """Test that PVNameLabel shows the PV name (not the channel URI) when disconnected."""
    from pvview.pvview import PVNameLabel

    label = PVNameLabel("fake:pv")
    assert label.text() == "fake:pv"


def test_pvnamelabel_desc_channel(qt_app):
    """Test that PVNameLabel connects to the .DESC field of the base record."""
    from pvview.pvview import PVNameLabel

    label = PVNameLabel("fake:pv.RBV")
    assert label.channel == "ca://fake:pv.DESC"


def test_pvnamelabel_value_changed_shows_desc(qt_app):
    """Test that PVNameLabel shows a non-empty DESC value."""
    from pvview.pvview import PVNameLabel

    label = PVNameLabel("fake:pv")
    label.value_changed("Motor 1 readback")
    assert label.text() == "Motor 1 readback"


def test_pvnamelabel_value_changed_falls_back_to_pvname(qt_app):
    """Test that PVNameLabel falls back to PV name when DESC is empty."""
    from pvview.pvview import PVNameLabel

    label = PVNameLabel("fake:pv")
    label.value_changed("")
    assert label.text() == "fake:pv"


def test_pvview_add_show_desc_true_uses_pvnamelabel(qt_app):
    """Test that add() uses PVNameLabel when show_desc=True (default)."""
    from pvview.pvview import PVNameLabel
    from pvview.pvview import PVView

    view = PVView()
    view.add("fake:pv")
    label = view.grid.itemAtPosition(1, 0).widget()
    assert isinstance(label, PVNameLabel)


def test_pvview_add_show_desc_false_uses_qlabel(qt_app):
    """Test that add() uses a plain QLabel when show_desc=False."""
    from PySide6.QtWidgets import QLabel

    from pvview.pvview import PVNameLabel
    from pvview.pvview import PVView

    view = PVView()
    view.add("fake:pv", show_desc=False)
    label = view.grid.itemAtPosition(1, 0).widget()
    assert isinstance(label, QLabel)
    assert not isinstance(label, PVNameLabel)


def test_pydmlabel_display_format_is_string(qt_app):
    """Test that value labels added by add() use DisplayFormat.String for waveform decoding."""
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


def test_main_no_pvargs_exits(qt_app, monkeypatch):
    """Test that main() exits with an error when no PV names are provided."""
    from pvview.pvview import main

    monkeypatch.setattr(sys, "argv", ["pvview"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code != 0
