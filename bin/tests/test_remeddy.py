import base64
import os
import runpy
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "remeddy"


def decode_command(command):
    encoded = command[command.index("-EncodedCommand") + 1]
    return base64.b64decode(encoded).decode("utf-16le")


class RemeddyTest(unittest.TestCase):
    def test_auto_detects_windows_and_launches_current_directory(self):
        commands = []

        def fake_run(command, **kwargs):
            commands.append((command, kwargs))
            if command[-2:] == ["/usr/bin/uname", "-s"]:
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="'uname' is not recognized")
            if command[-2:] == ["-Command", "Write-Output windows"]:
                return subprocess.CompletedProcess(command, 0, stdout="windows\n", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch.dict(os.environ, {"PWD": tmp}, clear=False),
                patch.object(sys, "argv", [str(SCRIPT), "winbox", "--remote-target", "devbox"]),
                patch("pathlib.Path.cwd", return_value=Path(tmp)),
                patch("subprocess.run", side_effect=fake_run),
            ):
                with self.assertRaises(SystemExit) as raised:
                    runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(len(commands), 3)
        command, kwargs = commands[-1]
        self.assertEqual(command[:3], ["ssh", "winbox", "powershell.exe"])
        self.assertIn("-OutputFormat", command)
        self.assertIn("Text", command)
        self.assertEqual(kwargs, {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True})
        script = decode_command(command)
        self.assertIn("$remoteName = 'ssh-remote+devbox'", script)
        self.assertIn(f"$remotePath = '{tmp}'", script)
        self.assertLess(script.index("Code - Insiders.exe"), script.index("code-insiders.cmd"))
        self.assertIn("$taskName = 'remeddy-' + [Guid]::NewGuid().ToString('N')", script)

    def test_auto_detects_macos_and_launches_current_directory(self):
        commands = []

        def fake_run(command, **kwargs):
            commands.append((command, kwargs))
            if command[-2:] == ["/usr/bin/uname", "-s"]:
                return subprocess.CompletedProcess(command, 0, stdout="Darwin\n", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch.dict(os.environ, {"PWD": tmp}, clear=False),
                patch.object(sys, "argv", [str(SCRIPT), "macbox", "--remote-target", "devbox"]),
                patch("pathlib.Path.cwd", return_value=Path(tmp)),
                patch("subprocess.run", side_effect=fake_run),
            ):
                with self.assertRaises(SystemExit) as raised:
                    runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(len(commands), 2)
        command, kwargs = commands[-1]
        self.assertEqual(command[:4], ["ssh", "macbox", "/bin/sh", "-lc"])
        self.assertEqual(kwargs, {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True})
        script = shlex.split(command[-1])[0]
        self.assertIn(
            "for candidate in code-insiders '/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code-insiders'",
            script,
        )
        self.assertIn(
            f'nohup "$code" --new-window --remote ssh-remote+devbox {tmp} >/dev/null 2>&1 &',
            script,
        )
        self.assertNotIn("/usr/bin/open", script)

    def test_optional_app_name_changes_macos_cli(self):
        module = runpy.run_path(str(SCRIPT))
        script = module["macos_shell_script"]("devbox", "/tmp/project", None, "Visual Studio Code")

        self.assertIn("for candidate in code '/Applications/Visual Studio Code.app", script)
        self.assertIn('nohup "$code" --new-window --remote ssh-remote+devbox /tmp/project', script)

    def test_generic_macos_app_uses_open_without_remote_args(self):
        module = runpy.run_path(str(SCRIPT))
        script = module["macos_shell_script"]("devbox", "/tmp/project", None, "Spotify")

        self.assertEqual(script, "exec /usr/bin/open -a Spotify")

    def test_generic_windows_app_omits_remote_args(self):
        module = runpy.run_path(str(SCRIPT))
        script = module["powershell_script"]("devbox", "/tmp/project", None, "Spotify")

        self.assertIn("Spotify.exe", script)
        self.assertNotIn("$arguments += '--remote'", script)
        self.assertNotIn("$arguments += $remoteName", script)
        self.assertNotIn("$arguments += $remotePath", script)

    def test_platform_override_skips_detection(self):
        commands = []

        def fake_run(command, **kwargs):
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with (
            patch.object(sys, "argv", [str(SCRIPT), "macbox", "--platform", "macos"]),
            patch("subprocess.run", side_effect=fake_run),
        ):
            with self.assertRaises(SystemExit) as raised:
                runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][:4], ["ssh", "macbox", "/bin/sh", "-lc"])

    def test_decodes_clixml_errors(self):
        module = runpy.run_path(str(SCRIPT))
        clean_powershell_output = module["clean_powershell_output"]
        raw = """#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">One_x000D__x000A_</S><S S="Error">Two</S></Objs>"""

        self.assertEqual(clean_powershell_output(raw), "One\r\nTwo")

    def test_rejects_conflicting_window_flags(self):
        with patch.object(sys, "argv", [str(SCRIPT), "host", "--new-window", "--reuse-window"]):
            with self.assertRaises(SystemExit) as raised:
                runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
