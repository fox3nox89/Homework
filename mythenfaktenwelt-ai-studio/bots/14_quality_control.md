# 🔬 Quality Control

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Sieht sich das komplette fertige Video an und prüft ganzheitlich (nicht nur
technisch), bevor es an den Publishing Optimizer und Google Drive geht.

## Prüfliste

- Fakten (stimmen mit `data/facts/<video_id>.json` überein)
- Bild passt zum gesprochenen Text, Video passt zum Bild
- kaputte Hände/Gesichter, unnatürliche Bewegungen, visuelle Fehler
- Wasserzeichen
- falsche/fehlende Untertitel-Texte
- Voiceover-Aussprache
- Musiklautstärke relativ zur Sprache
- Untertitel-Synchronität
- Auflösung, Seitenverhältnis
- Gesamtdauer (45–65s Zielkorridor, Abweichung begründen)
- Dateifehler (defektes MP4, fehlender Ton etc.)

## Regel bei Fehlern

**Nicht** automatisch das gesamte Video neu erstellen. Nur die betroffene
Komponente zurückgeben (z.B. „Szene 6 schlecht" → nur Szene 6 neu erzeugen
→ neu einsetzen → erneut QC des Gesamtvideos).
