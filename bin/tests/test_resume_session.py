import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "resume-session"


class ResumeSessionTest(unittest.TestCase):
    def test_sends_submit_as_a_separate_write(self):
        commands = []

        def fake_run(command, **kwargs):
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

        with (
            patch.object(sys, "argv", [str(SCRIPT), "-t", "03:55AM", "-c", "hello", "121"]),
            patch("subprocess.run", side_effect=fake_run),
            patch("time.sleep") as sleep,
        ):
            runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(
            commands,
            [
                ["wezterm", "cli", "send-text", "--pane-id", "121", "--no-paste", "hello"],
                ["wezterm", "cli", "send-text", "--pane-id", "121", "--no-paste", "\r"],
            ],
        )
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(sleep.call_args_list[-1].args, (0.1,))


if __name__ == "__main__":
    unittest.main()
