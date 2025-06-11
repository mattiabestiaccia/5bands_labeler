"""
Core Module per 5bands_labeler
Logica di business per il labeling di immagini multispettrali
"""

__version__ = "1.0.0"
__author__ = "HPL Project"

# Import principali
try:
    from .project_manager import ProjectManager
    from .image_cropper import ImageCropper
except ImportError:
    # Fallback per import relativi
    pass

__all__ = [
    'ProjectManager',
    'ImageCropper'
]
