"""
Erzeugt eine SRT-Untertiteldatei, synchron zum Voiceover.

Bevorzugt: echte Wort-/Segment-Timestamps vom TTS-Provider (z.B.
ElevenLabs liefert bei manchen Endpunkten Zeitstempel). Nur wenn keine
Timestamps vorliegen, wird die Dauer proportional zur Zeichenzahl je
Segment auf die bekannte Gesamtdauer verteilt (Naeherung, kein Fakt --
im dann folgenden QC-Schritt auf Synchronitaet pruefen).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Segment:
    text: str
    start_s: float
    end_s: float


def _format_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments: list[Segment], output_path: Path) -> None:
    lines = []
    for i, seg in enumerate(segments, start=1):
        lines.append(str(i))
        lines.append(f"{_format_timestamp(seg.start_s)} --> {_format_timestamp(seg.end_s)}")
        lines.append(seg.text.strip())
        lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def segments_from_text_proportional(
    voiceover_lines: list[str], total_duration_s: float, min_seg_s: float = 1.2
) -> list[Segment]:
    """Fallback ohne echte TTS-Timestamps: Dauer proportional zur
    Zeichenzahl verteilen. Nur verwenden, wenn der Voice-Provider keine
    Zeitstempel liefert -- danach im QC-Schritt Synchronitaet pruefen."""
    lengths = [max(len(line), 1) for line in voiceover_lines]
    total_len = sum(lengths)
    segments: list[Segment] = []
    cursor = 0.0
    for line, length in zip(voiceover_lines, lengths):
        duration = max(total_duration_s * (length / total_len), min_seg_s)
        segments.append(Segment(text=line, start_s=cursor, end_s=cursor + duration))
        cursor += duration
    if segments:
        # letzte Endzeit auf die tatsaechliche Gesamtdauer kappen
        segments[-1].end_s = total_duration_s
    return segments
