#!/usr/bin/env python3
"""
Superpixel Utils - Utilità per generazione superpixel

Fornisce implementazioni degli algoritmi SLIC, Felzenszwalb e Quickshift
per la segmentazione in superpixel di immagini multispettrali.
"""

import numpy as np
from typing import Tuple, Optional, Union
from PIL import Image


class SuperpixelGenerator:
    """Generatore di superpixel per immagini multispettrali"""
    
    @staticmethod
    def prepare_image_for_superpixel(bands_data: np.ndarray, image_type: str, 
                                   view_mode: str = "rgb") -> Optional[np.ndarray]:
        """
        Prepara l'immagine per l'applicazione degli algoritmi superpixel
        
        Args:
            bands_data: Array (bands, height, width) 
            image_type: 'multispectral' o 'rgb'
            view_mode: modalità di visualizzazione corrente
            
        Returns:
            Array (height, width, 3) per RGB o (height, width) per singola banda
        """
        try:
            if image_type == 'rgb':
                # Immagine RGB: usa direttamente
                if bands_data.shape[0] == 3:
                    # Trasponi da (3, H, W) a (H, W, 3)
                    rgb_image = np.transpose(bands_data, (1, 2, 0))
                    return SuperpixelGenerator._normalize_for_display(rgb_image)
                else:
                    return None
                    
            elif image_type == 'multispectral':
                if bands_data.shape[0] >= 3:
                    # Multispettrale con almeno 3 bande: crea RGB usando bande 3,2,1 (Red, Green, Blue)
                    if bands_data.shape[0] >= 3:
                        # Usa bande 3,2,1 (indexing 0-based: 2,1,0)
                        rgb_bands = [2, 1, 0] if bands_data.shape[0] >= 3 else [0, 0, 0]
                        rgb_image = np.zeros((bands_data.shape[1], bands_data.shape[2], 3), dtype=np.float32)
                        
                        for i, band_idx in enumerate(rgb_bands):
                            if band_idx < bands_data.shape[0]:
                                rgb_image[:, :, i] = SuperpixelGenerator._normalize_band(bands_data[band_idx])
                        
                        return SuperpixelGenerator._normalize_for_display(rgb_image)
                else:
                    # Meno di 3 bande: usa la prima banda disponibile
                    single_band = SuperpixelGenerator._normalize_band(bands_data[0])
                    return single_band
                    
            return None
            
        except Exception as e:
            print(f"Errore preparazione immagine per superpixel: {e}")
            return None
    
    @staticmethod
    def _normalize_band(band_data: np.ndarray, percentiles: Tuple[float, float] = (2, 98)) -> np.ndarray:
        """Normalizza una banda usando percentili"""
        p_low, p_high = np.percentile(band_data, percentiles)
        normalized = np.clip((band_data - p_low) / (p_high - p_low), 0, 1)
        return normalized
    
    @staticmethod
    def _normalize_for_display(image: np.ndarray) -> np.ndarray:
        """Normalizza immagine per display (0-255)"""
        if image.dtype != np.uint8:
            # Normalizza a 0-1 se necessario
            if image.max() > 1.0:
                image = image / image.max()
            # Converti a 0-255
            image = (image * 255).astype(np.uint8)
        return image
    
    @staticmethod
    def generate_slic(image: np.ndarray, n_segments: int = 400, 
                     compactness: float = 10.0, sigma: float = 1.0) -> Optional[np.ndarray]:
        """
        Genera superpixel usando algoritmo SLIC
        
        Args:
            image: Immagine input (H, W, 3) per RGB o (H, W) per grayscale
            n_segments: Numero approssimativo di superpixel
            compactness: Bilancia aderenza al colore vs forma compatta
            sigma: Gaussian blur pre-processing
            
        Returns:
            Array (H, W) con label superpixel
        """
        try:
            from skimage.segmentation import slic
            from skimage.filters import gaussian
            
            # Pre-processing con gaussian blur
            if len(image.shape) == 3:
                # RGB
                processed_image = gaussian(image, sigma=sigma, channel_axis=2, preserve_range=True)
            else:
                # Grayscale
                processed_image = gaussian(image, sigma=sigma, preserve_range=True)
            
            # Applica SLIC
            segments = slic(processed_image, n_segments=n_segments, 
                          compactness=compactness, start_label=1, channel_axis=2 if len(image.shape) == 3 else None)
            
            return segments
            
        except ImportError:
            print("Errore: scikit-image non installato. Installa con: pip install scikit-image")
            return None
        except Exception as e:
            print(f"Errore generazione SLIC: {e}")
            return None
    
    @staticmethod
    def generate_felzenszwalb(image: np.ndarray, scale: float = 100, 
                            sigma: float = 0.5, min_size: int = 50) -> Optional[np.ndarray]:
        """
        Genera superpixel usando algoritmo Felzenszwalb
        
        Args:
            image: Immagine input (H, W, 3) per RGB o (H, W) per grayscale
            scale: Controlla dimensione segmenti (valori più alti = segmenti più grandi)
            sigma: Gaussian blur pre-processing
            min_size: Dimensione minima segmenti
            
        Returns:
            Array (H, W) con label superpixel
        """
        try:
            from skimage.segmentation import felzenszwalb
            from skimage.filters import gaussian
            
            # Pre-processing
            if len(image.shape) == 3:
                processed_image = gaussian(image, sigma=sigma, channel_axis=2, preserve_range=True)
            else:
                processed_image = gaussian(image, sigma=sigma, preserve_range=True)
            
            # Applica Felzenszwalb
            segments = felzenszwalb(processed_image, scale=scale, sigma=sigma, min_size=min_size)
            
            return segments
            
        except ImportError:
            print("Errore: scikit-image non installato. Installa con: pip install scikit-image")
            return None
        except Exception as e:
            print(f"Errore generazione Felzenszwalb: {e}")
            return None
    
    @staticmethod
    def generate_quickshift(image: np.ndarray, kernel_size: float = 3, 
                          max_dist: float = 6, ratio: float = 0.5) -> Optional[np.ndarray]:
        """
        Genera superpixel usando algoritmo Quickshift
        
        Args:
            image: Immagine input (H, W, 3) per RGB o (H, W) per grayscale
            kernel_size: Dimensione kernel per density estimation
            max_dist: Distanza massima per collegamenti
            ratio: Bilancia aderenza al colore vs vicinanza spaziale
            
        Returns:
            Array (H, W) con label superpixel
        """
        try:
            from skimage.segmentation import quickshift
            
            # Applica Quickshift
            segments = quickshift(image, kernel_size=kernel_size, 
                                max_dist=max_dist, ratio=ratio)
            
            return segments
            
        except ImportError:
            print("Errore: scikit-image non installato. Installa con: pip install scikit-image")
            return None
        except Exception as e:
            print(f"Errore generazione Quickshift: {e}")
            return None
    
    @staticmethod
    def create_boundary_overlay(segments: np.ndarray, color: Tuple[int, int, int] = (255, 255, 0),
                              thickness: int = 1) -> Optional[np.ndarray]:
        """
        Crea overlay con bordi dei superpixel
        
        Args:
            segments: Array segmentazione (H, W)
            color: Colore bordi RGB
            thickness: Spessore bordi
            
        Returns:
            Array (H, W, 4) RGBA con bordi trasparenti
        """
        try:
            from skimage.segmentation import find_boundaries
            from scipy.ndimage import binary_dilation
            
            # Trova bordi
            boundaries = find_boundaries(segments, mode='outer')
            
            # Applica dilatazione per spessore
            if thickness > 1:
                boundaries = binary_dilation(boundaries, iterations=thickness-1)
            
            # Crea overlay RGBA
            overlay = np.zeros((segments.shape[0], segments.shape[1], 4), dtype=np.uint8)
            
            # Imposta colore dove ci sono bordi
            overlay[boundaries, 0] = color[0]  # R
            overlay[boundaries, 1] = color[1]  # G  
            overlay[boundaries, 2] = color[2]  # B
            overlay[boundaries, 3] = 255      # A (opaco)
            
            return overlay
            
        except ImportError:
            print("Errore: scipy non disponibile per operazioni morfologiche")
            # Fallback senza dilatazione
            try:
                from skimage.segmentation import find_boundaries
                boundaries = find_boundaries(segments, mode='outer')
                overlay = np.zeros((segments.shape[0], segments.shape[1], 4), dtype=np.uint8)
                overlay[boundaries, :3] = color
                overlay[boundaries, 3] = 255
                return overlay
            except Exception:
                return None
        except Exception as e:
            print(f"Errore creazione overlay bordi: {e}")
            return None
    
    @staticmethod
    def get_superpixel_count(segments: np.ndarray) -> int:
        """Conta il numero di superpixel unici"""
        if segments is None:
            return 0
        return len(np.unique(segments))
    
    @staticmethod
    def get_superpixel_at_coordinate(segments: np.ndarray, x: int, y: int) -> Optional[int]:
        """
        Ottiene l'ID del superpixel alle coordinate specificate
        
        Args:
            segments: Array segmentazione
            x, y: Coordinate (x=colonna, y=riga)
            
        Returns:
            ID superpixel o None se coordinate non valide
        """
        try:
            if segments is None:
                return None
            
            h, w = segments.shape
            if 0 <= y < h and 0 <= x < w:
                return int(segments[y, x])
            return None
            
        except Exception as e:
            print(f"Errore accesso superpixel: {e}")
            return None