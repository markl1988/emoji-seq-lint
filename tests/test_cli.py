"""End-to-end tests that go through main() and real files on disk."""

import contextlib
import io
import json
import os
import tempfile
import unittest

from emojiseqlint.cli import main

SUN = "☀"
GRINNING_FACE = "\U0001F600"
ZWJ = "‍"


class CliTests(unittest.TestCase):
    def _write(self, text):
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", encoding="utf-8", delete=False
        )
        try:
            handle.write(text)
        finally:
            handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_text_output_and_exit_status_on_a_flagged_file(self):
        prefix = "look at the sun: "
        path = self._write(prefix + SUN + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main([path])
        self.assertEqual(status, 1)
        self.assertIn(f"{path}:1:{len(prefix) + 1}: VS001", out.getvalue())

    def test_clean_file_exits_zero_with_no_output(self):
        path = self._write("nothing to see here\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main([path])
        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue(), "")

    def test_json_output_is_well_formed(self):
        path = self._write("truncated bug: " + GRINNING_FACE + ZWJ + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main(["--format", "json", path])
        self.assertEqual(status, 1)
        payload = json.loads(out.getvalue())
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["path"], path)
        self.assertEqual(payload[0]["code"], "ZWJ001")

    def test_ignore_flag_suppresses_matching_codes(self):
        prefix = "look at the sun: "
        path = self._write(prefix + SUN + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main(["--ignore", "VS001", path])
        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue(), "")

    def test_ignore_flag_accepts_comma_separated_codes(self):
        path = self._write("truncated bug: " + GRINNING_FACE + ZWJ + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main(["--ignore", "ZWJ001,ZWJ002", path])
        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue(), "")

    def test_ignore_flag_leaves_other_codes_reported(self):
        prefix = "look at the sun: "
        path = self._write(prefix + SUN + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main(["--ignore", "TONE001", path])
        self.assertEqual(status, 1)
        self.assertIn("VS001", out.getvalue())

    def test_missing_file_is_reported_but_does_not_crash(self):
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = main(["/no/such/path/here.md"])
        self.assertEqual(status, 0)
        self.assertIn("could not read file", err.getvalue())


if __name__ == "__main__":
    unittest.main()
