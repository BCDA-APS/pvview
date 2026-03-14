# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install for development
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run all tests
pytest

# Run a single test
pytest tests/test_pvview.py::test_pvview_instantiation

# Run the app (requires a running EPICS IOC with accessible PVs)
pvview xxx:m1.RBV xxx:m1.VAL

# Sort imports (enforced by pre-commit)
isort --sl src/ tests/
```

## Architecture

`pvview` is a minimal single-module GUI application. The entire application logic lives in `src/pvview/pvview.py`.

**`PVView(QWidget)`** — the only class. It builds a two-column `QGridLayout` (PV Name | PV Value). Row 0 is a fixed header. Each subsequent row is added by `add(pvname)`, which creates a plain `QLabel` for the name and a `PyDMLabel` for the live value. `PyDMLabel` handles all EPICS connectivity via a `ca://` channel URI — there is no manual EPICS code.

**`main()`** — creates a `QApplication`, uses `argparse` to parse one or more positional PV name arguments, instantiates `PVView`, calls `add()` for each PV, and enters the Qt event loop. When no PV names are given, argparse prints an error and calls `sys.exit(2)`. Before `sys.exit()`, `PyEPICSPlugin.thread_pool` is explicitly shut down to prevent a QThread teardown warning from PySide6.

**`src/pvview/__init__.py`** — only exposes `__version__` via `importlib.metadata`; all package metadata lives in `pyproject.toml`.

## Key constraints

- **Qt version**: PySide6 only (PyDM does not support PyQt6). Enum access uses nested form: `QFrame.Shape.Panel`, `QFrame.Shadow.Raised/Sunken`. Event loop uses `app.exec()` (no trailing underscore).
- **EPICS dependency**: `PyDMLabel` requires PyDM and a Channel Access environment at runtime. Tests that instantiate `PVView` skip automatically when PySide6 is absent; tests that call `add()` with a real PV name would need a live IOC.
- **Test teardown**: The `qt_app` fixture is session-scoped and explicitly shuts down `PyEPICSPlugin.thread_pool` and `RulesEngine` before exiting, to prevent a PySide6 QThread teardown crash.
- **Versioning**: managed by `setuptools-scm` from git tags. Do not manually edit `__version__`.
- **Import style**: `isort --sl` (force single-line) is enforced by pre-commit. Each symbol gets its own `from X import Y` line.
