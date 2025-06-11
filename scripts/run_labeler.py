#!/usr/bin/env python3
"""
Run Labeler - Script di avvio per il labeler multispettrale

Avvia l'interfaccia grafica per il labeling di immagini multispettrali
con 5 bande (MicaSense Red Edge).
"""

import sys
import os
from pathlib import Path

# Aggiungi le directory necessarie al path per gli import
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
gui_dir = src_dir / "gui"
core_dir = src_dir / "core"
utils_dir = src_dir / "utils"

# Aggiungi tutte le directory necessarie
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(gui_dir))
sys.path.insert(0, str(core_dir))
sys.path.insert(0, str(utils_dir))

try:
    from labeling_gui import main

    if __name__ == "__main__":
        print("🚀 Avvio Labeler Multispettrale 5 Bande...")
        print("📋 Funzionalità disponibili:")
        print("   • Caricamento immagini TIFF multispettrali")
        print("   • Visualizzazione bande singole")
        print("   • RGB Naturale (3,2,1)")
        print("   • False Color IR (5,3,2)")
        print("   • Red Edge Enhanced (4,3,2)")
        print("   • NDVI-like (5,4,3)")
        print("   • Click per coordinate")
        print("   • Crop quadrati personalizzabili")
        print("   • Salvataggio crop automatico")
        print("   • Gestione progetti automatica")
        print()

        main()

except ImportError as e:
    print(f"❌ Errore import: {e}")
    print("Verifica che tutte le dipendenze siano installate:")
    print("pip install pillow numpy tifffile imagecodecs")
    sys.exit(1)
except Exception as e:
    print(f"❌ Errore avvio applicazione: {e}")
    sys.exit(1)
