---
name: summarize
description: "Summarize URLs, files, stdin, YouTube, podcasts, PDFs, audio, video."
---

# summarize

CLI-only steipete/summarize wrapper. No daemon/browser extension.

```bash
summarize "https://example.com"
```

Wrapper runs:

```bash
npx -y @steipete/summarize "$@"
```

## Commands

```bash
summarize "https://example.com" --length short --plain
summarize "/path/to/file.pdf" --model google/gemini-3-flash --plain
printf "%s\n" "content to summarize" | summarize - --plain
summarize "https://youtu.be/VIDEO_ID" --youtube auto --plain
summarize "https://example.com" --extract
```

## Workflow

1. Default: `summarize <url-or-path> --plain`.
2. Detail control: `--length short|medium|long|xl|xxl`.
3. Cleaned source, no LLM summary: `--extract`.
4. Stdin: pipe content and pass `-`.
5. Model override only when user asks or input type needs it.

## Notes

- Requires Node 24+ and `npx`.
- Provider auth/config belongs to user env: API keys or local CLIs like Codex/Claude/Gemini.
- Media-heavy paths may need `ffmpeg`, `yt-dlp`, or `tesseract`.
