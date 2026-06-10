import base64
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "wined"


def decode_command(command):
    encoded = command[command.index("-EncodedCommand") + 1]
    return base64.b64decode(encoded).decode("utf-16le")


class WinedTest(unittest.TestCase):
    def test_launches_windows_code_insiders_for_current_directory(self):
        commands = []

        def fake_run(command, **kwargs):
            commands.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0)

        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch.dict(os.environ, {"PWD": tmp}, clear=False),
                patch.object(sys, "argv", [str(SCRIPT), "--windows-host", "winbox", "--remote-target", "devbox"]),
                patch("pathlib.Path.cwd", return_value=Path(tmp)),
                patch("subprocess.run", side_effect=fake_run),
            ):
                with self.assertRaises(SystemExit) as raised:
                    runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(raised.exception.code, 0)
        command, kwargs = commands[0]
        self.assertEqual(command[:3], ["ssh", "winbox", "powershell.exe"])
        self.assertIn("-OutputFormat", command)
        self.assertIn("Text", command)
        self.assertEqual(kwargs, {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True})
        script = decode_command(command)
        self.assertIn("$ProgressPreference = 'SilentlyContinue'", script)
        self.assertIn("$remoteName = 'ssh-remote+devbox'", script)
        self.assertIn(f"$remotePath = '{tmp}'", script)
        self.assertLess(script.index("Code - Insiders.exe"), script.index("code-insiders.cmd"))
        self.assertIn("$arguments += '--remote'", script)
        self.assertIn("New-ScheduledTaskAction -Execute $code -Argument $argumentString", script)
        self.assertIn("New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited", script)
        self.assertIn("Start-ScheduledTask -TaskName $taskName", script)
        self.assertIn("Unregister-ScheduledTask -TaskName $taskName", script)

    def test_decodes_clixml_errors(self):
        module = runpy.run_path(str(SCRIPT))
        clean_powershell_output = module["clean_powershell_output"]
        raw = """#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">One_x000D__x000A_</S><S S="Error">Two</S></Objs>"""

        self.assertEqual(clean_powershell_output(raw), "One\r\nTwo")

    def test_rejects_conflicting_window_flags(self):
        with patch.object(sys, "argv", [str(SCRIPT), "--new-window", "--reuse-window"]):
            with self.assertRaises(SystemExit) as raised:
                runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
