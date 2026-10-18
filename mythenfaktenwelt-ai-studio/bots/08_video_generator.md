# 🎥 Video Generator

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Wandelt freigegebene Bilder (nach Image QC) per Image-to-Video in kurze
Clips um. Ruft dafür **nicht direkt** einen bestimmten Anbieter fest
verdrahtet auf, sondern fragt den Provider Router
(`scripts/router/provider_router.py`) nach dem aktuell besten verfügbaren
Dienst.

## Wichtig

Niemals allein von Grok abhängig sein. Wenn Grok verfügbar ist, darf das
bestehende Grok-Abo genutzt werden. Erreicht Grok sein Limit: **nicht
stoppen**, sofort den vom Provider Router gelieferten nächsten Dienst
verwenden.

## Clip QC (nach jeder Generierung)

- Unnatürliche Bewegungen? Gesichts-/Handfehler durch die Animation?
- Entspricht der Clip der geforderten Kamerabewegung/Atmosphäre?
- Wasserzeichen vorhanden? (führt zu Ablehnung, ausser technisch nicht
  vermeidbar und vom Nutzer akzeptiert)
- Tatsächlich 9:16, nicht verzerrt?

Fehlerhafte Clips: Ursache in `data/failure_memory.json` eintragen
(Provider, Szenentyp, Kamerabewegung, Prompt) und entweder mit
angepasstem Prompt erneut beim selben Provider oder beim nächsten Provider
in der Router-Kette versuchen.
