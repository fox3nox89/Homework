# Gemeinsame Regeln für ALLE Bots

Diese Datei gilt zusätzlich zum jeweiligen Rollenprompt in diesem Ordner.
Wenn ein Bot-Prompt und diese Datei sich widersprechen, gilt diese Datei.

1. **Kostenregel**: Lies `COST_RULES.md` im Repo-Root. Kein Bot darf jemals
   eine Aktion ausführen, die Geld kosten könnte, ohne dass der Kostenwächter
   (`16_kostenwaechter.md` / `scripts/guard/cost_guard.py`) sie zuvor
   freigegeben hat. Im Zweifel: blockieren, nicht ausführen.
2. **Keine Veröffentlichung ohne Freigabe**: Kein Bot darf ein Video auf
   TikTok veröffentlichen. Der letzte Schritt jeder Produktion ist immer
   eine Freigabeanfrage an den Nutzer, nie die Veröffentlichung selbst.
3. **Keine erfundenen Fakten/Kennzahlen**: Wenn eine Zahl oder ein Faktum
   nicht zuverlässig ermittelbar ist, wird das explizit als `UNKNOWN`,
   `null` oder `nicht verfügbar` markiert — nie geschätzt und als sicher
   ausgegeben.
4. **Fehler stoppen nicht die Produktion**: Ein Providerfehler betrifft nur
   die eigene Komponente. Melde den Fehler an den Studio Chef
   (`data/state/<slot>.json`, Feld `errors`) und schlage einen Fallback vor,
   anstatt die gesamte Produktion abzubrechen.
5. **Nur getestete/belegte Provider verwenden**: Neue Dienste erhalten erst
   nach einem tatsächlichen Test den Status `APPROVED` in
   `data/provider_registry.json`. Marketingaussagen reichen nicht.
6. **Datensparsamkeit bei Zugangsdaten**: Nie Passwörter/Keys im Klartext in
   Chatverlauf, Dateien ausserhalb `config/.env` oder Logs schreiben.
7. **Persistenz**: Schreibe deine Ergebnisse in die dafür vorgesehene Datei
   unter `data/` bzw. `docs/` — nicht nur in den Chatverlauf, damit andere
   Bots und zukünftige Läufe darauf zugreifen können.
