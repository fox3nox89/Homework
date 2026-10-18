# Providers — Übersicht

> Wird vom Free-Video-AI-Scout-Bot gepflegt. Maschinenlesbare Quelle der
> Wahrheit ist `data/provider_registry.json` — diese Datei ist die
> menschenlesbare Zusammenfassung davon. Bei Widerspruch gilt die JSON-Datei.

## Status-Bedeutung

- `APPROVED` — live getestet, erfüllt Pflichtkriterien (siehe unten), aktuell
  nutzbar innerhalb bestehender Abos oder echter Gratis-Kontingente.
- `CANDIDATE` — gefunden, aber noch nicht ausreichend verifiziert (kein
  Standardtest durchgeführt, oder Testergebnis widersprüchlich).
- `REJECTED` — getestet und ungeeignet (z.B. kein echtes 9:16, Zwangs-
  Wasserzeichen, kein tatsächliches Gratiskontingent, TOS verbietet
  Automatisierung).

## Pflichtkriterien für `APPROVED` (Image-to-Video-Provider)

1. Unterstützt Image-to-Video
2. Echtes 9:16 (nicht nur zugeschnitten/verzerrt)
3. Mindestens TikTok-taugliche Qualität
4. Kostenlos oder echtes, wiederkehrendes Gratis-Kontingent
5. Kein Zwangs-Wasserzeichen (oder entfernbar innerhalb der Gratis-Nutzung)
6. Kommerzielle Nutzung durch die Lizenz/AGB gedeckt
7. Automatisierbar ohne TOS-Verstoss (API bevorzugt; Browser-Automation nur,
   wenn die AGB das nicht ausschliessen)

## Aktuelle Registry (Auszug — Platzhalter, siehe `data/provider_registry.json`)

| Provider | Typ | Status | 9:16 | Wasserzeichen | Kontingent | Zuletzt geprüft |
|---|---|---|---|---|---|---|
| Grok (bestehendes Abo) | Cloud, Image+Video | `CANDIDATE` | zu prüfen | zu prüfen | im Abo enthalten | _(noch nicht geprüft)_ |
| _(vom Scout einzutragen)_ | | | | | | |

**Kein Eintrag in dieser Tabelle darf ohne einen tatsächlich durchgeführten
Test (oder ausreichende offizielle Dokumentation) auf `APPROVED` gesetzt
werden.** Marketingtext allein reicht nicht.
