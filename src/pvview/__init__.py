from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pvview")
except PackageNotFoundError:
    __version__ = "unknown"
