# Scalare Genetics Core 0.1.0

En fristående svensk webbapp för lokal avelsdokumentation. Python 3.10+; inga externa paket. Windows: dubbelklicka start.bat eller öppna terminalen i mappen och kör `python app.py`. Öppna http://127.0.0.1:8765 och skapa ett konto. Mac/Linux: `python3 app.py`. Avsluta med Ctrl+C. Data sparas i data/scalare.sqlite3. Säkerhetskopiera hela data-mappen när programmet är avstängt. JSON-export finns per konto, men automatisk import saknas.

## Funktioner
Separata konton, automatiska permanenta ID per konto och posttyp, fiskar, foton, grupper, akvarier, linjer, kullar, fria avelsmål, redigerbart genbibliotek och genetiska hypoteser med evidens. Stamtavla upp till åtta led med kontroll mot cirkulära föräldrareferenser. Generationer anges av användaren; okända betecknas inte automatiskt F1. Enlokus-simulator för diploida genotyper och preliminärt parurval efter känt stamtavleöverlapp. JSON-export med bilder. Bayesfunktion finns i Pythonmodulen men inte i gränssnittet.

## Begränsningar
Detta är en första fungerande prototyp, inte en komplett produktionsklar tjänst. Automatisk bildanalys, fenotypmodell, multilokusgenetik, målstyrd optimering, sannolikhetsprofiler i gränssnittet, automatiska generationer, vetenskapligt verifierat genbibliotek, verklig inavelskoefficient och import återstår. Genbiblioteket är tomt från början för att undvika påhittade genetiska data. Parurval är endast ett informationsstöd och tar inte hänsyn till kön eller hälsa. Ingen lösenordsåterställning eller sessionsutgång. Servern ska endast användas på betrodd lokal dator; öppna den inte mot internet. Separata konton är inte ett bevis på produktionssäkerhet. Inga anspråk på vetenskaplig validering. Testa med exempeldata först.

## Test
`python -m unittest -v`.

## Desktop v0.2.0 (Windowsinriktad utvecklingsversion)
Starta `start-desktop.bat` med Python installerat. Det installerar beroenden och öppnar ett eget Tk/ttk-programfönster utan webbläsare. Data lagras normalt i `%LOCALAPPDATA%\ScalareGenetics`. För att använda tidigare webbdata, kopiera den gamla databasen `data\scalare.sqlite3` till den platsen när båda programmen är stängda och innan ny data skapas. Säkerhetskopiera först.

Bygg Windowsprogrammet på Windows med `build-windows.bat`. Det skapar `dist\ScalareGenetics\ScalareGenetics.exe` med tillhörande filer. Installera Inno Setup 6 för att även generera `Output\ScalareGeneticsSetup.exe` med `setup.iss`. Ingen färdig exe ingår; Linuxmiljön kan inte verifiera en Windowsbyggnad. Tk/ttk valdes för en testbar native prototyp istället för Qt. Bildanalys, automatisk generationsklassificering, flerspråkighet och avancerad genetisk optimering återstår. Konton separeras i appen, men den lokala databasen är inte krypterad. Säkerhetskopian innehåller samtliga konton. Återställning sker manuellt med appen stängd.

## Version 0.3.0
Nya skrivbordsfunktioner: Testkorsning beräknar tre genotyphypoteser med lika priorer och 1 % symmetriskt klassificeringsfel, under antagande om enkel dominant/recessiv nedärvning. Resultatet sparas manuellt i genetiska profiler. Generationshjälp föreslår F1, nästa F-generation eller BC-generation när användaren bekräftat släktskapet. Oberoende multilokussimulering finns i breeding.py som API, inte i gränssnittet. Genkoppling, varierande penetrans, automatisk bildanalys och källverifierat artbibliotek saknas. Ingen Windows-exe byggd; använd start-desktop.bat som tidigare. Befintligt databasformat oförändrat; ta säkerhetskopia före uppgradering.

## Version 0.4.0
Målstyrda korsningar: ange exempelvis `Dark=D/D,pb=pb/pb`. Registrera först genetiska profiler med fiskens ID i namnfältet, samma lokusnamn som i målet, en diploid genotyp och status `bekräftad` endast när underlaget räcker. Motstridiga profiler behandlas som okända. Sannolikheter förutsätter oberoende lokus. Inavelsgrad beräknas som föräldrarnas släktskapskoefficient med antagandet att okända grundare är obesläktade. Detta är inte ett bevis för faktiskt släktskap. Kontrollera fiskarnas hälsa och fertilitet. Kön som inte känns igen markeras okänt.

Windows: bygg med build-windows.bat på en Windowsdator, eller lägg innehållet i roten av ett GitHub-repo och kör arbetsflödet Windows build. Ingen färdig EXE ingår; byggprocessen är inte verifierad på Windows. Automatisk bildtolkning, källbelagt förifyllt genbibliotek, automatisk uppdatering av genetiska profiler och långsiktig flergenerationsoptimering återstår. 17 tester passerade i Linux med virtuellt skrivbord.

## v0.5.0
Ny modul Kartlägg individ: välj registrerad fisk och kull, ange testargenotyp och observerade antal. Uppdaterar en genetisk hypotes över flera kullar. Rättelse av samma kull ersätter observationen. Modellen antar oberoende avkommor, lika priorer och 1 % klassificeringsfel; använd inte resultatet som bekräftad genotyp. Testarens genotyp anges manuellt. Windowsbyggnad, bildanalys och komplett genbibliotek återstår.

## v0.6.0
Referensbibliotek med nio lokus, källänkar och validering. Ny F1/F2/BC1-simulator för kända genotyper, inklusive egna lokus. Modellen förutsätter oberoende nedärvning, slumpmässiga F1-föräldrar och lika överlevnad; den optimerar inte individurval eller förutsäger fenotyp. Bulgarian Green och andra mindre kartlagda anlag har inte förifyllts. Windowsinstallationen och bildanalys återstår.

## v0.7.0 – Visual Genetics
- Fiskar → Registrera från foto skapar ett permanent SC-ID och sparar originalbilden.
- Faderns och moderns stam och härkomstkälla är frivilliga fält; inga stamnamn behandlas som verifierade genotyper.
- Bildanalys på sparad bild: ungefärlig andel mörka/blå pixlar samt motivets höjd/bredd. Kräver jämn vit bakgrund och marginal. Inte en fiskdetektor, mätning av iridescens eller genotypklassificerare. Mätningar sparas separat per foto och bevaras vid redigering.
- Visuell korsning: välj individer eller ange ett uttryckligt Dark-scenario. Bekräftade individuella genotyper eller två registrerade föräldrars bekräftade genotyper används; okänd genetik ger ingen påhittad sannolikhet. Osäkra föräldragenotyper antas oberoende; släktskap kan bryta detta antagande.
- Tre AI-genererade referensillustrationer för enkel D/+ modell, vit bakgrund och vänstervänd sidovy. Inga bilder för ej modellerade allelkombinationer. Bilderna är inte foton av faktisk avkomma. Andra lokus och miljö kan ändra fenotypen.
- Befintliga lokala data används utan schemaändring av SQLite-tabellerna. Säkerhetskopiera före uppgradering.
- Windows EXE ej byggd/testad här; byggskript uppdaterade för bildresurser.
- 32 automatiserade tester godkända i Linux med virtuell bildskärm, inklusive navigationsgrundtest. Ingen validering mot verkliga fiskpopulationer.

## v0.8.0 – villkorad flerlokussimulering
Ny meny Flera genlokus: ange kända eller antagna genotyper för två föräldrar, valfri målgenotyp och kullstorlek. Visar kombinationer, målmatch, F1/F2/BC1 och chans till minst en målgenotyp i F1. Oberoende lokus och lika överlevnad antas. Fenotypetiketter är partiella hypoteser, inte säkra klassificeringar. Den gamla bildsimulatorn bevaras; nya kombinationer saknar ännu bildrendering. Bulgarian Green och Paraiba är inte modellerade. Ingen ny automatisk bildklassificering eller Windows-EXE i denna version.

## v0.9.0
Välj en rad i flerlokussimulatorn för en illustrativ bild av Dark + Philippine Blue. Blå färg är en schematisk överlagring, inte en validerad prognos om verklig fenotyp. Ögonregionens röda pixlar kan analyseras i programkärnan med manuellt valda normaliserade koordinater; ännu inget gränssnitt för detta. Övriga kombinationer saknar bildmodell. Windowsinstallationen är ännu inte verifierad.

## v0.10.0
Härkomst & testval: ange sannolikhetsvikter för föräldrarnas genotyper vid ett lokus. Programmet beräknar avkommans genotypfördelning och rangordnar angivna testgenotyper efter förväntad informationsvinst per klassificerad avkomma. Resultatet är villkorat på användarens fenotypregel, oberoende föräldraprofiler och lika överlevnad. Stamnamn används inte som genetiska bevis. Modellen är ännu inte kopplad till sparade individprofiler; värden matas in manuellt. Ingen ny bildmodell eller Windows-EXE ingår.

## v0.11.0 – Integrated breeding planner
Öppna **Genetiskt pass & avelsplan**. Välj ett sparat mål eller ange målgenotyper, kullstorlek och högsta beräknade inavelsgrad. Ange `ja` i akvarieregistrets nya fält för lediga avelsakvarier. Endast akvarier utan registrerade fiskar föreslås. Genetiska pass bygger på bekräftade uppgifter, befintlig testkorsningsmodell eller härkomst från entydiga föräldraprofiler. Motstridiga bekräftelser ger okänd profil. Stamnamn och bilder är inte genotypbevis. Prognoser antar oberoende lokus och föräldraprofiler; för besläktade föräldrar med osäkra profiler avstår modellen från sannolikhet. Kullsannolikhet beräknas endast vid entydiga föräldraprofiler. Okänd härkomst kan underskatta inavel. Fördelningen av akvarier är en enkel girig heuristik, inte optimal schemaläggning eller kapacitetskontroll. Planen är rådgivande och kan exporteras som text. Befintliga databaser behålls; nya registerfält ligger i JSON. Säkerhetskopiera före uppdatering.

Windowsinstallation, validerad bildklassificering, fullständigt genbibliotek, flerspråkighet och långsiktig flergenerationsoptimering återstår.

## v0.12.0 – Flergenerationsurval

Ny meny: F1–F10 urvalsplan. Ange kända föräldragenotyper, målgenotyper, antal generationer och bedömda avkommor per kull. Programmet undersöker upp till fyra oberoende lokus och redovisar en begränsad sökning över hypotetiska urvalsvägar. För varje generation visas målsannolikheten per avkomma samt en konservativ sannolikhetsgräns för att kunna hitta de nödvändiga genotyperna längs den valda vägen. Gränsen använder separata delar av varje kull för att säkerställa två olika individer vid urval. Den är inte sannolikheten för praktisk avelsframgång: kön, fertilitet, hälsa, släktskap, genkoppling och överlevnad ingår inte. Syskonurval är en matematisk modell, inte en rekommendation att genomföra inavel. Tidigare separata avelsplaner med inavelskontroll kvarstår. Cirkulära stamtavlor avvisas innan inavelsberäkning. Windowsbyggskript ingår men EXE är inte byggd eller verifierad.

## v0.13.0 – Release preparation

Windows: packa upp och kör start-desktop.bat med Python 3 installerat. Skriptet skapar en lokal virtuell miljö och installerar Pillow om det behövs. Därefter körs appen lokalt. Bygg Windows-EXE och Inno Setup-installation med build-windows.bat på Windows; dessa binärer har inte byggts eller verifierats här.

Ny kontoexport i JSON inklusive foton, utan lösenord. Hela databasen kan säkerhetskopieras och återställas med integritetskontroll och separat kopia av föregående databas. Stäng andra instanser före återställning. Lokala konton är inte ett skydd mot andra personer med filåtkomst på datorn. JSON-exporten är avsedd för dataåtkomst, inte återimport.

Bildanalys: markera ögonområdet själv för en lokal rödhetsmätning. Mätningen sparas separat från genetiska bevis. Enlokuskullprognos för obesläktade föräldrar med osäkra genotyper väger nu samman villkorade kullutfall, istället för att anta oberoende marginalutfall mellan syskon. Förutsätter oberoende föräldraprofiler och lika överlevnad. Okänd släkthistorik kan ge missvisande låg inavelsgrad.

Kvar före kommersiell 1.0: verifierad Windowsinstallation, licensgranskning inklusive bilder, fullständig översättning, validerad automatisk fenotypklassificering, mer kompletta genetiska modeller inklusive Bulgarian Green och Paraiba, användartester och fullständig säkerhetsgranskning. Detta är inte en kommersiellt färdig produkt.
