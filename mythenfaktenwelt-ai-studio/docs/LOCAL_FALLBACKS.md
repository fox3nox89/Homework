# Lokale Notfallsysteme — Auswahlkriterien

Ein rein cloudbasiertes System kann nie garantieren, immer verfügbar zu
sein. Diese Datei beschreibt **wie** die passenden lokalen Fallbacks
ausgewählt werden — nicht, welche konkret installiert werden, weil das von
der tatsächlichen Hardware deines Rechners abhängt, die von der Cloud-Session
aus, in der dieses Repo entstand, nicht geprüft werden konnte.

Führe diese Prüfung einmalig lokal aus (Hermes-Bot mit Systemzugriff oder
manuell) und trage das Ergebnis in `config/settings.yaml` unter
`local_fallbacks:` ein.

## 1. Lokales Steuerungs-LLM

Zweck: Orchestrierung, Dateiüberwachung, Providerwechsel, Statusprüfung,
einfache Tool-Aufrufe, Watchdog — **nicht** die kreative Hauptarbeit.

Prüfschritte:
```bash
nvidia-smi --query-gpu=name,memory.total --format=csv   # GPU-VRAM ermitteln
ollama list                                              # falls Ollama vorhanden
```
Auswahlkriterium: ein aktuelles Modell, das
(a) zuverlässiges Tool-/Function-Calling unterstützt,
(b) auf der vorhandenen GPU/CPU in vertretbarer Zeit läuft (Faustregel:
Modellgrösse in GB ungefähr ≤ verfügbarer VRAM),
(c) von Hermes als lokaler Modell-Provider angebunden werden kann
(`hermes model` listet konfigurierte Provider — prüfe dort, ob ein
Ollama-/llama.cpp-/vLLM-Endpoint als Option erscheint).
Trage das gewählte Modell inkl. Testdatum in `config/settings.yaml` ein.
Keine Modellnamen oder Benchmarks hier vorab festlegen — sie veralten
schneller als dieses Repo gepflegt wird.

## 2. Lokales Bildmodell (optional)

Nur vorbereiten, falls Cloud-Bildgeneratoren ausfallen. Prüfkriterien:
9:16-taugliche Auflösung, Laufzeit pro Bild auf vorhandener GPU, Lizenz für
kommerzielle Nutzung (TikTok-Veröffentlichung zählt als solche).

## 3. Lokales Image-to-Video

Kandidaten, die aktuell zu prüfen sind (nicht blind installieren — jedes
Modell hat unterschiedliche VRAM-Anforderungen und Lizenzbedingungen, die
sich ändern können):
- LTX-Video
- Wan
- HunyuanVideo
- ggf. neuere Modelle zum Prüfzeitpunkt

Prüfe pro Kandidat:
1. Minimale VRAM-Anforderung vs. vorhandene GPU
2. Lizenz (kommerzielle Nutzung erlaubt?)
3. Native 9:16-Unterstützung oder Nachbearbeitung nötig?
4. Tatsächliche Generierungszeit auf deiner Hardware (Testlauf, kein
   Herstellerversprechen übernehmen)

Ergebnis in `config/providers.example.json` als Eintrag mit
`"type": "local"` und Status `CANDIDATE`/`APPROVED` nach Test eintragen.

## 4. Lokale deutsche TTS

Mindestens eine brauchbare lokale deutsche Ersatzstimme vorbereiten, für
den Fall, dass ElevenLabs-Kontingent erschöpft ist. Kandidaten, die zum
Prüfzeitpunkt zu testen sind (z.B. Piper, Coqui TTS, oder aktuellere
Alternativen) — mehrere testen, beste geeignete Stimme auswählen:

Anforderungen:
- gutes Deutsch, natürliche Aussprache
- möglichst konsistente Stimme über mehrere Generierungen
- ausreichend gute Audioqualität für TikTok
- Lizenz für den vorgesehenen Einsatz geeignet
- **keine Stimme einer realen Person ohne deren Berechtigung klonen**

Das Testergebnis (gewähltes Modell + Stimme) wird als `FALLBACK_VOICE` in
`config/settings.yaml` gespeichert und von `scripts/router/provider_router.py`
verwendet, wenn ElevenLabs `LIMIT` oder `UNKNOWN` meldet.
