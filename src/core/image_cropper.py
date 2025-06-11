#!/usr/bin/env python3
"""
Image Cropper - Logica per il crop di immagini multispettrali

Fornisce funzionalità per ritagliare immagini multispettrali in quadrati
centrati su coordinate specifiche.
"""

import numpy as np
import tifffile
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional, Union
import os


class ImageCropper:
    """Classe per il crop di immagini multispettrali"""
    
    def __init__(self):
        """Inizializza il cropper"""
        pass
    
    def crop_multispectral_image(
        self, 
        image_data: np.ndarray, 
        center_x: int, 
        center_y: int, 
        crop_size: int,
        output_path: str,
        preserve_bands: bool = True
    ) -> bool:
        """
        Ritaglia un'immagine multispettrale in un quadrato centrato
        
        Args:
            image_data: Array numpy dell'immagine (bands, height, width)
            center_x: Coordinata X del centro del crop
            center_y: Coordinata Y del centro del crop
            crop_size: Dimensione del lato del quadrato
            output_path: Percorso di output del file
            preserve_bands: Se True mantiene tutte le bande, altrimenti solo RGB
            
        Returns:
            True se il crop è stato salvato con successo
        """
        try:
            # Verifica formato immagine
            if len(image_data.shape) != 3:
                raise ValueError("L'immagine deve avere 3 dimensioni (bands, height, width)")
            
            bands, height, width = image_data.shape
            
            # Calcola bounds del crop
            half_size = crop_size // 2
            x1 = max(0, center_x - half_size)
            y1 = max(0, center_y - half_size)
            x2 = min(width, center_x + half_size)
            y2 = min(height, center_y + half_size)
            
            # Verifica che il crop sia valido
            actual_width = x2 - x1
            actual_height = y2 - y1
            
            if actual_width < crop_size or actual_height < crop_size:
                # Crop troppo vicino al bordo, prova ad aggiustare
                x1, y1, x2, y2 = self._adjust_crop_bounds(
                    center_x, center_y, crop_size, width, height
                )
                actual_width = x2 - x1
                actual_height = y2 - y1
                
                if actual_width < crop_size or actual_height < crop_size:
                    raise ValueError(f"Impossibile creare crop {crop_size}x{crop_size} alle coordinate ({center_x}, {center_y})")
            
            # Estrai il crop
            if preserve_bands:
                cropped_data = image_data[:, y1:y2, x1:x2]
            else:
                # Prendi solo le prime 3 bande per RGB
                num_bands = min(3, bands)
                cropped_data = image_data[:num_bands, y1:y2, x1:x2]
            
            # Assicurati che sia esattamente crop_size x crop_size
            if cropped_data.shape[1] != crop_size or cropped_data.shape[2] != crop_size:
                cropped_data = self._resize_crop(cropped_data, crop_size)
            
            # Salva il crop
            self._save_crop(cropped_data, output_path)
            
            return True
            
        except Exception as e:
            print(f"Errore durante il crop: {e}")
            return False
    
    def _adjust_crop_bounds(
        self, 
        center_x: int, 
        center_y: int, 
        crop_size: int, 
        img_width: int, 
        img_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Aggiusta i bounds del crop per rimanere dentro l'immagine
        
        Returns:
            Tuple (x1, y1, x2, y2) dei bounds aggiustati
        """
        half_size = crop_size // 2
        
        # Calcola bounds ideali
        x1 = center_x - half_size
        y1 = center_y - half_size
        x2 = center_x + half_size
        y2 = center_y + half_size
        
        # Aggiusta se fuori dai bounds
        if x1 < 0:
            x2 += abs(x1)
            x1 = 0
        elif x2 > img_width:
            x1 -= (x2 - img_width)
            x2 = img_width
        
        if y1 < 0:
            y2 += abs(y1)
            y1 = 0
        elif y2 > img_height:
            y1 -= (y2 - img_height)
            y2 = img_height
        
        # Assicurati che rimanga dentro i bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(img_width, x2)
        y2 = min(img_height, y2)
        
        return x1, y1, x2, y2
    
    def _resize_crop(self, crop_data: np.ndarray, target_size: int) -> np.ndarray:
        """
        Ridimensiona il crop alla dimensione target
        
        Args:
            crop_data: Dati del crop (bands, height, width)
            target_size: Dimensione target
            
        Returns:
            Crop ridimensionato
        """
        bands, height, width = crop_data.shape
        
        if height == target_size and width == target_size:
            return crop_data
        
        # Ridimensiona ogni banda separatamente
        resized_bands = []
        
        for band_idx in range(bands):
            band_data = crop_data[band_idx]
            
            # Converti in PIL Image per ridimensionamento
            if band_data.dtype == np.uint8:
                pil_img = Image.fromarray(band_data, mode='L')
            else:
                # Normalizza per PIL
                normalized = ((band_data - band_data.min()) / 
                            (band_data.max() - band_data.min()) * 255).astype(np.uint8)
                pil_img = Image.fromarray(normalized, mode='L')
            
            # Ridimensiona
            resized_pil = pil_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Riconverti in numpy
            if band_data.dtype != np.uint8:
                # Riporta al range originale
                resized_array = np.array(resized_pil, dtype=np.float32)
                resized_array = (resized_array / 255.0 * 
                               (band_data.max() - band_data.min()) + band_data.min())
                resized_array = resized_array.astype(band_data.dtype)
            else:
                resized_array = np.array(resized_pil)
            
            resized_bands.append(resized_array)
        
        return np.stack(resized_bands, axis=0)
    
    def _save_crop(self, crop_data: np.ndarray, output_path: str):
        """
        Salva il crop come file TIFF
        
        Args:
            crop_data: Dati del crop (bands, height, width)
            output_path: Percorso di output
        """
        # Crea directory se non esiste
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Salva come TIFF multibanda
        tifffile.imwrite(output_path, crop_data, photometric='minisblack')
    
    def crop_from_file(
        self,
        input_path: str,
        center_x: int,
        center_y: int,
        crop_size: int,
        output_path: str,
        preserve_bands: bool = True
    ) -> bool:
        """
        Ritaglia un'immagine direttamente da file
        
        Args:
            input_path: Percorso del file di input
            center_x: Coordinata X del centro del crop
            center_y: Coordinata Y del centro del crop
            crop_size: Dimensione del lato del quadrato
            output_path: Percorso di output del file
            preserve_bands: Se True mantiene tutte le bande
            
        Returns:
            True se il crop è stato salvato con successo
        """
        try:
            # Carica immagine
            image_data = tifffile.imread(input_path)
            
            # Verifica formato
            if len(image_data.shape) == 2:
                # Immagine singola banda, aggiungi dimensione banda
                image_data = image_data[np.newaxis, :, :]
            elif len(image_data.shape) == 3 and image_data.shape[2] < image_data.shape[0]:
                # Probabilmente formato (height, width, bands), trasponi
                image_data = np.transpose(image_data, (2, 0, 1))
            
            return self.crop_multispectral_image(
                image_data, center_x, center_y, crop_size, output_path, preserve_bands
            )
            
        except Exception as e:
            print(f"Errore durante il caricamento del file {input_path}: {e}")
            return False
    
    def get_crop_info(
        self,
        image_shape: Tuple[int, int, int],
        center_x: int,
        center_y: int,
        crop_size: int
    ) -> dict:
        """
        Ottieni informazioni sul crop senza eseguirlo
        
        Args:
            image_shape: Forma dell'immagine (bands, height, width)
            center_x: Coordinata X del centro
            center_y: Coordinata Y del centro
            crop_size: Dimensione del crop
            
        Returns:
            Dizionario con informazioni sul crop
        """
        bands, height, width = image_shape
        
        # Calcola bounds
        half_size = crop_size // 2
        x1 = max(0, center_x - half_size)
        y1 = max(0, center_y - half_size)
        x2 = min(width, center_x + half_size)
        y2 = min(height, center_y + half_size)
        
        actual_width = x2 - x1
        actual_height = y2 - y1
        
        # Verifica validità
        is_valid = actual_width >= crop_size and actual_height >= crop_size
        
        # Calcola bounds aggiustati se necessario
        if not is_valid:
            x1_adj, y1_adj, x2_adj, y2_adj = self._adjust_crop_bounds(
                center_x, center_y, crop_size, width, height
            )
            actual_width_adj = x2_adj - x1_adj
            actual_height_adj = y2_adj - y1_adj
            can_adjust = actual_width_adj >= crop_size and actual_height_adj >= crop_size
        else:
            can_adjust = True
            x1_adj, y1_adj, x2_adj, y2_adj = x1, y1, x2, y2
        
        return {
            'is_valid': is_valid,
            'can_adjust': can_adjust,
            'original_bounds': (x1, y1, x2, y2),
            'adjusted_bounds': (x1_adj, y1_adj, x2_adj, y2_adj),
            'actual_size': (actual_width, actual_height),
            'center': (center_x, center_y),
            'crop_size': crop_size
        }
