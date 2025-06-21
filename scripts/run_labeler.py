#!/usr/bin/env python3
"""
Run Labeler - Script di avvio per il labeler multispettrale

Avvia l'interfaccia grafica per il labeling di immagini multispettrali
con 5 bande (MicaSense Red Edge).
"""

import sys

try:
    from gui.labeling_gui import main

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
    print("Assicurati che il package sia installato in modalità editable:")
    print("pip install -e .")
    print("Oppure installa le dipendenze:")
    print("pip install pillow numpy tifffile imagecodecs")
    sys.exit(1)
except Exception as e:
    print(f"❌ Errore avvio applicazione: {e}")
    sys.exit(1)
