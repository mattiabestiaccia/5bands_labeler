#!/usr/bin/env python3
"""
Script per creare una versione augmented del dataset squares con 20 immagini per classe.

Applica trasformazioni leggere per preservare le caratteristiche delle immagini:
- Rotazioni (90°, 180°, 270°)
- Flip orizzontale e verticale
- Piccole variazioni di luminosità e contrasto
- Leggero rumore gaussiano

Autore: Augment Agent
Data: 2025-06-20
"""

import os
import cv2
import numpy as np
from pathlib import Path
import random
from tqdm import tqdm
import argparse

def load_image_safely(img_path):
    """Carica un'immagine gestendo i problemi con i file TIFF a 32-bit"""
    try:
        img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
        if img is None:
            print(f"⚠️  Impossibile caricare: {img_path}")
            return None
        return img
    except Exception as e:
        print(f"❌ Errore nel caricamento di {img_path}: {e}")
        return None

def apply_rotation(img, angle):
    """Applica rotazione di 90°, 180° o 270°"""
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return img

def apply_flip(img, flip_type):
    """Applica flip orizzontale (1) o verticale (0)"""
    return cv2.flip(img, flip_type)

def apply_brightness_contrast(img, brightness=0, contrast=1.0):
    """Applica variazioni di luminosità e contrasto"""
    return cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

def apply_gaussian_noise(img, mean=0, std=5):
    """Aggiunge rumore gaussiano leggero"""
    noise = np.random.normal(mean, std, img.shape).astype(np.uint8)
    return cv2.add(img, noise)

def augment_image(img, augmentation_type):
    """Applica una specifica trasformazione all'immagine"""
    if augmentation_type == 'rot90':
        return apply_rotation(img, 90)
    elif augmentation_type == 'rot180':
        return apply_rotation(img, 180)
    elif augmentation_type == 'rot270':
        return apply_rotation(img, 270)
    elif augmentation_type == 'flip_h':
        return apply_flip(img, 1)
    elif augmentation_type == 'flip_v':
        return apply_flip(img, 0)
    elif augmentation_type == 'bright_up':
        return apply_brightness_contrast(img, brightness=10, contrast=1.1)
    elif augmentation_type == 'bright_down':
        return apply_brightness_contrast(img, brightness=-10, contrast=0.9)
    elif augmentation_type == 'contrast_up':
        return apply_brightness_contrast(img, brightness=0, contrast=1.2)
    elif augmentation_type == 'contrast_down':
        return apply_brightness_contrast(img, brightness=0, contrast=0.8)
    elif augmentation_type == 'noise':
        return apply_gaussian_noise(img, std=3)
    else:
        return img

def create_augmented_dataset(input_dir, output_dir, target_images_per_class=20):
    """
    Crea un dataset augmented con il numero target di immagini per classe
    
    Args:
        input_dir: Directory del dataset originale
        output_dir: Directory dove salvare il dataset augmented
        target_images_per_class: Numero target di immagini per classe
    """
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Crea la directory di output
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Definisci le trasformazioni disponibili
    augmentations = [
        'rot90', 'rot180', 'rot270',
        'flip_h', 'flip_v',
        'bright_up', 'bright_down',
        'contrast_up', 'contrast_down',
        'noise'
    ]
    
    print(f"🔄 Creazione dataset augmented: {target_images_per_class} immagini per classe")
    print(f"📁 Input: {input_dir}")
    print(f"📁 Output: {output_dir}")
    
    # Processa ogni classe
    for class_dir in input_path.iterdir():
        if not class_dir.is_dir():
            continue
            
        class_name = class_dir.name
        print(f"\n🏷️  Processando classe: {class_name}")
        
        # Crea directory di output per la classe
        output_class_dir = output_path / class_name
        output_class_dir.mkdir(exist_ok=True)
        
        # Carica tutte le immagini originali della classe
        original_images = []
        image_files = []
        
        for img_file in class_dir.glob("*.tif"):
            img = load_image_safely(img_file)
            if img is not None:
                original_images.append(img)
                image_files.append(img_file)
        
        print(f"   📸 Immagini originali caricate: {len(original_images)}")
        
        if len(original_images) == 0:
            print(f"   ⚠️  Nessuna immagine valida trovata per {class_name}")
            continue
        
        # Salva le immagini originali
        for i, (img, img_file) in enumerate(zip(original_images, image_files)):
            output_filename = f"{class_name}_original_{i:03d}.png"
            output_filepath = output_class_dir / output_filename
            cv2.imwrite(str(output_filepath), img)
        
        # Calcola quante immagini augmented servono
        images_needed = target_images_per_class - len(original_images)
        
        if images_needed <= 0:
            print(f"   ✅ Classe {class_name} ha già {len(original_images)} immagini (target: {target_images_per_class})")
            continue
        
        print(f"   🔄 Generando {images_needed} immagini augmented...")
        
        # Genera immagini augmented
        augmented_count = 0
        
        with tqdm(total=images_needed, desc=f"   Augmenting {class_name}") as pbar:
            while augmented_count < images_needed:
                # Scegli un'immagine originale casuale
                base_img = random.choice(original_images)
                
                # Scegli una trasformazione casuale
                aug_type = random.choice(augmentations)
                
                # Applica la trasformazione
                augmented_img = augment_image(base_img, aug_type)
                
                # Salva l'immagine augmented
                output_filename = f"{class_name}_aug_{aug_type}_{augmented_count:03d}.png"
                output_filepath = output_class_dir / output_filename
                cv2.imwrite(str(output_filepath), augmented_img)
                
                augmented_count += 1
                pbar.update(1)
        
        total_images = len(original_images) + augmented_count
        print(f"   ✅ Classe {class_name} completata: {total_images} immagini totali")
    
    print(f"\n🎉 Dataset augmented creato con successo in: {output_dir}")
    
    # Stampa statistiche finali
    print("\n📊 Statistiche finali:")
    for class_dir in output_path.iterdir():
        if class_dir.is_dir():
            num_images = len(list(class_dir.glob("*.png")))
            print(f"   {class_dir.name}: {num_images} immagini")

def main():
    parser = argparse.ArgumentParser(description="Crea dataset augmented del dataset squares")
    parser.add_argument("--input", "-i", 
                       default="/home/brus/Projects/HPL/paper/Poplar/data/datasets/squares",
                       help="Directory del dataset originale")
    parser.add_argument("--output", "-o",
                       default="/home/brus/Projects/HPL/paper/Poplar/data/datasets/squares_augmented",
                       help="Directory di output per il dataset augmented")
    parser.add_argument("--target", "-t", type=int, default=20,
                       help="Numero target di immagini per classe")
    
    args = parser.parse_args()
    
    create_augmented_dataset(args.input, args.output, args.target)

if __name__ == "__main__":
    main()
