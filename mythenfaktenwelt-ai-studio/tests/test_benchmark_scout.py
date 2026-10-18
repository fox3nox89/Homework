import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "scout"))

from benchmark_scout import BenchmarkCandidate, engagement_score, rank_candidates  # noqa: E402


def _c(**kwargs):
    defaults = dict(
        platform="youtube", channel_name="x", video_url="https://x/1", topic_cluster="Mythen"
    )
    defaults.update(kwargs)
    return BenchmarkCandidate(**defaults)


def test_engagement_score_none_without_views():
    assert engagement_score(_c(views=None, likes=100)) is None
    assert engagement_score(_c(views=0, likes=100)) is None


def test_engagement_score_computed():
    c = _c(views=1000, likes=80, comments=20)
    assert engagement_score(c) == 0.1


def test_rank_prefers_higher_views():
    low = _c(video_url="a", views=1000, likes=10)
    high = _c(video_url="b", views=1_000_000, likes=10)
    ranked = rank_candidates([low, high])
    assert ranked[0].video_url == "b"


def test_rank_uses_engagement_as_tiebreak():
    same_views_low_engagement = _c(video_url="a", views=1000, likes=1)
    same_views_high_engagement = _c(video_url="b", views=1000, likes=100)
    ranked = rank_candidates([same_views_low_engagement, same_views_high_engagement])
    assert ranked[0].video_url == "b"


def test_candidates_without_views_rank_last():
    unknown = _c(video_url="a", views=None)
    known = _c(video_url="b", views=1)
    ranked = rank_candidates([unknown, known])
    assert ranked[0].video_url == "b"
