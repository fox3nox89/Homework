# Style Bible — MythenFaktenWelt

> Vom Visual-Director-Bot zu erstellen/pflegen, basierend auf einer Analyse
> der bisher erfolgreichsten veröffentlichten Videos (`docs/channel_analysis.md`
> und `data/content_history.json`). Solange keine ausreichende Historie
> vorliegt, ist dies ein Entwurf, der nach den ersten Produktionsläufen
> verfeinert wird — nicht als endgültig behandeln.

## Bildsprache

- Seitenverhältnis: 9:16 (Portrait), durchgängig
- Realismus-Grad: _(festlegen nach ersten Tests — z.B. "fotorealistisch" vs.
  "stilisiert/cinematic")_
- Farbpalette / Stimmung: _(aus erfolgreichen bisherigen Videos ableiten)_
- Licht: _(z.B. dramatisch, warm/kalt je nach Thema)_
- **Keine unnötigen Schriftzüge innerhalb generierter Bilder** — Text kommt
  ausschliesslich über die Untertitel-Ebene im Video-Editor.
- Wiederkehrende visuelle Motive, die den Kanal wiedererkennbar machen:
  _(nach ersten Videos festlegen)_

## Negative Prompts (Standard, für jede Szene ergänzbar)

```
text, watermark, logo, deformed hands, extra fingers, blurry, low quality,
distorted face, duplicate limbs, oversaturated, cartoon (falls Realismus
gewünscht)
```

## Kamera & Bewegung (Image-to-Video)

- Bevorzugte Kamerabewegungen: _(z.B. leichter Zoom, Parallax — nach Tests
  festlegen, da manche Bewegungen bei bestimmten Providern Gesichtsfehler
  verursachen; siehe `data/failure_memory.json`)_
- Clipdauer pro Szene: an Voiceover-Segmentlänge gekoppelt (siehe
  `bots/06_visual_director.md`)

## Ton & Sprache (Skript)

- Deutsch, kurze Sätze, sachlich korrekt, keine erfundene Dramatik
- Starke erste 1–2 Sekunden (Hook) — konkrete Muster, die bei
  MythenFaktenWelt funktioniert haben: _(aus channel_analysis.md ableiten)_

## Musik

- Lautstärke relativ zur Stimme: Musik darf Sprache nie überdecken
  (Richtwert im Video-Editor: Musik ca. -18 bis -22 LUFS relativ zur
  Sprachspur, iterativ anpassen)

---
*Dieses Dokument wird vom Visual-Director-Bot nach jeder signifikanten
Performance-Änderung aktualisiert (siehe `bots/06_visual_director.md`).*
