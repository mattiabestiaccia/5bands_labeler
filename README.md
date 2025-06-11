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
├── src/                    # Codice sorgente
│   ├── gui/               # Componenti interfaccia grafica
│   ├── core/              # Logica di business
│   └── utils/             # Funzioni di utilità
├── scripts/               # Script di avvio e utilità
├── docs/                  # Documentazione dettagliata
├── projects/              # Progetti utente (esclusi da git tranne test_proj)
├── venv_labeler/          # Ambiente virtuale Python
└── tests/                 # Test automatici (futuro)
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

- Python 3.7+
- tkinter (incluso con Python)
- Dipendenze: `pillow numpy tifffile imagecodecs`

## 📖 Documentazione

Per informazioni dettagliate, consulta la [documentazione completa](docs/README.md).

## 🔧 Sviluppo

### Struttura Codice

- `src/gui/labeling_gui.py`: Interfaccia principale
- `src/gui/coordinate_viewer.py`: Visualizzatore con click per coordinate
- `src/gui/crop_controls.py`: Controlli per il crop
- `src/core/image_cropper.py`: Logica di crop
- `src/core/project_manager.py`: Gestione progetti

### Test

```bash
# Avvio con ambiente virtuale
source venv_labeler/bin/activate
python3 scripts/run_labeler.py
```

## 📄 Licenza

Progetto HPL - Labeler Multispettrale 5 Bande
