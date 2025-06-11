#!/usr/bin/env python3
"""
Image Utils - Utilità per elaborazione immagini multispettrali

Fornisce funzioni di utilità per l'elaborazione e manipolazione
di immagini multispettrali per il labeling.
"""

import numpy as np
import tifffile
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional, List, Union
import os


class ImageUtils:
    """Classe con utilità per immagini multispettrali"""

    @staticmethod
    def load_image(file_path: str) -> Optional[Tuple[np.ndarray, str]]:
        """
        Carica un'immagine (multispettrale TIFF o RGB standard)

        Args:
            file_path: Percorso del file

        Returns:
            Tuple (array numpy, tipo_immagine) o None se errore
            tipo_immagine: 'multispectral' o 'rgb'
        """
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext in ['.tif', '.tiff']:
                # Carica come TIFF multispettrale
                image_data = tifffile.imread(file_path)

                # Normalizza formato
                if len(image_data.shape) == 2:
                    # Immagine singola banda
                    image_data = image_data[np.newaxis, :, :]
                elif len(image_data.shape) == 3:
                    # Verifica se è (height, width, bands) e trasponi se necessario
                    if image_data.shape[2] < image_data.shape[0] and image_data.shape[2] <= 5:
                        image_data = np.transpose(image_data, (2, 0, 1))

                return image_data, 'multispectral'

            elif file_ext in ['.png', '.jpg', '.jpeg']:
                # Carica come immagine RGB standard
                pil_image = Image.open(file_path)

                # Converti in RGB se necessario
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')

                # Converti in array numpy (height, width, 3)
                rgb_array = np.array(pil_image)

                # Trasponi in formato (bands, height, width) per compatibilità
                image_data = np.transpose(rgb_array, (2, 0, 1))

                return image_data, 'rgb'
            else:
                print(f"Formato file non supportato: {file_ext}")
                return None

        except Exception as e:
            print(f"Errore caricamento immagine {file_path}: {e}")
            return None

    @staticmethod
    def load_multispectral_image(file_path: str) -> Optional[np.ndarray]:
        """
        Carica un'immagine multispettrale (retrocompatibilità)

        Args:
            file_path: Percorso del file TIFF

        Returns:
            Array numpy (bands, height, width) o None se errore
        """
        result = ImageUtils.load_image(file_path)
        if result is None:
            return None

        image_data, image_type = result
        return image_data
    
    @staticmethod
    def get_image_info(file_path: str) -> Optional[dict]:
        """
        Ottieni informazioni su un'immagine
        
        Args:
            file_path: Percorso del file
            
        Returns:
            Dizionario con informazioni o None se errore
        """
        try:
            image_data = ImageUtils.load_multispectral_image(file_path)
            if image_data is None:
                return None
            
            file_stat = Path(file_path).stat()
            
            return {
                'filename': os.path.basename(file_path),
                'path': file_path,
                'shape': image_data.shape,
                'bands': image_data.shape[0],
                'height': image_data.shape[1],
                'width': image_data.shape[2],
                'dtype': str(image_data.dtype),
                'size_mb': file_stat.st_size / (1024 * 1024),
                'min_value': float(image_data.min()),
                'max_value': float(image_data.max()),
                'mean_value': float(image_data.mean())
            }
            
        except Exception as e:
            print(f"Errore analisi immagine {file_path}: {e}")
            return None
    
    @staticmethod
    def normalize_band(band_data: np.ndarray, percentile_range: Tuple[float, float] = (2, 98)) -> np.ndarray:
        """
        Normalizza una banda per visualizzazione
        
        Args:
            band_data: Dati della banda
            percentile_range: Range di percentili per normalizzazione
            
        Returns:
            Banda normalizzata (0-1)
        """
        try:
            low_perc, high_perc = percentile_range
            band_min = np.percentile(band_data, low_perc)
            band_max = np.percentile(band_data, high_perc)
            
            if band_max > band_min:
                normalized = (band_data - band_min) / (band_max - band_min)
                return np.clip(normalized, 0, 1)
            else:
                return np.zeros_like(band_data, dtype=np.float32)
                
        except Exception as e:
            print(f"Errore normalizzazione banda: {e}")
            return np.zeros_like(band_data, dtype=np.float32)
    
    @staticmethod
    def create_rgb_composite(
        image_data: np.ndarray, 
        band_indices: Tuple[int, int, int] = (2, 1, 0),
        normalize: bool = True
    ) -> Optional[np.ndarray]:
        """
        Crea un composito RGB da immagine multispettrale
        
        Args:
            image_data: Dati immagine (bands, height, width)
            band_indices: Indici delle bande per R, G, B
            normalize: Se normalizzare le bande
            
        Returns:
            Array RGB (height, width, 3) o None se errore
        """
        try:
            if len(image_data.shape) != 3:
                raise ValueError("Immagine deve avere 3 dimensioni")
            
            bands, height, width = image_data.shape
            r_idx, g_idx, b_idx = band_indices
            
            # Verifica indici validi
            if max(band_indices) >= bands:
                raise ValueError(f"Indici banda non validi per immagine con {bands} bande")
            
            # Estrai bande
            red_band = image_data[r_idx]
            green_band = image_data[g_idx]
            blue_band = image_data[b_idx]
            
            # Normalizza se richiesto
            if normalize:
                red_band = ImageUtils.normalize_band(red_band)
                green_band = ImageUtils.normalize_band(green_band)
                blue_band = ImageUtils.normalize_band(blue_band)
            
            # Crea composito RGB
            rgb_composite = np.stack([red_band, green_band, blue_band], axis=2)
            
            return rgb_composite
            
        except Exception as e:
            print(f"Errore creazione composito RGB: {e}")
            return None
    
    @staticmethod
    def validate_coordinates(
        x: int, 
        y: int, 
        image_shape: Tuple[int, int, int]
    ) -> bool:
        """
        Valida coordinate per un'immagine
        
        Args:
            x: Coordinata X
            y: Coordinata Y
            image_shape: Forma immagine (bands, height, width)
            
        Returns:
            True se coordinate valide
        """
        try:
            bands, height, width = image_shape
            return 0 <= x < width and 0 <= y < height
        except:
            return False
    
    @staticmethod
    def calculate_crop_bounds(
        center_x: int,
        center_y: int,
        crop_size: int,
        image_shape: Tuple[int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Calcola i bounds per un crop centrato
        
        Args:
            center_x: Coordinata X del centro
            center_y: Coordinata Y del centro
            crop_size: Dimensione del crop
            image_shape: Forma immagine (bands, height, width)
            
        Returns:
            Tuple (x1, y1, x2, y2) dei bounds
        """
        bands, height, width = image_shape
        
        half_size = crop_size // 2
        
        x1 = max(0, center_x - half_size)
        y1 = max(0, center_y - half_size)
        x2 = min(width, center_x + half_size)
        y2 = min(height, center_y + half_size)
        
        return x1, y1, x2, y2
    
    @staticmethod
    def find_supported_image_files(directory: str) -> List[str]:
        """
        Trova tutti i file immagine supportati in una directory

        Args:
            directory: Percorso della directory

        Returns:
            Lista di percorsi file immagine supportati
        """
        try:
            directory_path = Path(directory)
            if not directory_path.exists() or not directory_path.is_dir():
                return []

            image_files = []
            # Supporta TIFF multispettrali e immagini RGB standard (case insensitive)
            patterns = [
                "*.tif", "*.tiff", "*.TIF", "*.TIFF",
                "*.png", "*.PNG",
                "*.jpg", "*.JPG", "*.jpeg", "*.JPEG"
            ]

            for pattern in patterns:
                image_files.extend(directory_path.glob(pattern))

            return [str(f) for f in sorted(image_files)]

        except Exception as e:
            print(f"Errore ricerca file immagine in {directory}: {e}")
            return []

    @staticmethod
    def find_tiff_files(directory: str) -> List[str]:
        """
        Trova tutti i file TIFF in una directory (retrocompatibilità)

        Args:
            directory: Percorso della directory

        Returns:
            Lista di percorsi file TIFF
        """
        try:
            directory_path = Path(directory)
            if not directory_path.exists() or not directory_path.is_dir():
                return []

            tiff_files = []
            patterns = ["*.tif", "*.tiff", "*.TIF", "*.TIFF"]

            for pattern in patterns:
                tiff_files.extend(directory_path.glob(pattern))

            return [str(f) for f in sorted(tiff_files)]

        except Exception as e:
            print(f"Errore ricerca file TIFF in {directory}: {e}")
            return []

    @staticmethod
    def get_image_type(file_path: str) -> str:
        """
        Determina il tipo di immagine dal percorso del file

        Args:
            file_path: Percorso del file

        Returns:
            'multispectral' per TIFF, 'rgb' per PNG/JPG, 'unknown' per altri
        """
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext in ['.tif', '.tiff']:
                return 'multispectral'
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return 'rgb'
            else:
                return 'unknown'

        except Exception:
            return 'unknown'

    @staticmethod
    def get_pixel_value(
        image_data: np.ndarray,
        x: int,
        y: int,
        band_index: Optional[int] = None
    ) -> Union[float, List[float], None]:
        """
        Ottieni valore pixel alle coordinate specificate
        
        Args:
            image_data: Dati immagine (bands, height, width)
            x: Coordinata X
            y: Coordinata Y
            band_index: Indice banda specifica (None per tutte)
            
        Returns:
            Valore pixel o lista valori per tutte le bande
        """
        try:
            if not ImageUtils.validate_coordinates(x, y, image_data.shape):
                return None
            
            if band_index is not None:
                if 0 <= band_index < image_data.shape[0]:
                    return float(image_data[band_index, y, x])
                else:
                    return None
            else:
                # Restituisci valori per tutte le bande
                return [float(image_data[i, y, x]) for i in range(image_data.shape[0])]
                
        except Exception as e:
            print(f"Errore lettura pixel ({x}, {y}): {e}")
            return None
    
    @staticmethod
    def create_preview_image(
        image_data: np.ndarray,
        max_size: int = 400,
        band_indices: Optional[Tuple[int, int, int]] = None
    ) -> Optional[Image.Image]:
        """
        Crea un'immagine preview ridimensionata
        
        Args:
            image_data: Dati immagine (bands, height, width)
            max_size: Dimensione massima del lato più lungo
            band_indices: Indici bande per RGB (None per prima banda in grayscale)
            
        Returns:
            Immagine PIL o None se errore
        """
        try:
            if band_indices is None:
                # Usa prima banda in grayscale
                band_data = image_data[0]
                normalized = ImageUtils.normalize_band(band_data)
                img_array = (normalized * 255).astype(np.uint8)
                pil_image = Image.fromarray(img_array, mode='L')
            else:
                # Crea composito RGB
                rgb_composite = ImageUtils.create_rgb_composite(image_data, band_indices)
                if rgb_composite is None:
                    return None
                
                img_array = (rgb_composite * 255).astype(np.uint8)
                pil_image = Image.fromarray(img_array, mode='RGB')
            
            # Ridimensiona se necessario
            if pil_image.width > max_size or pil_image.height > max_size:
                pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return pil_image
            
        except Exception as e:
            print(f"Errore creazione preview: {e}")
            return None
