"""emojiseqlint: a linter for malformed emoji sequences."""

from .linter import Finding, scan_line, scan_text

__version__ = "0.1.0"

__all__ = ["Finding", "scan_line", "scan_text", "__version__"]
