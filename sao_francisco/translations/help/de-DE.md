# São Francisco – Hilfe

São Francisco wandelt Audio und Video in Text um. Wählen Sie eine Datei auf Ihrem Computer oder fügen Sie eine öffentliche Videoadresse ein. Die Oberfläche startet auf Englisch; unter **Einstellungen → Oberflächensprache** können Sie sie ändern. Die Sprache Ihrer Aufnahmen bleibt davon unberührt.

## Erste Schritte

Beginnen Sie mit einer kurzen Aufnahme:

1. Öffnen Sie **Einstellungen** und hinterlegen Sie einen API-Schlüssel für OpenAI oder Gemini.
2. Kehren Sie zu **Transkribieren** zurück.
3. Wählen Sie eine Datei oder fügen Sie eine Videoadresse ein.
4. Wählen Sie Dienst und Modell.
5. Markieren Sie die gewünschten Ausgabeformate.
6. Wählen Sie den Zielordner.
7. Klicken Sie auf **Transkription starten**.

Die fertigen Dateien liegen im gewählten Ordner und lassen sich auch im **Verlauf** öffnen.

## Dateien, Videos oder URLs hinzufügen

Unter **Dateien** wählen Sie eine oder mehrere Audio- oder Videodateien. Gängige Formate wie MP3, WAV, M4A, MP4, MOV, MKV und WebM werden unterstützt.

Unter **YouTube oder URL** fügen Sie die öffentliche Videoadresse ein. Inhalte mit Anmeldung, Abonnement, Zahlung oder besonderer Genehmigung können nicht verfügbar sein.

Um den zum Video veröffentlichten Text zu verwenden, aktivieren Sie **Verfügbare Videountertitel verwenden**. São Francisco entfernt fortschreitende Wiederholungen vor der Dokumenterstellung. Die Option ist standardmäßig aus; lassen Sie sie aus, wenn Sie eine neue Audiotranskription wünschen.

Ein online erreichbares Video ist nicht automatisch frei nutzbar. Transkribieren Sie nur Material, zu dessen Nutzung Sie berechtigt sind oder eine Erlaubnis haben.

### Sprache erkennen

**Automatisch erkennen** lässt den Dienst die gesprochene Sprache bestimmen. Sie können sie auch selbst angeben. Keine Option ist immer besser: Eine Angabe kann bei Rauschen, Akzenten, Namen und ähnlichen Sprachen helfen; die Erkennung eignet sich für unbekannte oder gemischte Sprachen. Dies ist nicht die Oberflächensprache.

## Modell auswählen

Die Namen beschreiben den empfohlenen Einsatz:

- **Sparsam — OpenAI:** guter Einstieg für Fließtext.
- **Höhere Genauigkeit — OpenAI:** priorisiert Namen und Wortschatz.
- **Sprecher erkennen — OpenAI:** unterscheidet Teilnehmer, soweit möglich.
- **Untertitel und Zeitmarken — OpenAI:** bietet präzisere Zeitmarken.
- **Gemini detailliert:** erstellt eine strukturierte Transkription.
- **Gemini sparsam:** Alternative für größere Mengen.

Die Qualität hängt von der Aufnahme ab. Rauschen, laute Musik, überlappende Stimmen, entfernte Mikrofone und ungewöhnliche Namen können eine Nachprüfung erfordern. Modelle und Verfügbarkeit können sich je nach Dienst ändern.

## Schlüssel für OpenAI und Gemini

Ein API-Schlüssel ist ein geheimer Zugangsschlüssel, mit dem São Francisco Audio an den gewählten Dienst senden kann. Zum Erstellen sind keine Entwicklerkenntnisse erforderlich.

Ein Chatbot-Abonnement und API-Nutzung sind getrennte Leistungen. ChatGPT Plus enthält beispielsweise nicht automatisch OpenAI-API-Guthaben. Jeder Anbieter verwaltet Abrechnung, Limits und Modellzugang selbst.

São Francisco speichert Schlüssel im sicheren Schlüsselspeicher des Systems und zeigt sie nicht erneut vollständig an.

### OpenAI-Schlüssel erstellen

1. Öffnen Sie die [offizielle OpenAI-Schlüsselseite](https://platform.openai.com/api-keys).
2. Melden Sie sich an oder erstellen Sie ein Konto.
3. Erstellen Sie einen Schlüssel für das gewünschte Projekt.
4. Kopieren Sie ihn, sobald er erscheint.
5. Fügen Sie ihn unter **Einstellungen → OpenAI** ein.
6. Wählen Sie **Prüfen**, dann **Einstellungen speichern**.

Auch einem gültigen Schlüssel können Guthaben, Kontingent oder Modellzugriff fehlen. Prüfen Sie Abrechnung und Limits bei OpenAI.

### Gemini-Schlüssel erstellen

1. Öffnen Sie die [offizielle Gemini-Schlüsselseite](https://ai.google.dev/gemini-api/docs/api-key).
2. Melden Sie sich bei Google AI Studio an.
3. Wählen Sie ein Projekt und erstellen Sie einen Schlüssel.
4. Fügen Sie ihn unter **Einstellungen → Gemini** ein.
5. Wählen Sie **Prüfen**, dann **Einstellungen speichern**.

> [!WARNING]
> Teilen Sie Schlüssel niemals in Dokumenten, Screenshots, Nachrichten oder Supportanfragen. Widerrufen Sie offengelegte Schlüssel und erstellen Sie neue.

## Verarbeitung langer Medien

São Francisco bereitet lange Videos in kleineren Teilen vor und fügt sie zu einer Transkription zusammen, ohne das ganze Video auf einmal zu senden.

Abgeschlossene Teile werden gespeichert. Nach einer Unterbrechung können Sie im **Verlauf** fortsetzen, ohne alles neu zu beginnen. Die Dauer hängt von Aufnahme, Internetgeschwindigkeit und Dienstverfügbarkeit ab.

## Verfolgen, abbrechen und fortsetzen

Der Bildschirm zeigt Fortschritt und aktuellen Teil an.

**Abbrechen** ändert die Karte auf **Wird abgebrochen** und beendet die Ausführung innerhalb von etwa fünf Sekunden. Fertige Teile und Dateien bleiben verfügbar. Eine bereits beim Dienst eingegangene Anfrage kann auch nach dem Abbruch abgeschlossen oder berechnet werden.

**Fortsetzen** führt eine unterbrochene Aufgabe weiter. Änderungen an Quelldatei, Dienst, Modell oder Transkriptionssprache erfordern eine neue Aufgabe. Ist das Ergebnis einer früheren Anfrage unklar, warnt die App vor einer neuen Anfrage, da erneut Kosten entstehen können.

## Ausgabeformate

- **TXT:** einfacher Text zum Lesen und Durchsuchen.
- **DOCX:** formatiertes Dokument für Textverarbeitungen.
- **SRT:** Untertitel für Videoplayer und Schnittprogramme.
- **VTT:** vor allem im Web verwendete Untertitel.

Zeitmarken in DOCX und TXT sind optional und standardmäßig aus. Aktivieren Sie vor dem Start **Zeitmarken in DOCX und TXT einfügen**. SRT und VTT benötigen immer Zeitangaben. Liefert das Modell keine genauen Zeiten, können Anpassungen im Schnittprogramm nötig sein.

Bei Onlinevideos wird der Videotitel, falls nötig angepasst, als Dateiname verwendet. Existiert der Name bereits, erhält das neue Ergebnis eine Nummer.

### Mit KI verbessern

Aktivieren Sie **Mit KI verbessern**, um zusätzlich zum Original eine besser lesbare zweite Version zu erhalten. Die App gliedert Absätze und korrigiert Zeichensetzung, Großschreibung und offensichtliche Erkennungsfehler.

Die Verbesserung soll nicht zusammenfassen, übersetzen, ausschmücken oder unklare Stellen ergänzen. Prüfen Sie dennoch insbesondere Namen, Zahlen und unklare Passagen.

DOCX und TXT erhalten getrennte Dateien für **Transkription** und **verbesserten Text**. Zeitmarken bleiben nur im Original. SRT und VTT werden nicht umgeschrieben.

Zuerst wird das Original fertiggestellt, gespeichert und exportiert; danach erzeugt die optionale Verbesserung zusätzliche Dateien. Bei Unterbrechung bleiben die Originale erhalten. Die Fortsetzung verwendet akzeptierte Schritte erneut und wiederholt keine Anfrage mit unklarem Ergebnis automatisch.

## Kosten, Daten und Speicherung

App-Kauf und API-Nutzung sind getrennt. São Francisco berechnet keine einzelnen Transkriptionen. API-Gebühren erhebt OpenAI oder Google direkt nach Konto und Modell; der App-Kauf enthält kein API-Guthaben.

Jeder gesendete Teil kann Kontingent verbrauchen. Beim Fortsetzen wird fertige Arbeit wiederverwendet. Bei ausreichenden Daten erscheint eine Kostenschätzung in US-Dollar. Kleine Beträge erscheinen als **unter 0,01 US$**. Bei vollständig aus vorhandenen Untertiteln erzeugtem Text ohne Verbesserung erscheint **Keine API-Kosten**.

Es handelt sich nur um eine Schätzung. Kostenlose Tarife, Steuern, Rabatte, unterbrochene Versuche und Preisänderungen können zu abweichenden Beträgen führen. Maßgeblich sind die [OpenAI-Nutzung](https://platform.openai.com/usage) oder [Google-Cloud-Abrechnung](https://console.cloud.google.com/billing).

Meldet der Dienst verlässliche Zahlen, kann die App Tokens anzeigen: kleine Einheiten zur Messung von Eingabe und Antwort. Nicht gemeldete Tokenzahlen werden nicht erfunden.

### Aktuelle API-Preise

Prüfen Sie die offiziellen [OpenAI-Preise](https://developers.openai.com/api/docs/pricing) und [Gemini-Preise](https://ai.google.dev/gemini-api/docs/pricing). Preise, Einheiten, Modelle und kostenlose Kontingente können sich ändern. Prüfen Sie sie vor kostenpflichtiger Arbeit.

Audio wird an den gewählten Dienst gesendet. Verlauf und Arbeitsdateien bleiben auf Ihrem Computer. Ergebnisse bleiben bis zur Löschung im Zielordner. Beachten Sie die [OpenAI-Bedingungen](https://openai.com/policies) und [Gemini-API-Bedingungen](https://ai.google.dev/gemini-api/terms).

## Häufige Probleme

### Schlüssel nicht akzeptiert

**Symptom:** Einstellungen melden einen ungültigen Schlüssel. **Maßnahme:** Anbieter, vollständige Kopie und Aktivität prüfen, dann Abrechnung, Limits und Modellzugang.

### Datei ohne Audio

**Symptom:** Die Aufgabe endet vor der Transkription. **Maßnahme:** Datei öffnen und Ton prüfen. Beschädigte Dateien oder reine Bildvideos können nicht transkribiert werden.

### Videoadresse funktioniert nicht mehr

**Symptom:** Das Video lässt sich nicht abrufen. **Maßnahme:** São Francisco aktualisieren und erneut versuchen. Anmeldepflichtige, bezahlte, live übertragene oder gesperrte Inhalte können weiterhin nicht verfügbar sein.

### Verarbeitung scheint zu hängen

**Symptom:** Derselbe Teil bleibt mehrere Minuten aktiv. **Maßnahme:** Lange Aufnahmen und ausgelastete Dienste benötigen Zeit. Bei Netzwerk- oder Kontingentmeldungen abbrechen und später fortsetzen.

### Untertitel sind nicht synchron

**Symptom:** SRT oder VTT erscheint vor oder nach dem gesprochenen Text. **Maßnahme:** **Untertitel und Zeitmarken** verwenden und mit dem Video prüfen.

### Kein Speicherplatz

**Symptom:** Vorbereitung oder Dateierstellung stoppt. **Maßnahme:** Speicherplatz freigeben und erneut versuchen.

## Tastenkürzel und Navigation

- `⌘N` unter macOS oder sonst `Ctrl+N` öffnet **Transkribieren**.
- `⌘K` oder `Ctrl+K` öffnet die **Hilfe**.
- `⌘,` oder `Ctrl+,` öffnet **Einstellungen**.
- `Tab` und `Shift+Tab` verschieben den Fokus.
- `Enter` oder `Leertaste` aktiviert das fokussierte Element.
- `Page Up`, `Page Down`, `Home` und `End` bewegen durch lange Texte.
- `Esc` schließt Hinweisfenster.

Inhaltsverzeichnis und Hilfeartikel lassen sich unabhängig scrollen.

## Lizenzen und Über

Der Code von São Francisco steht unter der MIT-Lizenz. Der Verkauf fertig gepackter Downloads hebt deren Freiheiten nicht auf. Komponenten, Bibliotheken und Schriftarten behalten ihre eigenen Lizenzen. Unter **Über → Hinweise zu Drittanbietern anzeigen** finden Sie das Inventar.
