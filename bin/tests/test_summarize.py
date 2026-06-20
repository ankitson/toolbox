import io
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "summarize"


class FakeProcess:
    def __init__(self, chunks, return_code=0):
        self.stdout = iter(chunks)
        self.return_code = return_code

    def wait(self):
        return self.return_code


class SummarizeTest(unittest.TestCase):
    def test_labels_extract_output_as_transcript(self):
        module = runpy.run_path(str(SCRIPT))

        self.assertEqual(module["output_kind"](["https://example.com"]), "summary")
        self.assertEqual(module["output_kind"](["--extract", "https://example.com"]), "transcript")

    def test_input_label_skips_option_values(self):
        module = runpy.run_path(str(SCRIPT))

        self.assertEqual(
            module["input_label"](["--length", "long", "--plain", "https://example.com/article"]),
            "https://example.com/article",
        )
        self.assertEqual(module["input_label"](["--model=google/gemini-3-flash", "-"]), "stdin")

    def test_run_and_save_streams_stdout_and_writes_markdown_copy(self):
        module = runpy.run_path(str(SCRIPT))
        globals_dict = module["run_and_save"].__globals__
        process = FakeProcess(["hello\n", "world\n"])

        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp)
            with (
                patch.dict(globals_dict, {"SAVE_DIR": save_dir}),
                patch.object(globals_dict["subprocess"], "Popen", return_value=process) as popen,
                patch.object(sys, "stdout", io.StringIO()) as stdout,
                patch.object(sys, "stderr", io.StringIO()) as stderr,
            ):
                return_code = module["run_and_save"](["https://youtu.be/watch?v=abc123", "--plain"])

            self.assertEqual(return_code, 0)
            self.assertEqual(stdout.getvalue(), "hello\nworld\n")
            saved = list(save_dir.glob("*-summary-youtu.be-abc123.md"))
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0].read_text(), "hello\nworld\n")
            self.assertIn(f"Saved summarize output to {saved[0]}", stderr.getvalue())
            popen.assert_called_once_with(
                ["npx", "-y", module["PACKAGE"], "https://youtu.be/watch?v=abc123", "--plain"],
                stdout=subprocess.PIPE,
                text=True,
            )

    def test_run_and_save_removes_temp_file_on_failure(self):
        module = runpy.run_path(str(SCRIPT))
        globals_dict = module["run_and_save"].__globals__
        process = FakeProcess(["partial\n"], return_code=2)

        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp)
            with (
                patch.dict(globals_dict, {"SAVE_DIR": save_dir}),
                patch.object(globals_dict["subprocess"], "Popen", return_value=process),
                patch.object(sys, "stdout", io.StringIO()),
                patch.object(sys, "stderr", io.StringIO()),
            ):
                return_code = module["run_and_save"](["https://example.com"])

            self.assertEqual(return_code, 2)
            self.assertEqual(list(save_dir.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
