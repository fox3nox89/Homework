"""
Benchmark Scout -- Bewertungslogik fuer fremde Top-Videos (Millionen
Views) im selben Themenfeld. Dieses Modul erfindet keine Netzwerk-Calls
gegen YouTube/TikTok (die echten Abrufe laufen lokal ueber die offizielle
YouTube Data API bzw. den persistenten Browser, siehe
bots/19_benchmark_analyst.md). Es bildet die reine, testbare Logik ab:
Kandidaten bewerten/ranken und destillierte Muster in die Registry
schreiben -- die Datenbeschaffung wird als Funktion injiziert, damit sie
lokal an die echten APIs angebunden werden kann.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_PATH = REPO_ROOT / "data" / "benchmark_videos.json"


@dataclass
class BenchmarkCandidate:
    platform: str  # "youtube" | "tiktok"
    channel_name: str
    video_url: str
    topic_cluster: str
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    length_seconds: Optional[float] = None
    hook_text: Optional[str] = None
    structure_notes: Optional[str] = None
    analysis_method: str = "metadata_only"


def engagement_score(candidate: BenchmarkCandidate) -> Optional[float]:
    """(Likes + Kommentare) / Views -- None, wenn Views unbekannt/0, statt
    einen falschen Wert vorzutaeuschen."""
    if not candidate.views:
        return None
    likes = candidate.likes or 0
    comments = candidate.comments or 0
    return (likes + comments) / candidate.views


def rank_candidates(candidates: list[BenchmarkCandidate]) -> list[BenchmarkCandidate]:
    """Rankt nach Views zuerst (Reichweite), Engagement-Score als
    Tie-Breaker. Kandidaten ohne Views-Angabe landen am Ende, nicht bei 0
    behauptet."""

    def sort_key(c: BenchmarkCandidate):
        has_views = c.views is not None
        score = engagement_score(c) or 0.0
        return (has_views, c.views or 0, score)

    return sorted(candidates, key=sort_key, reverse=True)


def fetch_and_rank(
    topic_cluster: str,
    fetch_fn: Callable[[str], list[BenchmarkCandidate]],
    top_n: int = 10,
) -> list[BenchmarkCandidate]:
    """fetch_fn ist die lokal injizierte, echte Datenquelle (z.B. ein
    Wrapper um die YouTube Data API `search.list` + `videos.list`, oder
    einen Browser-Lesevorgang fuer TikTok). Hier wird nur gerankt."""
    candidates = fetch_fn(topic_cluster)
    return rank_candidates(candidates)[:top_n]


def save_candidates(candidates: list[BenchmarkCandidate]) -> None:
    if not BENCHMARK_PATH.exists():
        example = REPO_ROOT / "data" / "benchmark_videos.example.json"
        BENCHMARK_PATH.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    registry = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    entries = registry.setdefault("entries", [])
    existing_urls = {e["video_url"] for e in entries}

    next_id = len(entries) + 1
    for c in candidates:
        if c.video_url in existing_urls:
            continue
        entries.append({
            "id": f"BM-{next_id:04d}",
            "platform": c.platform,
            "channel_name": c.channel_name,
            "video_url": c.video_url,
            "topic_cluster": c.topic_cluster,
            "views": c.views,
            "likes": c.likes,
            "comments": c.comments,
            "length_seconds": c.length_seconds,
            "hook_text": c.hook_text,
            "structure_notes": c.structure_notes,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "analysis_method": c.analysis_method,
        })
        existing_urls.add(c.video_url)
        next_id += 1

    BENCHMARK_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
