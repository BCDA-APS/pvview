# pvview
display one or more EPICS PVs in a PyDM GUI window as a table

## Install

```bash
pip install pvview
```

### Install with conda (recommended)

Use conda to create an isolated Python environment, then pip for everything else:

```bash
conda create -n pvview python=3.14
conda activate pvview
pip install pvview
```

### Install from source

```bash
git clone https://github.com/BCDA-APS/pvview.git
cd pvview
conda create -n pvview python=3.14
conda activate pvview
pip install -e .
```

## Example

```
pvview {sky,xxx}:{iso8601,:UPTIME} xxx:alldone adsky:cam1:Acquire &
```

![pvview image](screen.jpg)

The `pvview` code was migrated from the
[BcdaQWidgets](https://github.com/BCDA-APS/bcdaqwidgets) project
(PyQt4-aware widgets for Python2)
to use the [PyDM](https://github.com/slaclab/pydm) project.
