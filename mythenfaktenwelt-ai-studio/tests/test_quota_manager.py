import pytest
from quota.quota_manager import QuotaManager


def test_unknown_by_default(tmp_path):
    qm = QuotaManager(path=tmp_path / "quota_status.json")
    assert qm.get_status("some_service") == "UNKNOWN"
    assert not qm.is_ready("some_service")


def test_set_and_get_status(tmp_path):
    qm = QuotaManager(path=tmp_path / "quota_status.json")
    qm.set_status("grok", "READY", credits_remaining=42)
    assert qm.get_status("grok") == "READY"
    assert qm.is_ready("grok")

    qm.set_status("grok", "LIMIT")
    assert qm.get_status("grok") == "LIMIT"
    assert not qm.is_ready("grok")


def test_rejects_invalid_status(tmp_path):
    qm = QuotaManager(path=tmp_path / "quota_status.json")
    with pytest.raises(ValueError):
        qm.set_status("grok", "PROBABLY_FINE")


def test_persists_across_instances(tmp_path):
    path = tmp_path / "quota_status.json"
    QuotaManager(path=path).set_status("elevenlabs", "READY")
    qm2 = QuotaManager(path=path)
    assert qm2.get_status("elevenlabs") == "READY"
