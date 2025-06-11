"""
GUI Module per 5bands_labeler
Interfaccia grafica per il labeling di immagini multispettrali
"""

__version__ = "1.0.0"
__author__ = "HPL Project"

# Import principali per facilitare l'uso del modulo
try:
    from .labeling_gui import LabelingGUI
    from .coordinate_viewer import CoordinateViewer
    from .file_selector import FileSelector
    from .crop_controls import CropControls
except ImportError:
    # Fallback per import relativi
    pass

def launch_gui():
    """Lancia l'interfaccia grafica principale"""
    from .labeling_gui import main
    main()

__all__ = [
    'LabelingGUI',
    'CoordinateViewer', 
    'FileSelector',
    'CropControls',
    'launch_gui'
]
