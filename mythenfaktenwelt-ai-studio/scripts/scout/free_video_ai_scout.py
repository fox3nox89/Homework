"""
Free Video AI Scout -- Testrahmen fuer neue Image-to-Video-Kandidaten.

Dieses Skript erfindet keine Provider-Adapter fuer konkrete Dienste (die
aktuelle Anbieterlandschaft aendert sich schneller, als ein Adapter hier
gepflegt werden koennte, und jeder Dienst braucht echte, von dir gepruefte
Zugangsdaten/AGB-Zustimmung). Stattdessen definiert es:

1. Ein Interface (ProviderAdapter), das ein neuer Kandidat implementieren
   muss, um automatisiert getestet zu werden.
2. Einen Standardtest (run_standard_test), der ein Testbild durch den
   Adapter schickt, das Ergebnis technisch prueft (Aufloesung/Seiten-
   verhaeltnis/Dauer via ffprobe) und in die Registry eintraegt.
3. Einen manuellen Bewertungspfad (record_manual_assessment) fuer Faelle,
   in denen (noch) kein Adapter existiert, aber eine Einschaetzung anhand
   offizieller Dokumentation dokumentiert werden soll -- mit Status
   CANDIDATE, nie APPROVED, solange kein echter Test gelaufen ist.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Protocol

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data" / "provider_registry.json"


class ProviderAdapter(Protocol):
    id: str

    def generate_image_to_video(self, image_path: Path, prompt: str, out_path: Path) -> None:
        """Muss out_path mit dem erzeugten Clip befuellen oder eine
        Exception werfen. Darf NIE selbststaendig eine Zahlung ausloesen --
        jeder Adapter muss vor der eigentlichen Anfrage
        scripts.guard.cost_guard.check_action() aufrufen."""
        ...


@dataclass
class TestResult:
    provider_id: str
    passed: bool
    aspect_ratio_ok: bool
    duration_s: Optional[float]
    watermark_suspected: Optional[bool]
    notes: str


def _ffprobe_dimensions(video_path: Path) -> tuple[int, int, float]:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-show_entries", "format=duration",
            "-of", "json", str(video_path),
        ],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(out.stdout)
    stream = data["streams"][0]
    duration = float(data.get("format", {}).get("duration", 0.0))
    return stream["width"], stream["height"], duration


def run_standard_test(adapter: ProviderAdapter, test_image: Path, test_prompt: str, work_dir: Path) -> TestResult:
    work_dir.mkdir(parents=True, exist_ok=True)
    out_path = work_dir / f"{adapter.id}_test_clip.mp4"
    try:
        adapter.generate_image_to_video(test_image, test_prompt, out_path)
    except Exception as exc:  # noqa: BLE001
        return TestResult(adapter.id, False, False, None, None, f"Fehler bei Generierung: {exc}")

    if not out_path.exists():
        return TestResult(adapter.id, False, False, None, None, "Kein Output-Clip erzeugt.")

    width, height, duration = _ffprobe_dimensions(out_path)
    aspect_ok = height > width and abs((height / width) - (16 / 9)) < 0.05
    result = TestResult(
        provider_id=adapter.id,
        passed=aspect_ok,
        aspect_ratio_ok=aspect_ok,
        duration_s=duration,
        watermark_suspected=None,  # manuelle Sichtpruefung noetig, nicht automatisch erkennbar
        notes=f"{width}x{height}, {duration:.1f}s. Wasserzeichen manuell pruefen: {out_path}",
    )
    _update_registry(adapter.id, status="CANDIDATE" if result.passed else "REJECTED", notes=result.notes)
    return result


def record_manual_assessment(provider_id: str, status: str, notes: str) -> None:
    if status not in ("APPROVED", "CANDIDATE", "REJECTED"):
        raise ValueError("status muss APPROVED, CANDIDATE oder REJECTED sein")
    if status == "APPROVED":
        raise ValueError(
            "APPROVED darf nur nach einem tatsaechlich durchgefuehrten Test "
            "(run_standard_test) vergeben werden, nicht rein manuell/aus "
            "Dokumentation."
        )
    _update_registry(provider_id, status=status, notes=notes)


def _update_registry(provider_id: str, status: str, notes: str) -> None:
    if not REGISTRY_PATH.exists():
        example = REPO_ROOT / "config" / "providers.example.json"
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = registry.setdefault("entries", [])
    entry = next((e for e in entries if e["id"] == provider_id), None)
    if entry is None:
        entry = {
            "id": provider_id, "type": "image_to_video", "existing_subscription": False,
            "supports_9_16": None, "watermark": None, "commercial_use_ok": None,
            "automatable_via": "none",
        }
        entries.append(entry)
    entry["status"] = status
    entry["quota"] = entry.get("quota", "UNKNOWN")
    entry["last_checked"] = datetime.now(timezone.utc).isoformat()
    entry["notes"] = notes
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
