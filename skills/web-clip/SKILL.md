---
name: web-clip
description: Clip URLs into local Markdown folders with downloaded media. Use when the user asks to save, clip, archive, preserve, or convert a webpage/article/blog post/documentation page into Markdown files.
---

# web-clip

Save a URL as a self-contained Markdown folder:

```bash
web-clip "https://example.com/article" -o clips
```

Output:

```text
clips/<page-slug>/
  index.md      # Markdown with YAML-ish front matter
  source.html   # fetched source HTML for debugging/re-extraction
  media/        # downloaded images referenced by index.md
```

## Commands

```bash
web-clip URL
web-clip URL -o ~/clips
web-clip URL --slug custom-folder-name --overwrite
web-clip URL --no-media
web-clip URL --rendered always
web-clip URL --json
```

## Workflow

1. Run `web-clip URL -o <folder>`.
2. Check the reported word count and media count.
3. Inspect `index.md` if the page is complex, login-gated, or heavily rendered by JavaScript.
4. If output is too short or the page is rendered by JavaScript, retry with `--rendered always`.

## Notes

- The default path is static HTML extraction with automatic rendered fallback when the static article is very short.
- `--rendered always` renders with Playwright before extraction for JavaScript-heavy pages.
- It removes common navigation, scripts, styles, forms, and hidden content.
- It chooses likely article/main content, converts headings/lists/tables/code/images/links to Markdown, downloads image media, and rewrites image links to local `media/` paths.
- It is best for public article/documentation pages. Pages requiring login may still need a browser session with the right account/profile.
