# Labeler Multispettrale 5 Bande

Interfaccia grafica per il labeling e crop di immagini multispettrali con 5 bande, ottimizzata per camera MicaSense Red Edge.

## 🚀 Avvio Rapido

```bash
# Metodo 1 - Script automatico (raccomandato)
cd /home/brus/Projects/HPL/paper/5bands_labeler
bash scripts/start_labeler.sh

# Metodo 2 - Manuale con ambiente virtuale
cd /home/brus/Projects/HPL/paper/5bands_labeler
source venv_labeler/bin/activate
python3 scripts/run_labeler.py

# Metodo 3 - Comando singolo
cd /home/brus/Projects/HPL/paper/5bands_labeler && source venv_labeler/bin/activate && python3 scripts/run_labeler.py
```

## 📁 Struttura Progetto

```
5bands_labeler/
├── src/                           # Codice sorgente principale
│   ├── gui/                      # Componenti interfaccia grafica
│   │   ├── labeling_gui.py       # Interfaccia principale
│   │   ├── coordinate_viewer.py  # Visualizzatore con click coordinate
│   │   ├── crop_controls.py      # Controlli per il crop
│   │   ├── file_selector.py      # Selettore file/cartelle
│   │   └── project_selector.py   # Selettore progetti
│   ├── core/                     # Logica di business
│   │   ├── image_cropper.py      # Logica di crop immagini
│   │   └── project_manager.py    # Gestione progetti
│   ├── utils/                    # Funzioni di utilità
│   │   ├── image_utils.py        # Utilità elaborazione immagini
│   │   └── superpixel_utils.py   # Algoritmi superpixel
│   └── 5bands_labeler.egg-info/  # Metadati installazione
├── scripts/                      # Script di avvio e utilità
│   ├── run_labeler.py           # Script principale di avvio
│   ├── start_labeler.sh         # Script bash automatico
│   └── create_light_augmented_dataset.py  # Creazione dataset
├── docs/                         # Documentazione dettagliata
│   └── README.md                # Documentazione completa
├── projects/                     # Progetti utente
│   ├── test_proj/               # Progetto di test (incluso in git)
│   ├── project_metadata.json   # Metadati progetti globali
│   └── labeling_project_*/      # Progetti utente (esclusi da git)
│       ├── originals/           # Immagini originali
│       ├── crops/               # Crop estratti
│       └── project_metadata.json  # Metadati progetto
├── venv_labeler/                 # Ambiente virtuale Python
├── setup.py                     # Configurazione installazione
├── requirements.txt             # Dipendenze Python
└── README.md                    # Questo file
```

## ✨ Funzionalità

- **Caricamento immagini**: File singoli, multipli o cartelle TIFF
- **5 modalità di visualizzazione**:
  - Bande singole (1-5)
  - RGB Naturale (3,2,1)
  - False Color IR (5,3,2) - vegetazione in rosso
  - Red Edge Enhanced (4,3,2) - stress vegetazione
  - NDVI-like (5,4,3) - salute vegetazione
- **Click per coordinate**: Click sull'immagine per selezionare coordinate
- **Anteprima crop in tempo reale**: Rettangolo giallo tratteggiato sull'immagine
- **Anteprima crop estratto**: Visualizzazione del crop effettivo in pannello dedicato
- **Crop quadrato**: Ritaglio quadrato centrato sulle coordinate selezionate
- **Controlli dimensioni avanzati**: Spinbox, slider e preset per dimensioni (16-512px)
- **Gestione progetti automatica**: Struttura `proj/originals/crops/`
- **Caricamento progetti esistenti**: Riprendi lavori precedenti
- **Salvataggio organizzato**: Crop salvati con nomi descrittivi
- **Cleanup automatico**: Rimozione progetti vuoti alla chiusura

## 📋 Requisiti

- **Python 3.7+** (testato fino a 3.11)
- **tkinter** (incluso con Python)
- **Dipendenze principali**:
  - `Pillow>=9.0.0` - Elaborazione immagini
  - `numpy>=1.21.0` - Calcoli numerici
  - `tifffile>=2021.11.2` - Lettura file TIFF
  - `imagecodecs>=2021.11.20` - Supporto compressione TIFF
  - `scikit-image>=0.19.0` - Algoritmi superpixel

### Installazione Dipendenze

```bash
# Installazione automatica con pip
pip install -r requirements.txt

# Oppure installazione come pacchetto
pip install -e .
```

## 📂 Gestione Progetti

Il labeler organizza automaticamente il lavoro in progetti con struttura standardizzata:

```
projects/
├── project_metadata.json           # Registro globale progetti
├── test_proj/                      # Progetto di esempio
└── labeling_project_YYYYMMDD_HHMMSS/  # Progetti utente
    ├── originals/                  # Immagini originali caricate
    ├── crops/                      # Crop estratti organizzati
    │   ├── image1_crop_001.tif
    │   ├── image1_crop_002.tif
    │   └── ...
    └── project_metadata.json       # Metadati specifici progetto
```

**Caratteristiche**:
- **Creazione automatica**: Nuovi progetti con timestamp
- **Caricamento esistenti**: Riprendi lavori precedenti
- **Cleanup automatico**: Rimozione progetti vuoti alla chiusura
- **Backup sicuro**: Solo `test_proj` incluso in git, progetti utente esclusi

## 📖 Documentazione

Per informazioni dettagliate, consulta la [documentazione completa](docs/README.md).

## 🔧 Sviluppo

### Struttura Codice Dettagliata

**Interfaccia Grafica (`src/gui/`)**:
- `labeling_gui.py`: Interfaccia principale e coordinamento componenti
- `coordinate_viewer.py`: Visualizzatore immagini con click per coordinate
- `crop_controls.py`: Controlli avanzati per dimensioni crop
- `file_selector.py`: Selettore file e cartelle con anteprima
- `project_selector.py`: Gestione selezione e creazione progetti

**Logica Core (`src/core/`)**:
- `image_cropper.py`: Algoritmi di crop e elaborazione immagini
- `project_manager.py`: Gestione progetti, metadati e strutture

**Utilità (`src/utils/`)**:
- `image_utils.py`: Funzioni elaborazione e visualizzazione immagini
- `superpixel_utils.py`: Algoritmi superpixel per segmentazione avanzata

### Installazione Sviluppo

```bash
# Clona e configura ambiente
git clone <repository-url>
cd 5bands_labeler

# Crea ambiente virtuale (se non esiste)
python3 -m venv venv_labeler
source venv_labeler/bin/activate

# Installa in modalità sviluppo
pip install -e .

# Oppure installa dipendenze manualmente
pip install -r requirements.txt
```

### Test e Debug

```bash
# Avvio normale
bash scripts/start_labeler.sh

# Avvio con ambiente virtuale attivo
source venv_labeler/bin/activate
python3 scripts/run_labeler.py

# Debug con output verboso
python3 -u scripts/run_labeler.py
```

## 📄 Licenza

Progetto HPL - Labeler Multispettrale 5 Bande
