"""
Publish Gate -- die einzige Stelle im gesamten System, an der ueber eine
Veroeffentlichung entschieden wird. Dieses Modul veroeffentlicht NIE etwas
selbst. Es kann nur:
  1. eine Freigabeanfrage an den Nutzer stellen (request_approval)
  2. eine bereits erteilte Freigabe abfragen (is_approved)

Eine tatsaechliche Veroeffentlichung auf TikTok ist bewusst NICHT Teil
dieses Repos als automatisierte Funktion. Nach erteilter Freigabe lädst du
das Video entweder manuell hoch, oder richtest -- als bewusster,
separater, expliziter Schritt, den DU auf deinem Rechner ausfuehrst und
den kein Bot von sich aus anstoesst -- eine eigene Upload-Automatisierung
ein. Andernfalls verstiesse dieses Skript gegen die Regel "ohne
ausdrueckliche Zustimmung niemals auf TikTok veroeffentlichen".
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVALS_DIR = REPO_ROOT / "data" / "approvals"


def _approval_path(video_id: str) -> Path:
    return APPROVALS_DIR / f"{video_id}.json"


def request_approval(video_id: str, dry_run: bool = False) -> None:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "video_id": video_id,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "status": "AWAITING_APPROVAL",
        "decided_at": None,
    }
    path = _approval_path(video_id)
    if not path.exists():
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    message = (
        f"Video '{video_id}' ist fertig und liegt auf Google Drive. "
        f"Darf es auf TikTok veroeffentlicht werden? Freigabe erteilen mit:\n"
        f"  python3 scripts/publish/publish_gate.py --approve {video_id}\n"
        f"Ablehnen mit:\n"
        f"  python3 scripts/publish/publish_gate.py --reject {video_id}"
    )
    if dry_run:
        print(f"[publish_gate] [dry-run] Freigabeanfrage (nicht wirklich gesendet):\n{message}")
    else:
        # TODO lokal: an den in config/settings.yaml konfigurierten
        # approval_channel senden (z.B. Hermes-Gateway-Nachricht). Bis dahin
        # nur lokale Ausgabe + Datei -- kein stiller Fehlschlag.
        print(f"[publish_gate] {message}")


def decide(video_id: str, approved: bool) -> None:
    path = _approval_path(video_id)
    if not path.exists():
        raise FileNotFoundError(f"Keine offene Freigabeanfrage fuer '{video_id}'.")
    record = json.loads(path.read_text(encoding="utf-8"))
    record["status"] = "APPROVED" if approved else "REJECTED"
    record["decided_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[publish_gate] '{video_id}' -> {record['status']}")


def is_approved(video_id: str) -> bool:
    path = _approval_path(video_id)
    if not path.exists():
        return False
    record = json.loads(path.read_text(encoding="utf-8"))
    return record.get("status") == "APPROVED"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--approve", metavar="VIDEO_ID")
    group.add_argument("--reject", metavar="VIDEO_ID")
    group.add_argument("--status", metavar="VIDEO_ID")
    args = parser.parse_args()

    if args.approve:
        decide(args.approve, approved=True)
    elif args.reject:
        decide(args.reject, approved=False)
    elif args.status:
        print("APPROVED" if is_approved(args.status) else "AWAITING_APPROVAL/REJECTED")
