# Browser-Architektur

Nicht den privaten Alltagsbrowser für Bot-Automation verwenden.

## Dediziertes Profil

Lege ein eigenes Browserprofil nur für Hermes-Bot-Browserzugriffe an, z.B.:
```bash
# Chrome/Chromium Beispiel
mkdir -p ~/.mfw-browser-profile
chromium --user-data-dir=~/.mfw-browser-profile
```
Melde dich dort **einmal manuell** bei TikTok (und ggf. Google Flow o.ä.)
an, wenn ein Bot dich darum bittet. Das Profil bleibt danach persistent —
kein Bot soll wiederholt nach Login fragen.

Trage den Profilpfad in `config/settings.yaml` unter `browser_profile_dir`
ein, damit alle Bots (TikTok Analyst, Video Generator, Free Video AI Scout)
denselben persistenten Kontext nutzen.

## Regeln

- Ein Profil pro Dienst ist erlaubt, aber **keine Mehrfachaccounts** für
  denselben Dienst, um Gratislimits zu umgehen.
- Keine automatisierte CAPTCHA-Lösung.
- Keine automatisierten Zustimmungen zu Nutzungsbedingungen, die du nicht
  selbst gelesen hast — bei neuen Diensten (Free Video AI Scout) zeigt der
  Bot dir die AGB-Zusammenfassung, bevor ein Account/Login erfolgt.
- Browser-Sessions laufen headful (sichtbar) bei jeder erstmaligen
  Anmeldung an einem neuen Dienst, damit du eingreifen kannst.
