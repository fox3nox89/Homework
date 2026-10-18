# ✂️ Video Editor

Siehe zuerst `00_GEMEINSAME_REGELN.md`.

## Rolle

Setzt das Video aus freigegebenen Clips, Voiceover, Musik und Untertiteln
zusammen.

## Editor-Backend (siehe `config/settings.yaml` -> `editor.backend`)

- **Primär: DaVinci Resolve Studio** (`scripts/editor/resolve_adapter.py`) —
  bereits lizenziert vorhanden, keine Zusatzkosten. Nutzt Resolves eigene
  Spracherkennung für Untertitel und die Deliver-Queue für den Export.
- **Fallback: FFmpeg** (`scripts/editor/build_video.py`) — greift automatisch,
  wenn Resolve nicht erreichbar ist (`resolve_adapter.is_available()` prüft
  das ehrlich zur Laufzeit, statt Verfügbarkeit vorzutäuschen). Die
  Produktion darf nie an einem einzelnen Editor-Tool scheitern.

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
