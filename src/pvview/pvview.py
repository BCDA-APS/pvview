#!/usr/bin/env python

"""
Display one or more EPICS PVs in a PyDM GUI window as a table.

EXAMPLE:

    pvview xxx:m1.DESC xxx:m1.RBV xxx:m1.VAL xxx:m1.DMOV &
"""

import argparse
import os
import sys

os.environ.setdefault("QT_API", "pyqt5")
_LAZY_ATTRS = frozenset({"PVNameLabel", "PVValueLabel", "PVView"})


def _init_classes():
    """Lazily import Qt/PyDM and inject GUI classes into module globals; idempotent."""
    _globals = globals()
    if "PVView" in _globals:
        return _globals["PVNameLabel"], _globals["PVValueLabel"], _globals["PVView"]

    from datetime import datetime

    from pydm.widgets.display_format import DisplayFormat
    from pydm.widgets.label import PyDMLabel
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import QFrame
    from PyQt5.QtWidgets import QGridLayout
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtWidgets import QWidget

    class PVNameLabel(PyDMLabel):
        """PyDMLabel showing a PV's .DESC field; falls back to the PV name when DESC is empty or unavailable."""

        def __init__(self, pvname, *args, **kwargs):
            """Connect to pvname's .DESC field and store pvname as the tooltip."""
            self._pvname = pvname
            desc_pvname = pvname.split(".")[0] + ".DESC"
            super().__init__(*args, init_channel=f"ca://{desc_pvname}", **kwargs)
            self.setToolTip(pvname)

        def value_changed(self, new_value):
            """Show the PV name when the DESC value is empty or whitespace."""
            super().value_changed(new_value)
            if not self.text().strip():
                self.setText(self._pvname)

        def check_enable_state(self):
            """Display the PV name while the channel is disconnected."""
            self.setText(self._pvname)

    class PVValueLabel(PyDMLabel):
        """PyDMLabel that decodes char waveforms and shows the last-update time as a tooltip."""

        def __init__(self, *args, **kwargs):
            """Set display format to String so char waveforms render as text."""
            super().__init__(*args, **kwargs)
            self.displayFormat = DisplayFormat.String

        def value_changed(self, new_value):
            """Update the tooltip with the current timestamp on each new value."""
            super().value_changed(new_value)
            now = datetime.now().astimezone()
            self.setToolTip(now.isoformat(sep=" ", timespec="seconds"))

    class PVView(QWidget):
        """Display EPICS PVs in a GUI table."""

        def __init__(self, name_header="Name / Description", parent=None):
            """Build the two-column grid layout with a header row."""
            super().__init__(parent)
            self.db = {}

            name_label = QLabel(name_header)
            value_label = QLabel("PV Value")
            self.formatWidget(name_label, QFrame.Raised, bold=True)
            self.formatWidget(value_label, QFrame.Raised, bold=True)

            self.grid = QGridLayout()
            self.grid.addWidget(name_label, 0, 0)
            self.grid.addWidget(value_label, 0, 1)
            self.grid.setColumnStretch(0, 0)
            self.grid.setColumnStretch(1, 1)

            self.setLayout(self.grid)
            self.setWindowTitle("EPICS PV View")

        def add(self, pvname, show_desc=True):
            """Add a PV row to the table; no-op if pvname is already present."""
            if pvname in self.db:
                return
            row = len(self.db) + 1
            label = PVNameLabel(pvname) if show_desc else QLabel(pvname)
            widget = PVValueLabel(init_channel=f"ca://{pvname}")
            widget.useAlarmState = True
            self.formatWidget(label)
            self.formatWidget(widget)
            self.db[pvname] = widget
            self.grid.addWidget(label, row, 0)
            self.grid.addWidget(widget, row, 1)

        def formatWidget(self, widget, shadow=None, bold=False):
            """Apply panel frame, shadow, and optional bold font to a widget."""
            shadow = shadow or QFrame.Sunken
            widget.setFrameShape(QFrame.Panel)
            widget.setFrameShadow(shadow)
            widget.setLineWidth(2)
            if bold:
                my_font = QFont()
                my_font.setBold(True)
                widget.setFont(my_font)

    _globals["PVNameLabel"] = PVNameLabel
    _globals["PVValueLabel"] = PVValueLabel
    _globals["PVView"] = PVView
    return PVNameLabel, PVValueLabel, PVView


def __getattr__(name):
    """Resolve Qt-dependent classes on first access without importing Qt at module load time (PEP 562)."""
    if name in _LAZY_ATTRS:
        _init_classes()
        try:
            return globals()[name]
        except KeyError:
            pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _launch(args):
    """Import Qt/PyDM and run the GUI (called only after argparse completes)."""
    import gc

    _, _, PVView = _init_classes()

    from pydm.data_plugins.epics_plugins.pyepics_plugin_component import PyEPICSPlugin
    from pydm.widgets.rules import RulesDispatcher
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    name_header = "Name / Description" if args.desc else "PV Name"
    probe = PVView(name_header=name_header)
    for pvname in args.pvnames:
        probe.add(pvname, show_desc=args.desc)
    probe.show()
    ret = app.exec_()
    gc.collect()
    if PyEPICSPlugin.thread_pool is not None:
        PyEPICSPlugin.thread_pool.shutdown(wait=True)
    rules_engine = RulesDispatcher().rules_engine
    if rules_engine.isRunning():
        rules_engine.requestInterruption()
        rules_engine.quit()
        rules_engine.wait(1000)
    sys.exit(ret)


def main():
    """Parse CLI arguments, launch the PVView window, and clean up on exit."""
    from importlib.metadata import version

    parser = argparse.ArgumentParser(
        prog="pvview",
        description="Display EPICS PVs in a table.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('pvview')}"
    )
    parser.add_argument(
        "pvnames", nargs="+", metavar="PVNAME", help="EPICS PV name(s) to display"
    )
    parser.add_argument(
        "--desc",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="show PV description in name column (default: enabled)",
    )
    args = parser.parse_args()
    _launch(args)


if __name__ == "__main__":
    main()
