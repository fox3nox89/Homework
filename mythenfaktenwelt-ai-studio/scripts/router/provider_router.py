"""
Provider Router -- waehlt fuer eine Szene/Aufgabe den besten aktuell
nutzbaren Provider, ohne jemals Kosten zu verursachen.

Reihenfolge, in der Kandidaten geprueft werden:
1. Provider mit existing_subscription=True und Quota-Status READY
2. Andere APPROVED-Provider mit Quota-Status READY (echte Gratis-Kontingente)
3. Lokaler Fallback (type == "local"), falls in der Registry vorhanden
4. Kein Kandidat mehr -> NoProviderAvailable, Studio Chef muss Slot pausieren

Jeder Kandidat wird zusaetzlich durch den Cost Guard geschickt, bevor er
zurueckgegeben wird -- der Router selbst trifft keine Kostenentscheidung.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guard.cost_guard import Action, check_action  # noqa: E402
from quota.quota_manager import QuotaManager  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "provider_registry.json"


class NoProviderAvailable(RuntimeError):
    pass


@dataclass
class ProviderChoice:
    provider_id: str
    type: str
    reason: str


class ProviderRouter:
    def __init__(
        self,
        registry_path: Path = DEFAULT_REGISTRY_PATH,
        quota_manager: Optional[QuotaManager] = None,
    ):
        self.registry_path = registry_path
        if not self.registry_path.exists():
            example = REPO_ROOT / "config" / "providers.example.json"
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            self.registry_path.write_text(
                example.read_text(encoding="utf-8"), encoding="utf-8"
            )
        self._registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.quota = quota_manager or QuotaManager()

    def _entries(self, provider_type: str):
        return [
            e for e in self._registry.get("entries", []) if e["type"] == provider_type
        ]

    def choose(self, provider_type: str, exclude: Optional[set[str]] = None) -> ProviderChoice:
        """provider_type z.B. 'image_to_video', 'image', 'tts', 'music'."""
        exclude = exclude or set()
        candidates = [e for e in self._entries(provider_type) if e["id"] not in exclude]

        # 1) Bestehendes Abo + READY
        for tier_name, predicate in (
            ("bestehendes Abo (READY)", lambda e: e.get("existing_subscription") and e["status"] == "APPROVED"),
            ("Gratis-Provider (APPROVED, READY)", lambda e: not e.get("existing_subscription") and e["status"] == "APPROVED"),
            ("lokaler Fallback", lambda e: e["type"] == provider_type and e.get("automatable_via") in (None, "none") and "local" in e["id"]),
        ):
            for entry in candidates:
                if not predicate(entry):
                    continue
                quota_status = self.quota.get_status(entry["id"])
                if quota_status == "LIMIT":
                    continue
                # READY oder UNKNOWN werden versucht (UNKNOWN != verboten,
                # aber jede Aktion laeuft trotzdem durch den Cost Guard).
                action = Action(
                    provider_id=entry["id"],
                    description=f"Auswahl fuer {provider_type} ({tier_name})",
                    existing_subscription=bool(entry.get("existing_subscription")),
                )
                result = check_action(action)
                if result.allowed:
                    return ProviderChoice(
                        provider_id=entry["id"], type=provider_type, reason=tier_name
                    )
                # PAYMENT_BLOCKED -> naechsten Kandidaten in dieser Stufe probieren
                continue

        raise NoProviderAvailable(
            f"Kein nutzbarer Provider fuer '{provider_type}' verfuegbar. "
            f"Alle Kandidaten haben LIMIT, sind nicht APPROVED, oder wurden "
            f"vom Cost Guard blockiert. Studio Chef muss den Slot pausieren "
            f"und den Nutzer informieren -- kein Fallback auf Bezahlung."
        )


if __name__ == "__main__":
    router = ProviderRouter()
    for ptype in ("image_to_video", "image", "tts", "music"):
        try:
            choice = router.choose(ptype)
            print(f"{ptype}: -> {choice.provider_id} ({choice.reason})")
        except NoProviderAvailable as e:
            print(f"{ptype}: KEIN PROVIDER -- {e}")
