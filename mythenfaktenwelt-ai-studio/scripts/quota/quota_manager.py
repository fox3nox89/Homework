"""
Quota Manager -- Status aller limitierten Dienste.

Regel: Wenn ein Kontingent nicht zuverlaessig auslesbar ist, wird UNKNOWN
verwendet. Niemals ein Restkontingent schaetzen oder erfinden.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = REPO_ROOT / "data" / "quota_status.json"

VALID_STATUSES = {"READY", "LIMIT", "UNKNOWN"}


class QuotaManager:
    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = path
        if not self.path.exists():
            example = REPO_ROOT / "config" / "quota_status.example.json"
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        self._data = json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def get_status(self, service_id: str) -> str:
        entry = self._data.get("services", {}).get(service_id)
        if entry is None:
            return "UNKNOWN"
        return entry.get("status", "UNKNOWN")

    def set_status(
        self,
        service_id: str,
        status: str,
        credits_remaining: Optional[float] = None,
        resets_at: Optional[str] = None,
    ) -> None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Ungueltiger Status '{status}'. Erlaubt: {VALID_STATUSES}")
        services = self._data.setdefault("services", {})
        services[service_id] = {
            "status": status,
            "credits_remaining": credits_remaining,
            "resets_at": resets_at,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()

    def is_ready(self, service_id: str) -> bool:
        return self.get_status(service_id) == "READY"

    def all_statuses(self) -> dict:
        return {
            sid: entry.get("status", "UNKNOWN")
            for sid, entry in self._data.get("services", {}).items()
        }
