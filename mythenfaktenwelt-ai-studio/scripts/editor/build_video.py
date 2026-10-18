#!/usr/bin/env python3
"""
Video Editor -- setzt Clips, Voiceover, Musik und Untertitel per FFmpeg zu
einem finalen 1080x1920 H.264-MP4 zusammen. Erfordert ein lokal
installiertes FFmpeg (wird von der Hermes-Installation typischerweise
mitgebracht, siehe SETUP.md).

Clips werden nie verzerrt: skaliert per 'force_original_aspect_ratio=decrease'
und auf 1080x1920 zentriert aufgefuellt (Letterbox/Pillarbox statt Stretch).
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

TARGET_W = 1080
TARGET_H = 1920

SCALE_PAD_FILTER = (
    f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=decrease,"
    f"pad={TARGET_W}:{TARGET_H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
)


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg wurde nicht gefunden. Installiere es lokal (siehe SETUP.md) "
            "bevor der Video Editor laeuft."
        )


def normalize_clip(input_path: Path, output_path: Path) -> None:
    """Bringt einen einzelnen Clip verzerrungsfrei auf 1080x1920."""
    _require_ffmpeg()
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(input_path),
            "-vf", SCALE_PAD_FILTER,
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-an",
            str(output_path),
        ],
        check=True,
    )


def concat_clips(clip_paths: list[Path], output_path: Path) -> None:
    """Haengt bereits normalisierte Clips (gleiche Aufloesung/Codec)
    aneinander, per FFmpeg-Concat-Demuxer (kein Re-Encode noetig)."""
    _require_ffmpeg()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve()}'\n")
        list_path = Path(f.name)
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                str(output_path),
            ],
            check=True,
        )
    finally:
        list_path.unlink(missing_ok=True)


def mix_audio(voice_path: Path, music_path: Path | None, output_path: Path, music_gain_db: float = -20.0) -> None:
    """Mischt Voiceover und (optionale) Hintergrundmusik. Musik darf die
    Sprache nie ueberdecken -- Richtwert siehe docs/STYLE_BIBLE.md."""
    _require_ffmpeg()
    if music_path is None:
        shutil.copy(voice_path, output_path)
        return
    filter_complex = f"[1:a]volume={music_gain_db}dB[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(voice_path),
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            str(output_path),
        ],
        check=True,
    )


def mux_video_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    _require_ffmpeg()
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path),
        ],
        check=True,
    )


def burn_subtitles(video_path: Path, srt_path: Path, output_path: Path) -> None:
    """Brennt Untertitel fest ein, mit Rand innerhalb der TikTok-Safe-Zone
    (MarginV haelt Abstand zu UI-Elementen am unteren Bildrand)."""
    _require_ffmpeg()
    style = "FontName=Arial,FontSize=20,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Alignment=2,MarginV=220"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"subtitles={srt_path}:force_style='{style}'",
            "-c:a", "copy",
            str(output_path),
        ],
        check=True,
    )


def assemble(
    clip_paths: list[Path],
    voice_path: Path,
    music_path: Path | None,
    srt_path: Path,
    final_output_path: Path,
) -> None:
    """Kompletter Pipeline-Durchlauf: normalisieren -> concat -> Audio
    mischen -> muxen -> Untertitel einbrennen."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        normalized = []
        for i, clip in enumerate(clip_paths):
            out = tmp_dir / f"norm_{i:03d}.mp4"
            normalize_clip(clip, out)
            normalized.append(out)

        concatenated = tmp_dir / "concatenated.mp4"
        concat_clips(normalized, concatenated)

        mixed_audio = tmp_dir / "mixed_audio.aac"
        mix_audio(voice_path, music_path, mixed_audio)

        muxed = tmp_dir / "muxed.mp4"
        mux_video_audio(concatenated, mixed_audio, muxed)

        burn_subtitles(muxed, srt_path, final_output_path)

    print(f"[build_video] Fertig: {final_output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clips", nargs="+", type=Path, required=True)
    parser.add_argument("--voice", type=Path, required=True)
    parser.add_argument("--music", type=Path, default=None)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    assemble(args.clips, args.voice, args.music, args.srt, args.out)
