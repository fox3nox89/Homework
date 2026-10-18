# ✂️ Video Editor

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Setzt das Video aus freigegebenen Clips, Voiceover, Musik und Untertiteln
zusammen. Nutzt lokal `scripts/editor/build_video.py` (FFmpeg-basiert) statt
proprietärer Cloud-Editoren.

## Anforderungen

- Finalformat: 1080×1920, 9:16, MP4, H.264 (oder ein aktuell TikTok-
  kompatibler, sinnvoller Codec, falls sich der Standard ändert)
- Clips niemals verzerren (Letterbox/Crop statt Stretch, siehe
  `scripts/editor/build_video.py`)
- Untertitel: gut lesbar, korrekt, TikTok-Safe-Zone beachten, synchron mit
  Voiceover (siehe `scripts/editor/subtitles.py`)
- Musiklautstärke nach Richtwert aus `docs/STYLE_BIBLE.md`

## Regeln

- Bei QC-Fehlschlag einer einzelnen Szene: nur diese Szene neu einsetzen
  und das Video neu rendern, nicht alle Szenen neu generieren lassen.
