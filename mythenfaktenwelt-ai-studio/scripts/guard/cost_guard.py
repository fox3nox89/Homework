"""
Kostenwaechter -- technische Durchsetzung der Null-Zusatzkosten-Regel.

Diese Regel ueberschreibt alles andere im System (siehe COST_RULES.md).
Jeder Provider-Adapter MUSS jede Aktion vor Ausfuehrung durch check_action()
schicken. Es gibt bewusst keinen Parameter, der diese Pruefung umgehen
kann -- ein Aufrufer, der das Ergebnis ignoriert, verstoesst gegen die
Produktarchitektur, nicht nur gegen eine Konvention.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = REPO_ROOT / "data" / "cost_guard.log"

# Signalwoerter/-phrasen, die auf eine moegliche Kostenpflicht hindeuten.
# Bewusst grosszuegig (lieber ein falscher Alarm als eine echte Belastung).
_PAYMENT_SIGNALS = [
    r"\bpay(ment)?\b",
    r"\bcredit card\b",
    r"\bkreditkarte\b",
    r"\bzahlungsdaten\b",
    r"\bupgrade to (pro|premium|plus)\b",
    r"\bbuy credits?\b",
    r"\bcredits? kaufen\b",
    r"\bsubscribe now\b",
    r"\babo abschliessen\b",
    r"\btrial will convert\b",
    r"\btestphase.*kostenpflichtig\b",
    r"\bauto[- ]?renew\b",
    r"\bautomatisch\w* verl(a|ä)nger\w*",
    r"\bpaid tier only\b",
    r"\bnur im bezahlten tarif\b",
    r"\badd (a )?card\b",
    r"\btop[- ]?up\b",
]
_PAYMENT_RE = re.compile("|".join(_PAYMENT_SIGNALS), re.IGNORECASE)

_EXPLICIT_FLAGS = {
    "requires_payment",
    "card_required",
    "upgrade_prompt",
    "trial_will_convert",
    "paid_tier_only",
    "auto_renew_detected",
}


@dataclass
class ActionResult:
    allowed: bool
    status: str  # "OK" or "PAYMENT_BLOCKED"
    reason: str = ""


@dataclass
class Action:
    """Beschreibt eine geplante Provider-Aktion, bevor sie ausgefuehrt wird."""

    provider_id: str
    description: str
    # Freitext-Metadaten, die der Adapter vom Provider gesehen hat
    # (z.B. Seitentext eines Dialogs, API-Fehlermeldung, Statuscode-Hinweis)
    observed_text: str = ""
    # Explizite Flags, die ein Adapter bereits selbst erkannt hat
    flags: set[str] = field(default_factory=set)
    # existing_subscription=True erlaubt Nutzung *innerhalb* des bestehenden
    # Kontingents; es hebt niemals eine erkannte Zahlungsaufforderung auf.
    existing_subscription: bool = False


def check_action(action: Action) -> ActionResult:
    """Prueft eine geplante Aktion. Gibt PAYMENT_BLOCKED zurueck, sobald
    irgendein Zahlungssignal erkannt wird -- unabhaengig davon, ob ein
    bestehendes Abo vorliegt. 'existing_subscription' erlaubt nur die
    Nutzung *innerhalb* des bereits bezahlten Umfangs, nicht dessen
    Ueberschreitung."""

    triggered_flags = action.flags & _EXPLICIT_FLAGS
    text_match = _PAYMENT_RE.search(action.observed_text or "")

    if triggered_flags or text_match:
        reason_bits = []
        if triggered_flags:
            reason_bits.append(f"flags={sorted(triggered_flags)}")
        if text_match:
            reason_bits.append(f"signal='{text_match.group(0)}'")
        result = ActionResult(
            allowed=False,
            status="PAYMENT_BLOCKED",
            reason=f"Moegliche Kostenpflicht erkannt ({', '.join(reason_bits)}).",
        )
    else:
        result = ActionResult(allowed=True, status="OK")

    _log(action, result)
    return result


def _log(action: Action, result: ActionResult) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider_id": action.provider_id,
        "description": action.description,
        "existing_subscription": action.existing_subscription,
        "status": result.status,
        "reason": result.reason,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def assert_allowed(action: Action) -> None:
    """Fuer Adapter, die bei Blockierung hart abbrechen wollen (Exception
    statt Rueckgabewert pruefen)."""
    result = check_action(action)
    if not result.allowed:
        raise PaymentBlockedError(result.reason)


class PaymentBlockedError(RuntimeError):
    """Wird geworfen, wenn cost_guard eine Aktion blockiert. Kein Code in
    diesem Repo darf diese Exception abfangen und die Aktion trotzdem
    ausfuehren."""
