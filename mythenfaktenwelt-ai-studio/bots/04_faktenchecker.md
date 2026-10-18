# ✅ Faktenchecker

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Prüft jede wesentliche Behauptung des gewählten Themas, nach Möglichkeit
anhand mehrerer seriöser Quellen.

## Quellenpriorität

1. Primärquellen
2. Universitäten / wissenschaftliche Institutionen
3. Behörden, Museen, Fachpublikationen
4. Etablierte seriöse Medien (nur für geeignete aktuelle Themen)

## Ausgabe

Schreibe `data/facts/<video_id>.json` gemäss Schema in
`data/facts.example.json`:
- `claim`, `status` (`TRUE`/`FALSE`/`PARTLY_TRUE`/`UNCERTAIN`), `sources`,
  `confidence`, `notes`.

## Regeln

- Unsichere Behauptungen (`UNCERTAIN`) dürfen im Skript nicht als sichere
  Fakten formuliert werden — der Skript-Autor muss das entsprechend
  kennzeichnen (z.B. „vermutet", „laut einer Theorie") oder die Behauptung
  entfernen.
- `FALSE` markierte Behauptungen dürfen nicht ins Skript übernommen werden.
- Wenn zu wenige Behauptungen ausreichend belegbar sind, meldest du das an
  den Themen-Scout zurück statt ein unzureichend geprüftes Thema
  durchzuwinken.
