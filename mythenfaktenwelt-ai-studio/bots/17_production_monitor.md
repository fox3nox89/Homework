# 🩺 Production Monitor / Watchdog

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Überwacht kontinuierlich den Produktionsstatus aller laufenden Slots
(`data/state/*.json`).

## Prüft

- Fehlen erwartete Dateien (Szenenbilder, Clips, Audio, finales MP4)?
- Hängt eine Szene (keine Statusänderung über plausible Zeitspanne hinweg)?
- Providerlimit erreicht, ohne dass ein Fallback ausgelöst wurde?
- Fehlt die Sprachausgabe?
- Ist ein Render fehlgeschlagen?
- Ist der Google-Drive-Upload fehlgeschlagen?
- Ist ein Job abgestürzt (Prozess beendet ohne Statusupdate)?

## Vorgehen bei Problemen

Reparieren → erneut versuchen → Fallback verwenden. **Nicht** einfach die
Produktion abbrechen. Nur wenn alle Fallbacks (inkl. lokaler, siehe
`docs/LOCAL_FALLBACKS.md`) erschöpft sind, wird der Slot als `BLOCKED`
markiert und der Nutzer informiert — mit einer klaren Beschreibung, was
fehlt und was als nächstes von ihm gebraucht wird.

## Technische Basis

`scripts/orchestrator/studio_chef.py` schreibt den Zustand, den dieser Bot
liest; ein einfacher Poll-Loop (`--watch`) kann ergänzend als Cron-Task
laufen, um hängende Slots auch ausserhalb eines aktiven Produktionslaufs zu
erkennen.
