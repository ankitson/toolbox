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

        result = self.run_clip(
            page.resolve().as_uri(), "-o", str(output), "--rendered", "never", "--json"
        )
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

    def test_rendered_mode_clips_javascript_rendered_article(self) -> None:
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

        result = self.run_clip(
            page.resolve().as_uri(), "-o", str(output), "--rendered", "always", "--json"
        )
        payload = json.loads(result.stdout)
        markdown = Path(payload["markdown_path"]).read_text()

        self.assertIn("# Rendered Fixture", markdown)
        self.assertIn("after JavaScript has executed", markdown)

    def test_repeated_clip_gets_unique_folder_without_overwrite(self) -> None:
        source = self.temp / "source"
        source.mkdir()
        page = source / "index.html"
        page.write_text(
            "<html><head><title>Repeat Me</title></head><body><article><p>"
            "Enough words to make a tiny but valid article for the repeat test."
            "</p></article></body></html>",
            encoding="utf-8",
        )
        output = self.temp / "clips"

        first = json.loads(
            self.run_clip(
                page.resolve().as_uri(), "-o", str(output), "--rendered", "never", "--json"
            ).stdout
        )
        second = json.loads(
            self.run_clip(
                page.resolve().as_uri(), "-o", str(output), "--rendered", "never", "--json"
            ).stdout
        )

        self.assertNotEqual(first["output_dir"], second["output_dir"])
        self.assertTrue(Path(first["markdown_path"]).is_file())
        self.assertTrue(Path(second["markdown_path"]).is_file())

    def test_overwrite_replaces_existing_folder_with_media(self) -> None:
        source = self.temp / "source"
        source.mkdir()
        (source / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
        page = source / "index.html"
        page.write_text(
            "<html><head><title>Overwrite Me</title></head><body><article>"
            "<p>First article with enough words to extract and an image.</p>"
            '<img src="image.png" alt="first">'
            "</article></body></html>",
            encoding="utf-8",
        )
        output = self.temp / "clips"

        self.run_clip(
            page.resolve().as_uri(),
            "-o",
            str(output),
            "--slug",
            "overwrite",
            "--rendered",
            "never",
            "--json",
        )
        page.write_text(
            "<html><head><title>Overwrite Me</title></head><body><article>"
            "<p>Second article should replace the previous markdown.</p>"
            "</article></body></html>",
            encoding="utf-8",
        )
        result = json.loads(
            self.run_clip(
                page.resolve().as_uri(),
                "-o",
                str(output),
                "--slug",
                "overwrite",
                "--overwrite",
                "--rendered",
                "never",
                "--json",
            ).stdout
        )

        markdown = Path(result["markdown_path"]).read_text()
        self.assertIn("Second article", markdown)
        self.assertNotIn("First article", markdown)

    def test_srcset_prefers_largest_image_candidate(self) -> None:
        source = self.temp / "source"
        source.mkdir()
        (source / "tiny.jpg").write_bytes(b"\xff\xd8\xff" + b"0" * 100)
        (source / "large.jpg").write_bytes(b"\xff\xd8\xff" + b"1" * 100)
        page = source / "index.html"
        page.write_text(
            """<html><head><title>Srcset Article</title></head><body><article>
            <h1>Srcset Article</h1>
            <p>This article has enough words to make the extractor choose this
            article element and exercise responsive image source selection.</p>
            <img src="tiny.jpg" srcset="tiny.jpg 320w, large.jpg 1200w" alt="responsive">
            </article></body></html>""",
            encoding="utf-8",
        )

        result = json.loads(
            self.run_clip(
                page.resolve().as_uri(), "-o", str(self.temp / "clips"), "--rendered", "never", "--json"
            ).stdout
        )

        markdown = Path(result["markdown_path"]).read_text()
        self.assertIn("![responsive](media/large-", markdown)
        self.assertNotIn("media/tiny-", markdown)
        self.assertEqual(len(result["media_files"]), 1)

    def test_noscript_image_fallback_is_preserved(self) -> None:
        source = self.temp / "source"
        source.mkdir()
        (source / "fallback.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
        page = source / "index.html"
        page.write_text(
            """<html><head><title>Noscript Article</title></head><body><article>
            <h1>Noscript Article</h1>
            <p>This article has enough words to make the extractor choose this
            article element and exercise image fallback preservation.</p>
            <noscript><img src="fallback.png" alt="fallback image"></noscript>
            </article></body></html>""",
            encoding="utf-8",
        )

        result = json.loads(
            self.run_clip(
                page.resolve().as_uri(), "-o", str(self.temp / "clips"), "--rendered", "never", "--json"
            ).stdout
        )

        markdown = Path(result["markdown_path"]).read_text()
        self.assertIn("![fallback image](media/fallback-", markdown)
        self.assertEqual(len(result["media_files"]), 1)


if __name__ == "__main__":
    unittest.main()
