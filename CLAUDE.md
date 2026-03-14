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

**Lazy-load pattern** — Qt and PyDM are heavy; importing them makes `pvview --help` noticeably slow. The module therefore defers all Qt/PyDM imports until they are actually needed, via two mechanisms:

- **`_init_classes()`** — imports Qt/PyDM, defines `PVNameLabel`, `PVValueLabel`, and `PVView` as local classes, then injects them into the module's `globals()` dict. Idempotent: a guard on `"PVView" in globals()` makes subsequent calls a no-op. Returns `(PVNameLabel, PVValueLabel, PVView)` for convenient unpacking.
- **`__getattr__(name)`** (PEP 562 module-level) — called by Python whenever an attribute is not found in the module dict. For names in `_LAZY_ATTRS`, it calls `_init_classes()` then returns the now-populated global. This makes `from pvview.pvview import PVView` work transparently without eagerly importing Qt.

**`PVView(QWidget)`** — builds a two-column `QGridLayout` (PV Name | PV Value). Row 0 is a fixed header. Each subsequent row is added by `add(pvname)`, which creates a `PVNameLabel` (or plain `QLabel`) for the name and a `PVValueLabel` for the live value. `PyDMLabel` handles all EPICS connectivity via a `ca://` channel URI — there is no manual EPICS code.

**`PVNameLabel(PyDMLabel)`** — connects to the `.DESC` field of the base record; falls back to the raw PV name when DESC is empty or the channel is disconnected.

**`PVValueLabel(PyDMLabel)`** — forces `DisplayFormat.String` so char waveforms render as text; updates the tooltip with an ISO timestamp on each value change.

**`_launch(args)`** — called by `main()` after argparse finishes. Calls `_init_classes()`, constructs the `QApplication` and `PVView`, enters the Qt event loop, and shuts down `PyEPICSPlugin.thread_pool` and `RulesEngine` before exiting.

**`main()`** — pure argparse; exits via `sys.exit(2)` on missing PV names before any Qt import occurs, keeping `--help` fast.

**`src/pvview/__init__.py`** — only exposes `__version__` via `importlib.metadata`; all package metadata lives in `pyproject.toml`.

## Key constraints

- **Qt version**: PySide6 only (PyDM does not support PyQt6). Enum access uses nested form: `QFrame.Shape.Panel`, `QFrame.Shadow.Raised/Sunken`. Event loop uses `app.exec()` (no trailing underscore).
- **EPICS dependency**: `PyDMLabel` requires PyDM and a Channel Access environment at runtime. Tests that instantiate `PVView` skip automatically when PySide6 is absent; tests that call `add()` with a real PV name would need a live IOC.
- **Lazy loading**: `PVNameLabel`, `PVValueLabel`, and `PVView` are NOT defined at module import time. They are injected into module globals by `_init_classes()` on first use. Do not add Qt/PyDM imports at the module's top level — this would break the `--help` speedup.
- **Test teardown**: The `qt_app` fixture is session-scoped and explicitly shuts down `PyEPICSPlugin.thread_pool` and `RulesEngine` before exiting, to prevent a PySide6 QThread teardown crash.
- **Versioning**: managed by `setuptools-scm` from git tags. Do not manually edit `__version__`.
- **Import style**: `isort --sl` (force single-line) is enforced by pre-commit. Each symbol gets its own `from X import Y` line.
