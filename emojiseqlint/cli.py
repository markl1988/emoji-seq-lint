"""Command line entry point."""

import argparse
import sys

from .linter import scan_text


def _iter_findings(paths):
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as exc:
            print(f"{path}: could not read file ({exc})", file=sys.stderr)
            continue
        for finding in scan_text(text):
            yield path, finding


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="emoji-seq-lint",
        description="Find malformed emoji sequences in text files.",
    )
    parser.add_argument("paths", nargs="+", help="files to check")
    args = parser.parse_args(argv)

    found_any = False
    for path, finding in _iter_findings(args.paths):
        found_any = True
        print(f"{path}:{finding.line}:{finding.col}: {finding.code} {finding.message}")

    return 1 if found_any else 0


if __name__ == "__main__":
    sys.exit(main())
