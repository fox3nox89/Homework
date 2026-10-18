# 🖼️ Image Generator

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Erzeugt für jede Szene (aus dem Visual Director) ein hochwertiges Bild,
bevor irgendein Image-to-Video-Schritt erfolgt.

## Provider

Modular, über `data/provider_registry.json` (Typ `image`). Mögliche bereits
verfügbare Dienste (nur nutzen, wenn aktuell zulässig und im bestehenden
Konto/Gratis-Kontingent enthalten):
- ChatGPT Images
- Google-Angebote
- andere kostenlose Cloud-Bildgeneratoren
- lokale Bildmodelle (`docs/LOCAL_FALLBACKS.md`)

Vor Verwendung: aktuelle Nutzungsbedingungen des Dienstes prüfen (jede
Provider-Wahl läuft durch `scripts/guard/cost_guard.py`).

## Anforderungen

- 9:16 (oder in 9:16 nachbearbeitet, ohne Verzerrung)
- hohe Qualität
- visuell passend zum gesprochenen Text der Szene

## Image QC (nach jeder Generierung)

Vor Weitergabe an den Video Generator:
- Erkennbare Bildfehler? (verzerrte Hände/Gesichter, unlogische Anatomie)
- Passt das Bild inhaltlich zur Szenenbeschreibung?
- Enthält das Bild unerwünschten Text/Wasserzeichen?

Ein schlecht bewertetes Bild wird **nicht** zu Video weiterverarbeitet —
neu generieren (ggf. mit angepasstem Prompt, siehe `data/failure_memory.json`)
statt fehlerhaftes Material durchzuwinken.
