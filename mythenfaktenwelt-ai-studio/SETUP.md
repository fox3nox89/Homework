# Setup

Dieses Repo wird **nicht** in einer Cloud-Session ausgeführt. Alles hier
läuft auf deinem eigenen Rechner, wo dein TikTok-Browserprofil, deine GPU
und deine bezahlten Abos tatsächlich existieren.

## Phase 0 — Bestehendes System verstehen (auf deinem PC, nicht hier)

Führe das aus, **bevor** du irgendetwas Neues aufsetzt:

1. Suche nach vorhandenen Projekten/Skripten deines bisherigen Grok-Workflows:
   ```
   # Windows (PowerShell)
   Get-ChildItem -Recurse -Include *.py,*.json,*.yaml,*.bat,*.ps1 -ErrorAction SilentlyContinue |
     Where-Object { $_.FullName -match 'grok|tiktok|mythen' }

   # macOS/Linux
   find ~ -iname "*grok*" -o -iname "*tiktok*" -o -iname "*mythen*" 2>/dev/null
   ```
2. **Nichts davon verändern oder löschen.** Kopiere gefundene Configs nach
   `data/legacy_backup/` (in diesem Repo, aber lokal — committe keine
   Zugangsdaten, siehe `.gitignore`).
3. Trage bisherige Produktionszeiten und den Google-Drive-Zielordner in
   `config/settings.yaml` ein (Felder `schedule` und `drive_target_folder_id`).
4. Fülle `docs/channel_analysis.md` und `data/content_history.json` nur mit
   Daten, die TikTok tatsächlich anzeigt (Studio-Analytics, Video-für-Video).
   Erfinde keine Kennzahlen — wenn TikTok eine Zahl nicht zeigt, bleibt das
   Feld leer bzw. `null`.

Für den TikTok-Login: Öffne den dedizierten Browser-Profil-Ordner (siehe
`docs/BROWSER.md`), melde dich einmal manuell an. Das Profil bleibt danach
persistent, damit kein Bot dich wiederholt um Login-Übernahme bitten muss.

## Hermes Agent installieren

Quelle: offizielles Repo `NousResearch/hermes-agent` (MIT-Lizenz). Prüfe vor
der Installation die aktuelle README, falls sich seither etwas geändert hat.

**Linux / macOS / WSL2:**
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes
```

**Windows (PowerShell):**
```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

Der Installer richtet laut offizieller README u.a. Python 3.14, Node.js,
npm, ripgrep und FFmpeg ein.

Falls auf deinem Rechner bereits eine Hermes-Installation existiert:
**sichere zuerst deine bestehende Konfiguration** (typischerweise unter
`~/.hermes/` oder äquivalent), bevor du `hermes update` ausführst.

Wichtige Befehle:
- `hermes setup` — vollständiger Konfigurationsassistent
- `hermes model` — LLM-Provider/Modell wählen
- `hermes tools` — Tool-Zugriffe (Browser, Dateisystem, ...) aktivieren
- `hermes gateway` — Messaging-Anbindung (optional, für Statusmeldungen)
- `hermes doctor` — Diagnose bei Problemen

## Bot-Profile einrichten

Jede Datei in `bots/` ist ein Systemprompt für eine Hermes-Bot-Rolle.
Lege pro Datei ein persistentes Hermes-Profil an (z.B. über
`/personality` bzw. das in deiner Hermes-Version aktuelle Äquivalent —
prüfe `hermes --help` bzw. `/help` in der Session, da sich Slash-Commands
zwischen Versionen ändern können) und weise ihm den jeweiligen Prompt zu.

Reihenfolge der Einrichtung (Abhängigkeiten):
1. `16_kostenwaechter.md` und `17_watchdog.md` zuerst — sie überwachen alle
   anderen Bots von Anfang an.
2. `01_studio_chef.md` — Orchestrator.
3. Die restlichen 14 Fachbots in beliebiger Reihenfolge.

## Geplante Ausführung (3×/Tag)

Zwei gleichwertige Optionen, je nachdem was auf deinem System zuverlässiger
läuft:

**A) Hermes-eigener Cron-Scheduler** (laut README vorhanden): richte drei
Tasks ein ("morgens", "mittags", "abends" — konkrete Uhrzeiten aus deinem
bisherigen Workflow, siehe Phase 0) die jeweils
`python3 scripts/orchestrator/studio_chef.py --once` auslösen bzw. den
Studio-Chef-Bot anstossen.

**B) Systemeigener Scheduler** (Cron/Task Scheduler) als robusterer Fallback,
falls Hermes selbst nicht läuft:
```
# crontab -e (Beispielzeiten, durch deine bisherigen ersetzen)
0 7  * * * cd /pfad/zu/mythenfaktenwelt-ai-studio && python3 scripts/orchestrator/studio_chef.py --once >> data/logs/studio_chef.log 2>&1
0 13 * * * cd /pfad/zu/mythenfaktenwelt-ai-studio && python3 scripts/orchestrator/studio_chef.py --once >> data/logs/studio_chef.log 2>&1
0 19 * * * cd /pfad/zu/mythenfaktenwelt-ai-studio && python3 scripts/orchestrator/studio_chef.py --once >> data/logs/studio_chef.log 2>&1
```
Beide können parallel aktiv sein; der Studio Chef ist idempotent (prüft
`data/state/*.json` und überspringt bereits laufende/abgeschlossene Slots).

## Lokale Notfallsysteme (empfohlen, nicht zwingend für den ersten Testlauf)

Siehe `docs/LOCAL_FALLBACKS.md` für Auswahlkriterien (abhängig von deiner
GPU/Hardware) für:
- lokales Steuerungs-LLM (Orchestrierung/Watchdog)
- lokales Bildmodell
- lokales Image-to-Video-Modell
- lokale deutsche TTS

Diese sind bewusst **nicht** vorinstalliert oder fest ausgewählt — die
Auswahl hängt von der tatsächlichen Hardware deines Rechners ab, die von
hier aus nicht geprüft werden kann. `docs/LOCAL_FALLBACKS.md` beschreibt,
wie du selbst (oder ein lokaler Hermes-Bot mit Systemzugriff) die passende
Wahl triffst.

## Erster Testlauf (Trockenübung, ohne echte Provider-Calls)

```bash
cd mythenfaktenwelt-ai-studio
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config/.env.example config/.env
cp config/settings.example.yaml config/settings.yaml
cp config/providers.example.json data/provider_registry.json
cp config/quota_status.example.json data/quota_status.json
python3 -m pytest tests/ -v
python3 scripts/orchestrator/studio_chef.py --dry-run
```
Der `--dry-run`-Modus durchläuft die gesamte Pipeline mit Platzhalter-Daten,
ruft aber keine externen Provider auf und fragt keine echte Freigabe ab —
so kannst du die Zustandsmaschine prüfen, bevor echte Kosten- oder
TikTok-relevante Aktionen möglich sind.
