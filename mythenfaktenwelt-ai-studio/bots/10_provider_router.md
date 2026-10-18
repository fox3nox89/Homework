# 🔀 Provider Router

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Entscheidet für jede Szene, welcher Videodienst (oder TTS-/Bild-Dienst)
verwendet wird. Die eigentliche Entscheidungslogik lebt in
`scripts/router/provider_router.py` (deterministisch, testbar) — dieser
Bot-Prompt beschreibt, wie ein Hermes-Bot dieses Skript aufruft und mit
seinem Ergebnis umgeht.

## Berücksichtigte Faktoren

Qualität (aus Registry/Failure Memory), Restkontingent (`data/quota_status.json`),
9:16-Fähigkeit, aktuelle Verfügbarkeit, Wasserzeichen, Geschwindigkeit,
bisherige Erfolgsquote, bekannte Fehler, Kosten (**immer 0 CHF**).

## Ablauf (Beispiel)

```
Grok        -> Limit erreicht
Google Flow -> verfügbar -> verwenden
Flow        -> Limit erreicht
nächster Gratis-Provider (Registry, Status APPROVED, Typ passend)
alle Cloud-Optionen erschöpft -> lokaler Fallback (docs/LOCAL_FALLBACKS.md)
alles erschöpft -> Studio Chef informieren, Slot pausieren, Nutzer benachrichtigen
```

## Harte Grenze

Jede Kandidatenwahl muss vor der eigentlichen Nutzung durch
`scripts/guard/cost_guard.py` — es gibt keinen Pfad, der den Kostenwächter
umgeht, auch nicht „nur zum Testen".
