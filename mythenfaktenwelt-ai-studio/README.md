# MythenFaktenWelt AI Studio

Autonomes (aber freigabepflichtiges) Produktionssystem für den TikTok-Kanal
**MythenFaktenWelt**, orchestriert über [Hermes Agent](https://github.com/NousResearch/hermes-agent)
von Nous Research.

## Was dieses System ist

Ein Satz von Hermes-Bot-Profilen (`bots/`), Datenschemata (`config/`, `data/`)
und lokalen Skripten (`scripts/`), die zusammen den bestehenden manuellen
Workflow nachbilden und robuster machen:

Themen-Scout → Faktenchecker → Skript-Autor → Visual Director →
Image Generator → Video Generator (Provider-Router) → Voice Agent →
Music Agent → Video Editor → Quality Control → Publishing Optimizer →
Google Drive Upload → **Freigabe durch dich** → (erst dann) Veröffentlichung.

## Was dieses System NICHT tut

- Es veröffentlicht **niemals** ohne deine ausdrückliche Freigabe auf TikTok.
- Es gibt **niemals** Geld aus. Siehe [`COST_RULES.md`](COST_RULES.md) — das ist
  die oberste Regel und überschreibt alles andere in diesem Repo.
- Es läuft **nicht** in der Cloud-Sandbox, in der dieses Repo erstellt wurde.
  Hermes Desktop, dein TikTok-Browserprofil, deine GPU und deine bezahlten
  Abos (Grok, ElevenLabs, ...) existieren nur auf deinem eigenen Rechner.
  Dieses Repo ist der Bauplan; ausgeführt wird es lokal.

## Ausgangslage (ehrlich, Stand dieses Commits)

- Auf dem Rechner, auf dem dieses Repo erstellt wurde (eine isolierte
  Cloud-Session), gab es **keine** Spuren eines bestehenden Grok-/TikTok-
  Workflows. Falls auf deinem eigentlichen PC bereits Skripte, Configs oder
  ein Google-Drive-Zielordner für den alten Workflow existieren, findest du
  in [`SETUP.md`](SETUP.md) unter Phase 0 eine Anleitung, wie du sie einliest
  und referenzierst, bevor irgendetwas geändert wird.
- Alle Provider-Angaben (Kontingente, Wasserzeichen, Preise) in diesem Repo
  sind **Platzhalter/Vorlagen**. Sie müssen von deinem lokalen System live
  geprüft werden (`scripts/scout/free_video_ai_scout.py`), bevor der
  Provider-Router sie als `APPROVED` einstuft. Nichts davon wurde hier
  erfunden oder als Fakt behauptet.

## Schnellstart

1. Lies [`SETUP.md`](SETUP.md) — Phase 0, dann Hermes-Installation.
2. Kopiere `config/.env.example` nach `config/.env` und trage vorhandene
   API-Keys/Zugänge ein (niemals ins Repo committen, siehe `.gitignore`).
3. Kopiere `config/settings.example.yaml` nach `config/settings.yaml` und
   trage deinen Google-Drive-Zielordner, Kanalnamen und Produktionszeiten ein.
4. Starte den Studio Chef: `python3 scripts/orchestrator/studio_chef.py --once`
   für einen Testlauf, danach per Cron/Hermes-Scheduler 3×/Tag.
5. Jedes fertige Video landet auf Google Drive **plus** einer Freigabeanfrage
   an dich. Ohne dein "JA" bleibt der Status `AWAITING_APPROVAL`.

## Repo-Struktur

```
bots/            Systemprompts/Rollen für jeden Hermes-Bot (17 Rollen)
config/          Vorlagen für Settings, Provider-Registry, Cost-Guard-Policy
data/            Laufzeitdaten: Themen-DB, Fakten, Fehler-Gedächtnis, Quoten
scripts/         Ausführbare Python-Skripte (Orchestrator, Router, Guard, Editor, ...)
docs/            STYLE_BIBLE, PROVIDERS, channel_analysis (werden vom System befüllt)
tests/           Unit-Tests für Cost-Guard, Router, Quota-Manager
```

Siehe [`SETUP.md`](SETUP.md) für die vollständige Installationsanleitung und
[`COST_RULES.md`](COST_RULES.md) für die harte 0-CHF-Regel.
