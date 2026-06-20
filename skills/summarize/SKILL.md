---
name: summarize
description: "Summarize URLs, files, stdin, YouTube, podcasts, PDFs, audio, video."
---

# summarize

CLI-only steipete/summarize wrapper. No daemon/browser extension. The local
wrapper streams output normally and also saves stdout copies under
`/tmp/summarize/`.

```bash
summarize "https://example.com"
```

Wrapper runs:

```bash
npx -y @steipete/summarize "$@"
```

The wrapper saves each successful stdout-producing run to:

```text
/tmp/summarize/YYYYMMDD-HHMMSS-summary-<input>.md
/tmp/summarize/YYYYMMDD-HHMMSS-transcript-<input>.md
```

Transcript files are created when using `--extract`; other runs are saved as
summaries.

## Commands

```bash
summarize "https://example.com" --length short --plain
summarize "/path/to/file.pdf" --model google/gemini-3-flash --plain
printf "%s\n" "content to summarize" | summarize - --plain
summarize "https://youtu.be/VIDEO_ID" --youtube auto --plain
summarize "https://example.com" --extract
```

## Workflow

1. Default: `summarize <url-or-path> --plain`; also check `/tmp/summarize/` for the saved summary.
2. Detail control: `--length short|medium|long|xl|xxl`.
3. Cleaned source, no LLM summary: `--extract`; this saves a transcript/source file in `/tmp/summarize/`.
4. Stdin: pipe content and pass `-`.
5. Model override only when user asks or input type needs it.
6. If the user asks where a prior transcript or summary went, list the newest files with `ls -lt /tmp/summarize/ | head`.

## Notes

- Requires Node 24+ and `npx`.
- Provider auth/config belongs to user env: API keys or local CLIs like Codex/Claude/Gemini.
- Media-heavy paths may need `ffmpeg`, `yt-dlp`, or `tesseract`.
