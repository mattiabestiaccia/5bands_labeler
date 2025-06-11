# Labeler Multispettrale 5 Bande

Interfaccia grafica per il labeling e crop di immagini multispettrali con 5 bande, ottimizzata per camera MicaSense Red Edge.

## Caratteristiche

### Funzionalità Principali
- **Caricamento immagini**: File singoli, multipli o cartelle di immagini TIFF
- **Creazione progetti automatica**: Struttura organizzata per ogni sessione di labeling
- **Visualizzazione multispettrale**: 5 modalità di visualizzazione avanzate
- **Click per coordinate**: Selezione coordinate tramite click sull'immagine
- **Crop personalizzabili**: Ritagli quadrati con dimensioni da 16 a 512 pixel
- **Salvataggio automatico**: Nomi automatici basati su coordinate e dimensioni
- **Cleanup automatico**: Rimozione progetti vuoti alla chiusura

### Modalità di Visualizzazione

1. **Bande Singole**: Visualizzazione di ogni banda individualmente
   - Banda 1: Blue (475nm)
   - Banda 2: Green (560nm)
   - Banda 3: Red (668nm)
   - Banda 4: Red Edge (717nm)
   - Banda 5: Near-IR (840nm)

2. **RGB Naturale (3,2,1)**: Composizione a colori naturali
3. **False Color IR (5,3,2)**: Vegetazione evidenziata in rosso
4. **Red Edge Enhanced (4,3,2)**: Analisi stress vegetazione
5. **NDVI-like (5,4,3)**: Indicatore salute vegetazione

## Struttura Progetto

Ogni progetto creato ha la seguente struttura:

```
nome_progetto/
├── originals/          # Immagini originali caricate
├── crops/              # Crop salvati
└── project_metadata.json  # Metadati del progetto
```

## Installazione

### Dipendenze Richieste

```bash
pip install pillow numpy tifffile imagecodecs
```

### Dipendenze Sistema
- Python 3.7+
- tkinter (solitamente incluso con Python)

## Utilizzo

### Avvio Applicazione

**Metodo 1 - Script automatico (raccomandato):**
```bash
bash scripts/start_labeler.sh
```

**Metodo 2 - Manuale con ambiente virtuale:**
```bash
cd /home/brus/Projects/HPL/paper/5bands_labeler
source venv_labeler/bin/activate
python3 scripts/run_labeler.py
```

**Metodo 3 - Comando singolo:**
```bash
cd /home/brus/Projects/HPL/paper/5bands_labeler && source venv_labeler/bin/activate && python3 scripts/run_labeler.py
```

### Workflow Tipico

1. **Carica immagini**:
   - Usa i pulsanti per selezionare file singoli, multipli o cartelle
   - Il progetto viene creato automaticamente
   - Oppure carica un progetto esistente per continuare il lavoro

2. **Seleziona coordinate**:
   - Doppio click su un file nella lista per caricarlo
   - Usa il dropdown per cambiare modalità di visualizzazione
   - Clicca sull'immagine per selezionare le coordinate del centro del crop

3. **Configura crop**:
   - Imposta la dimensione del crop (16-512 pixel)
   - Usa spinbox, slider o preset rapidi
   - Preset comuni: 32, 64, 128, 256px
   - Preset aggiuntivi: 16, 48, 96, 192, 384, 512px
   - Verifica l'anteprima in tempo reale sull'immagine
   - Visualizza l'anteprima del crop estratto nel pannello dedicato

4. **Salva crop**:
   - Clicca "Salva Crop" per salvare il ritaglio
   - I file vengono salvati automaticamente nella cartella `crops/`
   - Nomi automatici basati su coordinate e dimensioni

### Controlli Interfaccia

#### Pannello Sinistro
- **Selezione File**: Caricamento immagini singole, multiple o cartelle
- **Progetto Corrente**: Gestione del progetto attivo con caricamento progetti esistenti
- **Controlli Crop**: Configurazione dimensioni e coordinate del crop

#### Pannello Destro
- **Visualizzatore**: Immagine con modalità di visualizzazione
- **Click Coordinate**: Click sull'immagine per selezionare coordinate
- **Anteprima Crop Overlay**: Rettangolo giallo tratteggiato sull'immagine
- **Anteprima Crop Estratto**: Pannello dedicato con preview del crop effettivo
- **Navigazione Bande**: Controlli per scorrere le bande (modalità singola)

### Controlli Dimensioni Crop Avanzati

Il labeler offre controlli multipli per specificare la dimensione del crop:

1. **Spinbox Numerico**: Inserimento diretto del valore (16-512px)
2. **Slider Orizzontale**: Controllo visuale con trascinamento
3. **Preset Comuni**: Bottoni rapidi per 32, 64, 128, 256px
4. **Preset Aggiuntivi**: Bottoni per 16, 48, 96, 192, 384, 512px

### Anteprima Crop Doppia

Il sistema fornisce due tipi di anteprima:

1. **Overlay sull'Immagine**:
   - Rettangolo giallo tratteggiato
   - Mostra l'area esatta che verrà ritagliata
   - Si aggiorna in tempo reale con le dimensioni

2. **Pannello Anteprima Dedicato**:
   - Visualizzazione del crop estratto (200x200px max)
   - Rispetta la modalità di visualizzazione corrente
   - Include informazioni dettagliate (coordinate, dimensioni, modalità)
   - Validazione automatica (avviso se troppo vicino ai bordi)

### Caricamento Progetti Esistenti

Il labeler permette di riprendere progetti precedenti:

1. **Accesso ai Progetti**:
   - Bottone "📂 Carica Progetto" nel pannello progetto
   - Menu File → "Carica Progetto..."

2. **Finestra Selezione Progetti**:
   - Lista di tutti i progetti disponibili
   - Informazioni dettagliate: nome, date, numero crop
   - Anteprima informazioni progetto selezionato
   - Ordinamento per data ultima modifica

3. **Informazioni Visualizzate**:
   - Nome progetto e percorso
   - Data creazione e ultima modifica
   - Numero di crop già salvati
   - Tipo di GUI utilizzata
   - Informazioni sui file sorgente

4. **Funzionalità Aggiuntive**:
   - Doppio click per caricamento rapido
   - Bottone "Apri Cartella" per esplorare il progetto
   - Aggiornamento automatico lista progetti
   - Continuazione seamless del lavoro precedente

### Aggiunta Immagini a Progetti Esistenti

Quando si carica un progetto esistente, è possibile aggiungere nuove immagini:

1. **Comportamento Automatico**:
   - Con progetto caricato: nuove selezioni si aggiungono al progetto
   - Senza progetto: nuove selezioni creano nuovo progetto

2. **Processo di Aggiunta**:
   - Seleziona file singoli, multipli o cartelle
   - Le immagini vengono aggiunte automaticamente al progetto corrente
   - Evita duplicati automaticamente
   - Aggiorna metadati del progetto

3. **Notifiche e Feedback**:
   - Messaggio di conferma con numero immagini aggiunte
   - Aggiornamento contatore immagini nel pannello progetto
   - Log dettagliato delle operazioni

4. **Vantaggi**:
   - Espansione progetti esistenti senza perdere lavoro
   - Gestione centralizzata di dataset complessi
   - Tracciamento completo di tutte le immagini utilizzate

## Interpretazione Visualizzazioni

### RGB Naturale (3,2,1)
- **Colori naturali**: Simile alla visione umana
- **Verde**: Vegetazione sana
- **Marrone/Giallo**: Suolo o vegetazione secca
- **Blu**: Acqua

### False Color IR (5,3,2)
- **Rosso brillante**: Vegetazione sana e densa
- **Rosa/Magenta**: Vegetazione moderata
- **Verde scuro**: Suolo o vegetazione rada
- **Blu/Nero**: Acqua o superfici artificiali

### Red Edge Enhanced (4,3,2)
- **Rosso intenso**: Vegetazione con alta attività Red Edge
- **Arancione/Giallo**: Vegetazione con stress moderato
- **Verde**: Vegetazione con possibile stress
- **Blu**: Aree non vegetate

### NDVI-like (5,4,3)
- **Rosso brillante**: Alta attività fotosintetica
- **Giallo/Verde**: Attività fotosintetica moderata
- **Blu/Viola**: Bassa attività fotosintetica o stress

## Risoluzione Problemi

### Errore "LZW compression"
Se ricevi errori relativi alla compressione LZW:
```bash
pip install imagecodecs
```

### Immagini non caricate
- Verifica che i file siano TIFF multibanda
- Controlla che abbiano 5 bande (ottimale per MicaSense)
- File con numero diverso di bande vengono caricati ma con avviso

### Progetti non creati
- Verifica permessi di scrittura nella cartella
- Controlla spazio disco disponibile

### Crop non validi
- Verifica che le coordinate siano dentro l'immagine
- Assicurati che il crop non sia troppo vicino ai bordi
- Riduci la dimensione del crop se necessario

## Limitazioni

- Supporta solo file TIFF multibanda
- Ottimizzato per 5 bande (MicaSense Red Edge)
- Visualizzazione ridimensionata a 800px per performance
- Crop sempre a risoluzione originale
- Crop sempre quadrati

## Sviluppo

### Struttura Codice

- `labeling_gui.py`: Interfaccia principale
- `coordinate_viewer.py`: Visualizzatore con click per coordinate
- `crop_controls.py`: Controlli per configurazione crop
- `file_selector.py`: Componente selezione file
- `project_manager.py`: Gestione progetti per labeling
- `image_cropper.py`: Logica di crop delle immagini
- `image_utils.py`: Utilità per elaborazione immagini

### Estensioni Possibili

- Supporto crop rettangolari
- Batch processing per crop multipli
- Export in formati diversi (PNG, JPEG)
- Annotazioni sui crop
- Integrazione con database di labeling
- Supporto per altri sensori multispettrali

## Differenze dal Visualizzatore

Il Labeler si differenzia dal Visualizzatore per:

1. **Focus sul labeling**: Ottimizzato per creare dataset di training
2. **Click per coordinate**: Selezione precisa di punti di interesse
3. **Crop automatici**: Generazione rapida di ritagli quadrati
4. **Gestione batch**: Elaborazione efficiente di molte immagini
5. **Metadati crop**: Tracciamento completo di coordinate e parametri

## Casi d'Uso

- **Machine Learning**: Creazione dataset per training modelli
- **Analisi vegetazione**: Estrazione campioni per studio fenologico
- **Monitoraggio colture**: Selezione aree di interesse per analisi temporali
- **Ricerca agricola**: Campionamento sistematico di parcelle sperimentali
- **Controllo qualità**: Verifica manuale di algoritmi di classificazione
