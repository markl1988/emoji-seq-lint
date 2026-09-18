"""Command line entry point."""

import argparse
import json
import sys

from .linter import scan_text


def _iter_findings(paths, ignore=frozenset()):
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as exc:
            print(f"{path}: could not read file ({exc})", file=sys.stderr)
            continue
        for finding in scan_text(text):
            if finding.code in ignore:
                continue
            yield path, finding


def _print_text(results):
    for path, finding in results:
        print(f"{path}:{finding.line}:{finding.col}: {finding.code} {finding.message}")


def _print_json(results):
    payload = [
        {
            "path": path,
            "line": finding.line,
            "col": finding.col,
            "code": finding.code,
            "message": finding.message,
        }
        for path, finding in results
    ]
    print(json.dumps(payload, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="emoji-seq-lint",
        description="Find malformed emoji sequences in text files.",
    )
    parser.add_argument("paths", nargs="+", help="files to check")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format, for piping into other tools (default: text)",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="CODE",
        help="rule code to suppress, e.g. VS001 (repeatable, or comma-separated)",
    )
    args = parser.parse_args(argv)
    ignore = {code.strip() for group in args.ignore for code in group.split(",") if code.strip()}

    results = list(_iter_findings(args.paths, ignore))
    if args.format == "json":
        _print_json(results)
    else:
        _print_text(results)

    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
