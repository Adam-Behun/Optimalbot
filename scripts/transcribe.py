#!/usr/bin/env python3
"""
Transcribe MP3 files using Deepgram with speaker diarization.

Usage:
    python scripts/transcribe.py path/to/audio.mp3
    python scripts/transcribe.py path/to/audio.mp3 --output transcript.txt
"""

import argparse
import os
import sys
from pathlib import Path

from deepgram import DeepgramClient, PrerecordedOptions


def transcribe(audio_path: str, output_path: str | None = None) -> str:
    """Transcribe audio file with speaker diarization."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print("Error: DEEPGRAM_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    audio_file = Path(audio_path)
    if not audio_file.exists():
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Transcribing: {audio_file.name}")

    client = DeepgramClient(api_key)

    with open(audio_file, "rb") as f:
        buffer = f.read()

    # Determine mimetype from extension
    ext = audio_file.suffix.lower()
    mimetypes = {
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/m4a",
        ".flac": "audio/flac",
        ".ogg": "audio/ogg",
    }
    mimetype = mimetypes.get(ext, "audio/mp3")

    options = PrerecordedOptions(
        model="nova-2",
        smart_format=True,
        diarize=True,
        punctuate=True,
        paragraphs=True,
    )

    response = client.listen.rest.v("1").transcribe_file(
        {"buffer": buffer, "mimetype": mimetype},
        options,
    )

    # Format output with speaker labels
    transcript_lines = []
    current_speaker = None

    for word in response.results.channels[0].alternatives[0].words:
        speaker = word.speaker
        text = word.punctuated_word or word.word

        if speaker != current_speaker:
            if transcript_lines:
                transcript_lines.append("")  # blank line between speakers
            transcript_lines.append(f"[Speaker {speaker}]")
            current_speaker = speaker

        # Append word to current line or start new line
        if transcript_lines and not transcript_lines[-1].startswith("["):
            transcript_lines[-1] += f" {text}"
        else:
            transcript_lines.append(text)

    transcript = "\n".join(transcript_lines)

    # Output
    if output_path:
        with open(output_path, "w") as f:
            f.write(transcript)
        print(f"Saved to: {output_path}")
    else:
        print("\n" + "=" * 60 + "\n")
        print(transcript)

    return transcript


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files with speaker diarization"
    )
    parser.add_argument("audio_file", help="Path to audio file (MP3, WAV, etc.)")
    parser.add_argument("-o", "--output", help="Output file path (optional)")

    args = parser.parse_args()
    transcribe(args.audio_file, args.output)


if __name__ == "__main__":
    main()
