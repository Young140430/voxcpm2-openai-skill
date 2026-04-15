#!/usr/bin/env python3
"""VoxCPM2 OpenAI-compatible TTS client.

Call the /v1/audio/speech endpoint exposed by vllm_omni to synthesize speech.
Supports zero-shot and voice-cloning modes.

Usage:
    # Zero-shot
    python voxcpm2_speech.py "Hello, this is VoxCPM2."

    # Voice cloning with local reference audio
    python voxcpm2_speech.py "Hello world" --ref-audio /path/to/reference.wav

    # Voice cloning with URL
    python voxcpm2_speech.py "Hello world" --ref-audio "https://example.com/ref.wav"

    # Custom server
    python voxcpm2_speech.py "Test" --api-base http://192.168.1.100:8000

Dependencies: httpx (auto-installed on first run).
Requires: Python >= 3.8
"""

from __future__ import annotations

import argparse
import base64
import importlib
import os
import subprocess
import sys

# ── Auto-install dependencies ──────────────────────────────────
REQUIRED_PACKAGES = ["httpx"]


def _ensure_deps() -> None:
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[VoxCPM2] Installing missing dependencies: {', '.join(missing)} ...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing, "-q"]
        )
        print("[VoxCPM2] Dependencies installed.")


_ensure_deps()

import httpx  # noqa: E402

# ── Defaults ──────────────────────────────────────────────────
DEFAULT_API_BASE = "http://localhost:8000"
DEFAULT_API_KEY = "sk-empty"
DEFAULT_MODEL = "voxcpm2"
DEFAULT_RESPONSE_FORMAT = "wav"
DEFAULT_OUTPUT = "output.wav"


# ── Core ──────────────────────────────────────────────────────
def encode_audio_to_base64(audio_path: str) -> str:
    """Encode a local audio file to a base64 data URL."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    ext = audio_path.lower().rsplit(".", 1)[-1]
    mime = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "flac": "audio/flac",
        "ogg": "audio/ogg",
    }.get(ext, "audio/wav")

    with open(audio_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def generate_speech(
    text: str,
    output: str,
    ref_audio: str | None,
    model: str,
    api_base: str,
    api_key: str,
    response_format: str,
) -> None:
    """Call the OpenAI-compatible /v1/audio/speech endpoint."""
    # VoxCPM2 has no predefined voices. The "voice" field is required by
    # the OpenAI API schema but ignored by VoxCPM2 — use any placeholder.
    # For voice cloning, pass ref_audio instead.
    payload: dict = {
        "model": model,
        "input": text,
        "voice": "default",
        "response_format": response_format,
    }

    if ref_audio:
        if ref_audio.startswith(("http://", "https://", "data:")):
            payload["ref_audio"] = ref_audio
        else:
            payload["ref_audio"] = encode_audio_to_base64(ref_audio)

    url = f"{api_base}/v1/audio/speech"
    mode = "voice cloning" if ref_audio else "zero-shot"
    print(f"[VoxCPM2] POST {url}")
    print(f"[VoxCPM2] Mode: {mode}")
    print(f"[VoxCPM2] Text: {text}")
    if ref_audio:
        display = ref_audio if len(ref_audio) <= 80 else ref_audio[:80] + "..."
        print(f"[VoxCPM2] Ref audio: {display}")

    with httpx.Client(timeout=300) as client:
        resp = client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    if resp.status_code != 200:
        print(f"[VoxCPM2] Error {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)

    with open(output, "wb") as f:
        f.write(resp.content)
    print(f"[VoxCPM2] Saved: {output} ({len(resp.content):,} bytes)")


# ── CLI ───────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="VoxCPM2 OpenAI-compatible speech synthesis client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Hello, this is VoxCPM2."
  %(prog)s "Hello world" -o hello.wav
  %(prog)s "今天天气不错" --ref-audio speaker.wav
  %(prog)s "今天天气不错" --ref-audio "https://example.com/speaker.wav"
  %(prog)s "Custom server" --api-base http://192.168.1.100:8000
        """,
    )
    p.add_argument("text", help="Text to synthesize")
    p.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help=f"Output file path (default: {DEFAULT_OUTPUT})")
    p.add_argument("--ref-audio", default=None, help="Reference audio for voice cloning (local path, URL, or data: URI)")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    p.add_argument("--api-base", default=DEFAULT_API_BASE, help=f"API server URL (default: {DEFAULT_API_BASE})")
    p.add_argument("--api-key", default=DEFAULT_API_KEY, help=f"API key (default: {DEFAULT_API_KEY})")
    p.add_argument("--response-format", default=DEFAULT_RESPONSE_FORMAT, help=f"Audio format: wav/mp3/flac/ogg (default: {DEFAULT_RESPONSE_FORMAT})")
    return p


def main() -> None:
    if sys.version_info < (3, 8):
        print(f"[VoxCPM2] Error: Python >= 3.8 required, current version {sys.version}")
        sys.exit(1)

    args = build_parser().parse_args()
    generate_speech(
        text=args.text,
        output=args.output,
        ref_audio=args.ref_audio,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        response_format=args.response_format,
    )


if __name__ == "__main__":
    main()
