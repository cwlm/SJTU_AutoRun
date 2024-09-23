from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sjtuautorun")
except PackageNotFoundError:
    __version__ = "unknown"
