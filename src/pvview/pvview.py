#!/usr/bin/env python

"""
display one or more EPICS PVs in a PyDM GUI window as a table

EXAMPLE:

    pvview xxx:m1.DESC xxx:m1.RBV xxx:m1.VAL xxx:m1.DMOV &
"""

import argparse
import sys
from datetime import datetime

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget
from pydm.widgets.display_format import DisplayFormat
from pydm.widgets.label import PyDMLabel


class PVNameLabel(PyDMLabel):
    """PyDMLabel showing a PV's .DESC field; falls back to the PV name when DESC is empty or unavailable."""

    def __init__(self, pvname, *args, **kwargs):
        self._pvname = pvname
        desc_pvname = pvname.split(".")[0] + ".DESC"
        super().__init__(init_channel=f"ca://{desc_pvname}", *args, **kwargs)

    def value_changed(self, new_value):
        super().value_changed(new_value)
        if not self.text().strip():
            self.setText(self._pvname)

    def check_enable_state(self):
        self.setText(self._pvname)


class PVValueLabel(PyDMLabel):
    """PyDMLabel that decodes char waveforms and shows the last-update time as a tooltip."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.displayFormat = DisplayFormat.String

    def value_changed(self, new_value):
        super().value_changed(new_value)
        self.setToolTip(datetime.now().isoformat(sep=" ", timespec="seconds"))


class PVView(QWidget):
    """Display EPICS PVs in a GUI table."""

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.db = {}

        name_label = QLabel("PV Name")
        value_label = QLabel("PV Value")
        self.formatWidget(name_label, QFrame.Shadow.Raised, bold=True)
        self.formatWidget(value_label, QFrame.Shadow.Raised, bold=True)

        self.grid = QGridLayout()
        self.grid.addWidget(name_label, 0, 0)
        self.grid.addWidget(value_label, 0, 1)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)

        self.setLayout(self.grid)
        self.setWindowTitle("EPICS PV View")

    def add(self, pvname):
        """add a PV to the table"""
        if pvname in self.db:
            return
        row = len(self.db) + 1
        label = PVNameLabel(pvname)
        widget = PVValueLabel(init_channel=f"ca://{pvname}")
        widget.useAlarmState = True
        self.formatWidget(label)
        self.formatWidget(widget)
        self.db[pvname] = widget
        self.grid.addWidget(label, row, 0)
        self.grid.addWidget(widget, row, 1)

    def formatWidget(self, widget, shadow=None, bold=False):
        """apply some styles to the widget"""
        shadow = shadow or QFrame.Shadow.Sunken
        widget.setFrameShape(QFrame.Shape.Panel)
        widget.setFrameShadow(shadow)
        widget.setLineWidth(2)
        if bold:
            myFont = QFont()
            myFont.setBold(True)
            widget.setFont(myFont)


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    parser = argparse.ArgumentParser(
        prog="pvview",
        description="Display EPICS PVs in a table.",
    )
    parser.add_argument("pvnames", nargs="+", metavar="PVNAME", help="EPICS PV name(s) to display")
    args = parser.parse_args()
    probe = PVView()
    for pvname in args.pvnames:
        probe.add(pvname)
    probe.show()
    ret = app.exec()
    from pydm.data_plugins.epics_plugins.pyepics_plugin_component import PyEPICSPlugin
    if PyEPICSPlugin.thread_pool is not None:
        PyEPICSPlugin.thread_pool.shutdown(wait=True)
    sys.exit(ret)


if __name__ == "__main__":
    main()
