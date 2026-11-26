# Windowsbygge v0.14.0
Detta är källkod för en byggmiljö, inte ett installerbart Windowsprogram.
Demoläget öppnas från inloggningsfönstret. Fiktiva data och bilder lagras i en separat tillfällig databas. Återställning är avstängd i demoläget.

## Bygg på GitHub
Lägg samtliga filer inklusive .github/workflows/windows.yml i roten på ett GitHub-repository. Öppna Actions, välj Windows installer och Run workflow. Efter en godkänd körning hämtas ScalareGenetics-Windows under Artifacts. Den innehåller ScalareGeneticsSetup.exe och SHA256.txt. Körningen bygger, installerar och utför ett automatiskt starttest. Ingen separat Pythoninstallation krävs hos slutanvändaren. Installationsfilen är inte kodsignerad. Windows kan därför visa en varning; stäng inte av säkerhetsfunktioner för att kringgå den.

Denna byggprocess har inte körts på Windows i den aktuella utvecklingsmiljön. 65 lokala tester samt ett separat starttest har körts på Linux. Windowskompatibilitet är ännu inte verifierad.
