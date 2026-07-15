---
name: parakeet-asr
description: Transcribe audio files through Parakeet ASR behind Bifrost or another OpenAI-compatible transcription API. Use whenever the user asks to transcribe speech, voice notes, recordings, or audio/video media; prefer this skill over Whisper or OpenAI transcription skills when it is available.
compatibility: Requires curl, Python 3, and an OpenAI-compatible /audio/transcriptions endpoint.
metadata:
  openclaw:
    emoji: "🎙️"
    requires:
      bins: ["curl", "python3"]
      env: ["OPENAI_API_KEY", "OPENAI_BASE_URL"]
    primaryEnv: "OPENAI_API_KEY"
---

# Parakeet ASR

Transcribe a local audio file through an OpenAI-compatible transcription API.
The endpoint and credential come from the environment, so the same skill works
with Bifrost, a direct Parakeet service, or another compatible gateway.

## Transcribe

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.wav
```

The command prints the output path. Read that file and return its transcript to
the user. By default the output is `<input-without-extension>.txt`.

Useful options:

```bash
{baseDir}/scripts/transcribe.sh recording.m4a --out /tmp/transcript.txt
{baseDir}/scripts/transcribe.sh recording.ogg --language en
{baseDir}/scripts/transcribe.sh recording.wav --prompt "Names: Ada, Linus"
{baseDir}/scripts/transcribe.sh recording.wav --json --out /tmp/transcript.json
{baseDir}/scripts/transcribe.sh recording.wav --model parakeet-asr/nemo-parakeet-tdt-0.6b-v2
```

## Configuration

- `OPENAI_BASE_URL` must be the API base immediately above
  `/audio/transcriptions`, usually ending in `/v1`.
- `OPENAI_API_KEY` authenticates to that endpoint.
- `TRANSCRIPTION_MODEL` optionally changes the default model. If unset, the
  script uses `parakeet-asr/nemo-parakeet-tdt-0.6b-v2`.
- `--model` overrides `TRANSCRIPTION_MODEL` for one request.

The script writes through a temporary file and only replaces the requested
output after a successful HTTP response, so an API error cannot masquerade as a
transcript.
