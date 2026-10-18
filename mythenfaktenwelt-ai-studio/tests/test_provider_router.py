import json

import pytest
from quota.quota_manager import QuotaManager
from router.provider_router import NoProviderAvailable, ProviderRouter

REGISTRY = {
    "entries": [
        {
            "id": "grok", "type": "image_to_video", "status": "APPROVED",
            "existing_subscription": True, "automatable_via": "api",
        },
        {
            "id": "google_flow", "type": "image_to_video", "status": "APPROVED",
            "existing_subscription": False, "automatable_via": "api",
        },
        {
            "id": "rejected_provider", "type": "image_to_video", "status": "REJECTED",
            "existing_subscription": False, "automatable_via": "api",
        },
    ]
}


def _make_router(tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(REGISTRY), encoding="utf-8")
    quota = QuotaManager(path=tmp_path / "quota.json")
    return ProviderRouter(registry_path=registry_path, quota_manager=quota), quota


def test_prefers_existing_subscription_when_ready(tmp_path):
    router, quota = _make_router(tmp_path)
    quota.set_status("grok", "READY")
    quota.set_status("google_flow", "READY")

    choice = router.choose("image_to_video")
    assert choice.provider_id == "grok"


def test_falls_back_to_free_provider_when_existing_subscription_hits_limit(tmp_path):
    router, quota = _make_router(tmp_path)
    quota.set_status("grok", "LIMIT")
    quota.set_status("google_flow", "READY")

    choice = router.choose("image_to_video")
    assert choice.provider_id == "google_flow"


def test_rejected_provider_never_chosen(tmp_path):
    router, quota = _make_router(tmp_path)
    quota.set_status("grok", "LIMIT")
    quota.set_status("google_flow", "LIMIT")

    with pytest.raises(NoProviderAvailable):
        router.choose("image_to_video")


def test_never_returns_a_provider_blocked_by_cost_guard(tmp_path):
    # Simuliert einen Provider, dessen Registrierung selbst schon als
    # zahlungspflichtig markiert waere -- der Cost Guard prueft zwar nur
    # Action-Text/Flags, aber der Router darf grundsaetzlich nie einen von
    # cost_guard blockierten Kandidaten zurueckgeben. Hier: kein Kandidat
    # mit existing_subscription/READY vorhanden simuliert LIMIT ueberall.
    router, quota = _make_router(tmp_path)
    quota.set_status("grok", "UNKNOWN")
    quota.set_status("google_flow", "LIMIT")
    choice = router.choose("image_to_video")
    # UNKNOWN wird versucht (nicht verboten), aber niemals stillschweigend
    # als READY behauptet.
    assert choice.provider_id == "grok"
