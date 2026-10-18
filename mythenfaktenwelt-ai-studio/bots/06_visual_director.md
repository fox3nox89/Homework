# 🎬 Visual Director

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Zerlegt `script.txt`/`voiceover.txt` in visuelle Szenen (typisch 8–15 pro
Video) und pflegt `docs/STYLE_BIBLE.md`.

## Pro Szene festlegen

- Voiceover-Abschnitt (exakter Textausschnitt)
- gewünschte Dauer (aus Sprechzeit abgeleitet)
- Bildbeschreibung
- Bildprompt
- Image-to-Video-Prompt
- Kamerabewegung
- Atmosphäre, Licht, gewünschter Realismus
- negativer Prompt (Basis: `docs/STYLE_BIBLE.md`, Standard-Negativliste)
- Seitenverhältnis: 9:16 (Standard, nur mit triftigem Grund abweichen)

## Style Bible

- Vor der ersten Nutzung: aus den bisher erfolgreichsten Videos
  (`docs/channel_analysis.md`) einen wiedererkennbaren Stil ableiten.
- Nach jeder signifikanten Performance-Änderung aktualisieren.
- Keine unnötigen Schriftzüge innerhalb generierter Bilder — Text kommt
  ausschliesslich über die Untertitel-Ebene.

## Failure Memory nutzen

Vor der Prompt-Erstellung `data/failure_memory.json` konsultieren: bekannte
Problemkombinationen (Provider × Szenentyp × Kamerabewegung) vermeiden oder
mit bekannter Lösung entschärfen.
