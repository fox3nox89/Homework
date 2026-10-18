import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "editor"))

from subtitles import Segment, segments_from_text_proportional, write_srt  # noqa: E402


def test_proportional_segments_cover_full_duration():
    lines = ["Kurzer Satz.", "Ein etwas laengerer zweiter Satz mit mehr Zeichen."]
    segments = segments_from_text_proportional(lines, total_duration_s=10.0)

    assert len(segments) == 2
    assert segments[0].start_s == 0.0
    assert segments[-1].end_s == 10.0
    assert segments[1].start_s == segments[0].end_s
    # laengerer Satz bekommt mehr Zeit
    assert (segments[1].end_s - segments[1].start_s) > (segments[0].end_s - segments[0].start_s)


def test_write_srt_format(tmp_path):
    segments = [Segment("Hallo Welt.", 0.0, 1.5), Segment("Zweite Zeile.", 1.5, 3.0)]
    out = tmp_path / "out.srt"
    write_srt(segments, out)

    content = out.read_text(encoding="utf-8")
    assert "1\n00:00:00,000 --> 00:00:01,500\nHallo Welt." in content
    assert "2\n00:00:01,500 --> 00:00:03,000\nZweite Zeile." in content
