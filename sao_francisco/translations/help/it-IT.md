# Guida di São Francisco

São Francisco trasforma audio e video in testo. Scegli un file sul computer o incolla l’indirizzo pubblico di un video. L’interfaccia parte in inglese; cambiala in **Impostazioni → Lingua dell’interfaccia** senza modificare la lingua delle registrazioni.

## Primi passi

Inizia con una registrazione breve:

1. Apri **Impostazioni** e aggiungi una chiave API OpenAI o Gemini.
2. Torna a **Trascrivi**.
3. Scegli un file o incolla un indirizzo video.
4. Seleziona servizio e modello.
5. Seleziona i formati di uscita.
6. Scegli la cartella di destinazione.
7. Premi **Avvia trascrizione**.

I file completati saranno nella cartella scelta. Puoi aprirli anche dalla **Cronologia**.

## Aggiungere file, video o indirizzi

In **File**, seleziona uno o più file audio o video. Sono supportati formati comuni come MP3, WAV, M4A, MP4, MOV, MKV e WebM.

In **YouTube o indirizzo**, incolla l’indirizzo pubblico del video. Contenuti che richiedono accesso, abbonamento, pagamento o autorizzazioni particolari potrebbero non essere disponibili.

Per riutilizzare il testo pubblicato con il video, seleziona **Usa i sottotitoli disponibili del video**. São Francisco elimina le ripetizioni progressive prima di creare il documento. L’opzione è disattivata per impostazione predefinita; lasciala così se preferisci una nuova trascrizione dell’audio.

Un video accessibile online non è necessariamente libero da utilizzare. Trascrivi solo materiale che hai il diritto o l’autorizzazione di usare.

### Rilevare la lingua

**Rileva automaticamente** lascia al servizio il riconoscimento della lingua parlata. Puoi anche specificarla. Nessuna scelta è sempre migliore: indicare la lingua può aiutare con rumore, accenti, nomi e lingue simili; il rilevamento è utile con lingue sconosciute o mescolate. È un’impostazione distinta dalla lingua dell’interfaccia.

## Scegliere un modello

I nomi indicano l’uso consigliato:

- **Economico — OpenAI:** buon punto di partenza per testo continuo.
- **Maggiore precisione — OpenAI:** privilegia nomi e vocabolario.
- **Identifica parlanti — OpenAI:** separa i partecipanti quando possibile.
- **Sottotitoli e tempi — OpenAI:** fornisce marcature temporali più precise.
- **Gemini dettagliato:** produce una trascrizione strutturata.
- **Gemini economico:** alternativa per grandi volumi.

La qualità dipende dalla registrazione. Rumore, musica alta, voci sovrapposte, microfoni lontani e nomi insoliti possono richiedere una revisione. Modelli e disponibilità possono cambiare secondo il servizio.

## Chiavi OpenAI e Gemini

Una chiave API è una credenziale segreta che consente a São Francisco di inviare l’audio al servizio scelto. Non occorre essere sviluppatori per crearla.

L’abbonamento a un chatbot e l’uso delle API sono servizi separati. Ad esempio, ChatGPT Plus non include automaticamente crediti API OpenAI. Ogni fornitore gestisce fatturazione, limiti e accesso ai modelli sulla propria piattaforma.

São Francisco conserva le chiavi nell’archivio sicuro del sistema e non le mostra più per intero.

### Creare una chiave OpenAI

1. Apri la [pagina ufficiale delle chiavi OpenAI](https://platform.openai.com/api-keys).
2. Accedi o crea un account.
3. Crea una chiave per il progetto desiderato.
4. Copiala quando appare.
5. Incollala in **Impostazioni → OpenAI** di São Francisco.
6. Scegli **Verifica**, poi **Salva impostazioni**.

Una chiave valida può non avere credito, quota o accesso al modello. Controlla fatturazione e limiti sulla piattaforma OpenAI.

### Creare una chiave Gemini

1. Apri la [pagina ufficiale delle chiavi Gemini](https://ai.google.dev/gemini-api/docs/api-key).
2. Accedi a Google AI Studio.
3. Scegli un progetto e crea una chiave.
4. Incollala in **Impostazioni → Gemini**.
5. Scegli **Verifica**, poi **Salva impostazioni**.

> [!WARNING]
> Non condividere mai una chiave in documenti, schermate, messaggi o richieste di assistenza. Se viene esposta, revocala e creane un’altra.

## Elaborazione dei contenuti lunghi

São Francisco prepara i video lunghi in parti più piccole e le unisce in un’unica trascrizione, senza inviare l’intero video in una volta.

Le parti completate vengono salvate. Dopo un’interruzione puoi continuare dalla **Cronologia** senza rifare tutto. Il tempo dipende dalla durata, dalla velocità di internet e dalla disponibilità del servizio.

## Seguire, annullare e riprendere

La schermata mostra l’avanzamento e la parte in elaborazione.

**Annulla** cambia la scheda in **Annullamento** e termina l’esecuzione entro circa cinque secondi. Parti e file già completati restano disponibili. Una richiesta già arrivata al servizio può terminare o generare addebiti anche dopo l’annullamento.

**Riprendi** continua un’attività interrotta. Cambiare file sorgente, servizio, modello o lingua di trascrizione richiede una nuova attività. Se l’esito di una richiesta precedente è incerto, l’app avvisa prima di consentirne un’altra, perché potrebbe generare un nuovo addebito.

## Formati di uscita

- **TXT:** testo semplice da leggere e cercare.
- **DOCX:** documento formattato per programmi di videoscrittura.
- **SRT:** sottotitoli per lettori ed editor video.
- **VTT:** sottotitoli usati soprattutto sul web.

Le marcature temporali di DOCX e TXT sono facoltative e disattivate di default. Seleziona **Includi marcature temporali in DOCX e TXT** prima di avviare. SRT e VTT richiedono sempre i tempi. Se il modello non li fornisce con precisione, può essere necessario correggerli nell’editor video.

Per i video online, il titolo viene usato nei nomi dei file, adattandolo se necessario. Se il nome esiste già, viene aggiunto un numero al nuovo risultato.

### Migliora con IA

Seleziona **Migliora con IA** per ricevere una seconda versione più leggibile insieme all’originale. L’app organizza i paragrafi e corregge punteggiatura, maiuscole ed evidenti errori di riconoscimento.

Il miglioramento non deve riassumere, tradurre, abbellire o completare passaggi incerti. Controlla comunque soprattutto nomi, numeri e punti poco chiari.

DOCX e TXT ricevono file separati di **trascrizione** e **testo migliorato**. Le marcature temporali restano solo nell’originale. SRT e VTT non vengono riscritti.

Prima l’originale viene completato, salvato ed esportato; poi il miglioramento facoltativo crea file aggiuntivi. Se si interrompe, gli originali restano disponibili. La ripresa riutilizza fasi accettate e non ripete automaticamente richieste dall’esito incerto.

## Costi, dati e archiviazione

L’acquisto dell’app è separato dall’uso delle API. São Francisco non addebita le singole trascrizioni. Gli eventuali costi API sono addebitati direttamente da OpenAI o Google secondo account e modello; l’acquisto non include crediti API.

Ogni parte inviata può consumare quota. La ripresa riutilizza il lavoro completato. Con dati sufficienti appare una stima in dollari statunitensi. Importi piccoli appaiono come **meno di 0,01 USD**. Se tutto il testo viene da sottotitoli esistenti senza miglioramento, appare **Nessun costo API**.

È solo una stima. Piani gratuiti, imposte, sconti, tentativi interrotti e variazioni di prezzo possono cambiare l’importo ufficiale. Consulta [l’utilizzo OpenAI](https://platform.openai.com/usage) o la [fatturazione Google Cloud](https://console.cloud.google.com/billing).

Se il servizio fornisce un conteggio affidabile, l’app può mostrare token: piccole unità che misurano ingresso e risposta. Non inventa conteggi non forniti.

### Prezzi API aggiornati

Consulta le pagine ufficiali dei [prezzi OpenAI](https://developers.openai.com/api/docs/pricing) e dei [prezzi Gemini](https://ai.google.dev/gemini-api/docs/pricing). Prezzi, unità, modelli e piani gratuiti possono cambiare. Verificali prima di un lavoro a pagamento.

L’audio viene inviato al servizio scelto. Cronologia e file di lavoro restano sul computer. I risultati restano nella cartella di destinazione finché non li elimini. Consulta i [termini OpenAI](https://openai.com/policies) e i [termini dell’API Gemini](https://ai.google.dev/gemini-api/terms).

## Problemi comuni

### La chiave non è accettata

**Sintomo:** le impostazioni segnalano una chiave non valida. **Azione:** verifica fornitore, copia completa e validità della chiave; poi fatturazione, limiti e accesso al modello.

### Il file non ha audio

**Sintomo:** l’attività termina prima della trascrizione. **Azione:** apri il file e verifica il suono. File danneggiati o video composti solo da immagini non possono essere trascritti.

### L’indirizzo video non funziona più

**Sintomo:** l’app non recupera il video. **Azione:** aggiorna São Francisco e riprova. Contenuti con accesso, pagamento, dirette o blocchi del sito possono restare indisponibili.

### L’elaborazione sembra ferma

**Sintomo:** la stessa parte resta attiva per vari minuti. **Azione:** registrazioni lunghe e servizi occupati richiedono tempo. Se appare un messaggio di rete o quota, annulla e riprendi più tardi.

### I sottotitoli non sono sincronizzati

**Sintomo:** SRT o VTT anticipa o ritarda la voce. **Azione:** usa **Sottotitoli e tempi** e verifica insieme al video.

### Spazio insufficiente

**Sintomo:** preparazione o creazione di file si interrompe. **Azione:** libera spazio e riprova.

## Scorciatoie e navigazione

- `⌘N` su macOS o `Ctrl+N` altrove apre **Trascrivi**.
- `⌘K` o `Ctrl+K` apre la **Guida**.
- `⌘,` o `Ctrl+,` apre **Impostazioni**.
- `Tab` e `Shift+Tab` spostano il focus.
- `Invio` o `Spazio` attiva il controllo selezionato.
- `Page Up`, `Page Down`, `Home` ed `End` scorrono i testi lunghi.
- `Esc` chiude le finestre degli avvisi.

Indice e articolo della guida scorrono indipendentemente.

## Licenze e informazioni

Il codice di São Francisco è distribuito con licenza MIT. Vendere i pacchetti pronti da scaricare non elimina le libertà della licenza. Componenti, librerie e caratteri mantengono le proprie licenze. Apri **Informazioni → Visualizza avvisi di terze parti** per leggere l’inventario.
