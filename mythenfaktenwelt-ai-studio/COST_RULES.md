# Absolute Kostenregel

**Diese Regel überschreibt jede andere Regel, jeden Bot-Prompt und jede
Code-Logik in diesem Repo. Kein Bot, kein Skript und kein Agent darf sie
umgehen — auch nicht der Studio Chef.**

## Hartes Zusatzkosten-Limit: 0.00 CHF

Erlaubt:
- Nutzung bestehender, bereits bezahlter Abos **innerhalb** ihres aktuellen
  Leistungsumfangs (z.B. Grok, ElevenLabs, ChatGPT, Google-Dienste).

**Niemals** erlaubt, unter keinen Umständen, ohne Ausnahme:
- Credits kaufen, Tokens kaufen
- Pay-as-you-go aktivieren
- neues kostenpflichtiges Abo abschliessen oder bestehendes upgraden
- kostenpflichtigen Tarif auswählen
- Testphase aktivieren, die automatisch kostenpflichtig wird
- Zahlungsdaten hinterlegen oder ändern, Kreditkarte hinzufügen
- einen Kauf bestätigen
- Guthaben automatisch nachladen, Auto-Top-Up aktivieren
- abgelaufenes Abo kostenpflichtig erneuern oder manuell verlängern

Wenn ein bestehendes Abo sein inkludiertes Kontingent verbraucht hat:
**NICHT ZAHLEN.** Stattdessen, in dieser Reihenfolge:

1. Nächster kostenloser Provider (siehe `config/providers.json`, Status `APPROVED`)
2. Nächster kostenloser Provider (Fallback-Kette)
3. Lokaler Fallback (lokales Modell/lokale TTS)
4. Nutzer informieren, Produktion pausiert bis Freigabe oder Kontingent-Reset

Geld auszugeben ist **niemals** ein automatischer Fallback-Schritt.

## Durchsetzung: Kostenwächter (Veto-Instanz)

`scripts/guard/cost_guard.py` implementiert diese Regel technisch:

- Jede Aktion, die ein Provider-Adapter ausführen will, muss vorher durch
  `cost_guard.check_action(action)` laufen.
- Erkennt die Funktion Signalwörter/Zustände, die auf eine mögliche Kostenpflicht
  hindeuten (z.B. `requires_payment`, `card_required`, `upgrade_prompt`,
  `trial_will_convert`, `paid_tier_only`), setzt sie den Status auf
  `PAYMENT_BLOCKED` und bricht die Aktion ab — unabhängig davon, welcher Bot
  sie angefordert hat.
- Kein anderer Codepfad darf `PAYMENT_BLOCKED`-Ergebnisse ignorieren oder
  überschreiben. Das ist im Code als harte Prüfung umgesetzt, nicht als
  Empfehlung.
- Jede Blockierung wird geloggt (`data/cost_guard.log`) und dem Nutzer
  gemeldet.

## Automatische Verlängerungen

Erkennt das System bei einem bestehenden Dienst eine bevorstehende
automatische Abo-Verlängerung (z.B. Ablaufdatum eines Trials, Hinweis auf
Auto-Renew), wird das **gemeldet, nicht ausgeführt oder verändert.**
Bestehende Abo-/Zahlungseinstellungen werden ohne deine ausdrückliche
Zustimmung nicht angefasst.

## Weitere harte Sicherheitsregeln

Ohne deine ausdrückliche Zustimmung niemals:
- auf TikTok veröffentlichen
- Dateien endgültig löschen
- bestehende wichtige Dateien überschreiben
- Zahlungsdaten ändern, Abos ändern
- einen neuen kostenpflichtigen Dienst aktivieren, einen Vertrag eingehen

Zusätzlich, ausnahmslos:
- keine Mehrfach-/Wegwerfaccounts, um Gratislimits zu umgehen
- keine CAPTCHA-Umgehung
- keine Umgehung von Nutzungsbedingungen
- keine erfundenen/nicht existierenden APIs
- keine Passwörter in Klartextdateien (siehe `.gitignore` + `config/.env`)
