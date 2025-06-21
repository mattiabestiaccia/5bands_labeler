#!/bin/bash
# Script di avvio automatico per 5bands_labeler
# Gestisce ambiente virtuale e dipendenze

set -e  # Esci se qualsiasi comando fallisce

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directory del progetto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv_labeler"

echo -e "${BLUE}🚀 Avvio Labeler Multispettrale 5 Bande${NC}"
echo -e "${BLUE}📁 Directory progetto: $PROJECT_DIR${NC}"

# Funzione per creare ambiente virtuale
create_venv() {
    echo -e "${YELLOW}📦 Creazione ambiente virtuale...${NC}"
    python3 -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Errore creazione ambiente virtuale${NC}"
        echo -e "${RED}Verifica che python3-venv sia installato:${NC}"
        echo -e "${RED}sudo apt install python3-venv${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Ambiente virtuale creato${NC}"
}

# Funzione per installare dipendenze
install_dependencies() {
    echo -e "${YELLOW}📦 Installazione dipendenze...${NC}"
    
    # Attiva ambiente virtuale
    source "$VENV_DIR/bin/activate"
    
    # Aggiorna pip
    pip install --upgrade pip
    
    # Installa dipendenze
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip install -r "$PROJECT_DIR/requirements.txt"
    else
        echo -e "${YELLOW}⚠️ File requirements.txt non trovato, installazione dipendenze base...${NC}"
        pip install pillow numpy tifffile imagecodecs
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Errore installazione dipendenze${NC}"
        exit 1
    fi
    
    # Installa il package in modalità editable per import semplificati
    echo -e "${YELLOW}📦 Installazione package in modalità editable...${NC}"
    cd "$PROJECT_DIR"
    pip install -e .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Errore installazione package editable${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dipendenze e package installati${NC}"
}

# Verifica se Python è disponibile
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 non trovato${NC}"
    echo -e "${RED}Installa Python3 prima di continuare${NC}"
    exit 1
fi

# Verifica/crea ambiente virtuale
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Ambiente virtuale non trovato${NC}"
    create_venv
    install_dependencies
else
    echo -e "${GREEN}✅ Ambiente virtuale trovato${NC}"
    
    # Verifica se le dipendenze sono installate
    source "$VENV_DIR/bin/activate"
    if ! python -c "import PIL, numpy, tifffile" &> /dev/null || ! python -c "import src.gui.labeling_gui" &> /dev/null; then
        echo -e "${YELLOW}📦 Dipendenze mancanti o package non installato, reinstallazione...${NC}"
        install_dependencies
    fi
fi

# Attiva ambiente virtuale
echo -e "${BLUE}🔧 Attivazione ambiente virtuale...${NC}"
source "$VENV_DIR/bin/activate"

# Verifica che lo script Python esista
PYTHON_SCRIPT="$SCRIPT_DIR/run_labeler.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Script Python non trovato: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Avvia l'applicazione
echo -e "${GREEN}🚀 Avvio applicazione...${NC}"
echo ""

cd "$PROJECT_DIR"
python3 "$PYTHON_SCRIPT"

# Cattura il codice di uscita
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Applicazione chiusa correttamente${NC}"
else
    echo ""
    echo -e "${RED}❌ Applicazione chiusa con errore (codice: $EXIT_CODE)${NC}"
fi

exit $EXIT_CODE
