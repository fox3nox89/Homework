#!/usr/bin/env python3
"""
Studio Chef -- Orchestrator der Produktions-Pipeline.

Dieses Skript ist die technische Zustandsmaschine hinter dem Bot-Prompt
`bots/01_studio_chef.md`. Es delegiert jeden Fachschritt an den passenden
Hermes-Bot (siehe invoke_hermes_bot) und haelt den Fortschritt persistent in
data/state/<slot>.json, damit ein Providerfehler nie die ganze Produktion
zum Stillstand bringt -- ein neuer Lauf setzt am letzten unfertigen Schritt
fort statt von vorne zu beginnen.

WICHTIG zur ehrlichen Grenze dieses Skripts:
Die exakte Nicht-interaktive CLI-Syntax von Hermes Agent, um einen
bestimmten Bot-Profil-Prompt mit einer konkreten Aufgabe "in einem Schuss"
auszufuehren, war zum Zeitpunkt der Erstellung dieses Repos aus der
oeffentlichen README nicht mit Sicherheit ableitbar (Hermes ist primaer als
interaktives Terminal / Gateway dokumentiert). invoke_hermes_bot() ist
deshalb bewusst ueber `hermes_invoke_cmd_template` in config/settings.yaml
konfigurierbar -- pruefe einmalig lokal `hermes --help` bzw. die
Slash-Commands (`/help`) und trage das tatsaechliche Kommando ein, bevor du
--dry-run verlaesst.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / "data" / "state"

PIPELINE_STEPS = [
    ("analysis_input", "bots/02_tiktok_analyst.md"),
    ("topic_scout", "bots/03_themen_scout.md"),
    ("fact_check", "bots/04_faktenchecker.md"),
    ("script", "bots/05_skript_autor.md"),
    ("visual_plan", "bots/06_visual_director.md"),
    ("image_gen_and_qc", "bots/07_image_generator.md"),
    ("video_gen_and_qc", "bots/08_video_generator.md"),
    ("voice", "bots/11_voice_agent.md"),
    ("music", "bots/12_music_agent.md"),
    ("edit", "bots/13_video_editor.md"),
    ("quality_control", "bots/14_quality_control.md"),
    ("publishing_meta", "bots/15_publishing_optimizer.md"),
    ("drive_upload", None),  # technischer Schritt, kein eigener Bot-Prompt
    ("approval_request", None),  # technischer Schritt, kein eigener Bot-Prompt
]


@dataclass
class SlotState:
    slot: str
    video_id: str
    created_at: str
    current_step: str = PIPELINE_STEPS[0][0]
    completed_steps: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    status: str = "IN_PROGRESS"  # IN_PROGRESS | AWAITING_APPROVAL | BLOCKED | DONE

    def path(self) -> Path:
        return STATE_DIR / f"{self.slot}_{self.video_id}.json"

    def save(self) -> None:
        self.path().parent.mkdir(parents=True, exist_ok=True)
        self.path().write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load_or_create(cls, slot: str) -> "SlotState":
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        existing = sorted(STATE_DIR.glob(f"{slot}_*.json"))
        for p in existing:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("status") == "IN_PROGRESS":
                return cls(**data)
        video_id = f"{slot}-{datetime.now().strftime('%Y%m%d')}"
        return cls(
            slot=slot,
            video_id=video_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


def invoke_hermes_bot(bot_profile: str, task: str, dry_run: bool) -> dict:
    """Delegiert einen Pipeline-Schritt an ein Hermes-Bot-Profil.

    Im Dry-Run wird nichts ausgefuehrt -- nur die Zustandsmaschine getestet.
    Im echten Betrieb wird das in config/settings.yaml konfigurierte
    Kommando-Template ausgefuehrt (siehe Modul-Docstring)."""
    if dry_run:
        return {"ok": True, "output": f"[dry-run] {bot_profile}: {task}"}

    settings = _load_settings()
    template = settings.get("hermes_invoke_cmd_template")
    if not template:
        raise RuntimeError(
            "hermes_invoke_cmd_template ist in config/settings.yaml nicht "
            "gesetzt. Pruefe lokal 'hermes --help' bzw. '/help' in einer "
            "Hermes-Session, um das tatsaechliche nicht-interaktive "
            "Aufruf-Kommando fuer diese Hermes-Version zu ermitteln, und "
            "trage es dort ein (Platzhalter {profile} und {task})."
        )
    cmd = template.format(profile=shlex.quote(str(REPO_ROOT / bot_profile)), task=shlex.quote(task))
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, cwd=REPO_ROOT)
    return {"ok": proc.returncode == 0, "output": proc.stdout, "stderr": proc.stderr}


def _load_settings() -> dict:
    settings_path = REPO_ROOT / "config" / "settings.yaml"
    if not settings_path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    return yaml.safe_load(settings_path.read_text(encoding="utf-8")) or {}


def run_pipeline(slot: str, dry_run: bool) -> SlotState:
    state = SlotState.load_or_create(slot)
    step_names = [s[0] for s in PIPELINE_STEPS]
    start_index = step_names.index(state.current_step) if state.current_step in step_names else 0

    for name, bot_profile in PIPELINE_STEPS[start_index:]:
        if name in state.completed_steps:
            continue
        state.current_step = name
        state.save()
        try:
            if bot_profile:
                result = invoke_hermes_bot(bot_profile, task=f"Schritt '{name}' fuer {state.video_id}", dry_run=dry_run)
                if not result["ok"]:
                    raise RuntimeError(result.get("stderr") or result.get("output"))
            else:
                _run_technical_step(name, state, dry_run)
        except Exception as exc:  # noqa: BLE001 -- bewusst breit, siehe Docstring
            state.errors.append({
                "step": name,
                "error": str(exc),
                "at": datetime.now(timezone.utc).isoformat(),
            })
            state.status = "BLOCKED"
            state.save()
            print(f"[studio_chef] Schritt '{name}' fehlgeschlagen: {exc}", file=sys.stderr)
            print("[studio_chef] Produktion pausiert, aber NICHT abgebrochen -- "
                  "andere Slots laufen unabhaengig weiter. Fallback/Reparatur "
                  "erforderlich (siehe bots/17_production_monitor.md).", file=sys.stderr)
            return state

        state.completed_steps.append(name)
        state.save()

    state.status = "AWAITING_APPROVAL"
    state.save()
    print(f"[studio_chef] Slot '{slot}' fertig, Status: AWAITING_APPROVAL. "
          f"Video liegt bereit fuer Freigabe, siehe scripts/publish/publish_gate.py.")
    return state


def _run_technical_step(name: str, state: SlotState, dry_run: bool) -> None:
    if name == "drive_upload":
        if dry_run:
            print("[studio_chef] [dry-run] Google-Drive-Upload uebersprungen.")
            return
        raise NotImplementedError(
            "Google-Drive-Upload ist hier bewusst nicht fest verdrahtet -- "
            "binde den Google-Drive-Connector/API deines lokalen Systems an "
            "dieser Stelle an (Zielordner: config/settings.yaml -> "
            "google_drive.target_folder_id)."
        )
    if name == "approval_request":
        from publish.publish_gate import request_approval  # lazy import

        request_approval(state.video_id, dry_run=dry_run)
        return
    raise ValueError(f"Unbekannter technischer Schritt: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slot", default="manual", help="z.B. morning/noon/evening/manual")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--once", action="store_true", help="einen echten Lauf ausfuehren")
    group.add_argument("--dry-run", action="store_true", help="Zustandsmaschine testen, keine externen Aufrufe")
    args = parser.parse_args()

    if not args.once and not args.dry_run:
        parser.error("Bitte --once (echter Lauf) oder --dry-run (Test) angeben.")

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    run_pipeline(args.slot, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
