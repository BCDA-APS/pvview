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

**`main()`** — creates a `QApplication`, instantiates `PVView`, reads PV names from `sys.argv[1:]`, calls `add()` for each, and enters the Qt event loop. It raises `RuntimeError` (not `sys.exit`) when called with no PV arguments.

**`src/pvview/__init__.py`** — only exposes `__version__` via `importlib.metadata`; all package metadata lives in `pyproject.toml`.

## Key constraints

- **Qt version**: PySide6 only (PyDM does not support PyQt6). Enum access uses nested form: `QFrame.Shape.Panel`, `QFrame.Shadow.Raised/Sunken`. Event loop uses `app.exec()` (no trailing underscore).
- **EPICS dependency**: `PyDMLabel` requires PyDM and a Channel Access environment at runtime. Tests that instantiate `PVView` skip automatically when PySide6 is absent; tests that call `add()` with a real PV name would need a live IOC.
- **Versioning**: managed by `setuptools-scm` from git tags. Do not manually edit `__version__`.
- **Import style**: `isort --sl` (force single-line) is enforced by pre-commit. Each symbol gets its own `from X import Y` line.
