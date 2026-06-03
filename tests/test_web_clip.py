#!/usr/bin/env python3
"""Black-box tests for bin/web-clip."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_CLIP = PROJECT_ROOT / "bin" / "web-clip"


class WebClipTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self.temp = Path(self._tempdir.name)

    def run_clip(self, url: str, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(WEB_CLIP), url, *args],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode:
            self.fail(
                f"web-clip failed with {result.returncode}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        return result

    def test_file_url_clip_writes_markdown_and_local_media(self) -> None:
        source = self.temp / "source"
        source.mkdir()
        (source / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
        page = source / "index.html"
        page.write_text(
            """<!doctype html>
<html>
  <head>
    <title>Fixture Article</title>
    <meta name="author" content="Tester">
  </head>
  <body>
    <nav>ignore me</nav>
    <article>
      <h1>Fixture Article</h1>
      <p>This substantial paragraph gives the extractor enough words to prefer
      article content over page chrome and unrelated links.</p>
      <figure>
        <img src="image.png" alt="Fixture image">
        <figcaption>Fixture caption</figcaption>
      </figure>
      <h2>Details</h2>
      <p>Another paragraph includes <a href="/relative">a relative link</a>,
      <strong>bold text</strong>, <em>emphasis</em>, and inline
      <code>code</code>.</p>
      <ul><li>First item</li><li>Second item</li></ul>
      <pre><code>print("hello")</code></pre>
    </article>
  </body>
</html>""",
            encoding="utf-8",
        )
        output = self.temp / "clips"

        result = self.run_clip(page.resolve().as_uri(), "-o", str(output), "--json")
        payload = json.loads(result.stdout)

        markdown_path = Path(payload["markdown_path"])
        markdown = markdown_path.read_text()
        self.assertIn("# Fixture Article", markdown)
        self.assertIn("![Fixture image](media/", markdown)
        self.assertEqual(markdown.count("Fixture caption"), 1)
        self.assertIn("**bold text**", markdown)
        self.assertIn("`code`", markdown)
        self.assertEqual(len(payload["media_files"]), 1)
        self.assertTrue(Path(payload["media_files"][0]).is_file())
        self.assertTrue((markdown_path.parent / "source.html").is_file())

    def test_browser_mode_clips_javascript_rendered_article(self) -> None:
        if not os.environ.get("WEB_CLIP_BROWSER_TEST"):
            self.skipTest("set WEB_CLIP_BROWSER_TEST=1 to exercise Playwright")
        source = self.temp / "source"
        source.mkdir()
        page = source / "index.html"
        page.write_text(
            """<!doctype html>
<html>
  <head><title>Rendered Fixture</title></head>
  <body>
    <div id="root">Loading...</div>
    <script>
      document.getElementById("root").innerHTML =
        '<article><h1>Rendered Fixture</h1><p>This article only exists after JavaScript has executed, which verifies browser mode captures rendered content.</p></article>';
    </script>
  </body>
</html>""",
            encoding="utf-8",
        )
        output = self.temp / "clips"

        result = self.run_clip(page.resolve().as_uri(), "-o", str(output), "--browser", "--json")
        payload = json.loads(result.stdout)
        markdown = Path(payload["markdown_path"]).read_text()

        self.assertIn("# Rendered Fixture", markdown)
        self.assertIn("after JavaScript has executed", markdown)


if __name__ == "__main__":
    unittest.main()
