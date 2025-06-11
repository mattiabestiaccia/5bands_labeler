"""
Utils Module per 5bands_labeler
Funzioni di utilità per il labeling di immagini multispettrali
"""

__version__ = "1.0.0"
__author__ = "HPL Project"

# Import principali
try:
    from .image_utils import ImageUtils
except ImportError:
    # Fallback per import relativi
    pass

__all__ = [
    'ImageUtils'
]
