#!/usr/bin/env python3
"""
Project Manager - Gestione progetti per labeling

Gestisce la creazione e organizzazione di progetti per il labeling
di immagini multispettrali con struttura semplificata.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil


class ProjectManager:
    """Gestore progetti semplificato per labeling"""
    
    def __init__(self, projects_base_dir: str = None):
        """
        Inizializza il gestore progetti
        
        Args:
            projects_base_dir: Directory base per i progetti (default: ./projects)
        """
        if projects_base_dir is None:
            # Directory di default relativa al modulo
            current_dir = Path(__file__).parent.parent.parent
            projects_base_dir = current_dir / "projects"
        
        self.projects_dir = Path(projects_base_dir)
        self.projects_dir.mkdir(exist_ok=True)
        
        # Stato corrente
        self.current_project = None
        self.current_project_path = None
        self.project_metadata = {}
        
        # Flag per tracking stato
        self.images_loaded = False
        self.crops_saved = False
    
    def create_project(self, project_name: Optional[str] = None, 
                      source_paths: List[str] = None) -> str:
        """
        Crea un nuovo progetto con struttura semplificata
        
        Args:
            project_name: Nome del progetto (auto-generato se None)
            source_paths: Path delle immagini sorgente
            
        Returns:
            Path del progetto creato
        """
        # Auto-genera nome se non fornito
        if not project_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = f"labeling_project_{timestamp}"
        
        # Sanitizza nome progetto
        safe_name = "".join(c for c in project_name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            safe_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_path = self.projects_dir / safe_name
        
        # Verifica se esiste già
        if project_path.exists():
            counter = 1
            while (self.projects_dir / f"{safe_name}_{counter}").exists():
                counter += 1
            safe_name = f"{safe_name}_{counter}"
            project_path = self.projects_dir / safe_name
        
        # Crea struttura progetto semplificata
        project_path.mkdir(exist_ok=True)
        
        # Sottocartelle richieste
        folders = [
            "originals",    # Immagini originali
            "crops"         # Crop salvati
        ]
        
        for folder in folders:
            (project_path / folder).mkdir(exist_ok=True)
        
        # Crea metadata del progetto
        metadata = {
            "project_name": project_name,
            "safe_name": safe_name,
            "description": f"Progetto labeling multispettrale",
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "gui_type": "labeling",
            "structure": {
                "originals": "Immagini originali caricate",
                "crops": "Crop salvati dalla GUI"
            },
            "source_info": self._analyze_source_paths(source_paths),
            "crops": [],
            "statistics": {
                "total_crops": 0,
                "total_images_processed": 0
            }
        }
        
        with open(project_path / "project_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Imposta come progetto corrente
        self.current_project = safe_name
        self.current_project_path = str(project_path)
        self.project_metadata = metadata
        
        # Reset flag
        self.images_loaded = False
        self.crops_saved = False
        
        return str(project_path)
    
    def _analyze_source_paths(self, source_paths: List[str]) -> Dict[str, Any]:
        """Analizza i path sorgente per metadata"""
        if not source_paths:
            return {"type": "none", "count": 0, "paths": []}

        info = {
            "paths": source_paths,
            "count": len(source_paths),
            "analyzed_date": datetime.now().isoformat()
        }

        # Determina tipo di selezione
        if len(source_paths) == 1:
            path = Path(source_paths[0])
            if path.is_file():
                info["type"] = "single_file"
                info["file_info"] = {
                    "name": path.name,
                    "size_mb": path.stat().st_size / (1024 * 1024) if path.exists() else 0
                }
            elif path.is_dir():
                info["type"] = "folder"
                # Conta file TIFF nella cartella e salva lista
                tiff_files = list(path.glob("*.tif")) + list(path.glob("*.tiff"))
                info["tiff_count"] = len(tiff_files)
                info["folder_name"] = path.name
                info["tiff_files"] = [str(f) for f in sorted(tiff_files)]  # Lista completa file TIFF
        else:
            info["type"] = "multiple_files"
            info["file_names"] = [Path(p).name for p in source_paths]

        return info

    def get_source_files_for_loading(self) -> tuple:
        """
        Restituisce i file sorgente in formato compatibile con FileSelector

        Returns:
            Tuple (selected_paths, selection_type) per FileSelector
        """
        if not self.project_metadata:
            return [], "none"

        source_info = self.project_metadata.get("source_info", {})
        source_type = source_info.get("type", "none")
        source_paths = source_info.get("paths", [])

        if source_type == "none" or not source_paths:
            return [], "none"

        # Verifica che i path esistano ancora
        valid_paths = []
        for path in source_paths:
            if os.path.exists(path):
                valid_paths.append(path)

        if not valid_paths:
            print("Attenzione: I file sorgente originali non sono più disponibili")
            return [], "none"

        # Mappa i tipi del progetto ai tipi del FileSelector
        if source_type == "single_file":
            return valid_paths, "single_file"
        elif source_type == "multiple_files":
            return valid_paths, "multiple_files"
        elif source_type == "folder":
            return valid_paths, "folder"
        else:
            return valid_paths, "multiple_files"  # Fallback
    
    def add_crop(self, crop_path: str, original_image: str, 
                coordinates: tuple, crop_size: int, view_mode: str = "unknown"):
        """
        Registra un nuovo crop nel progetto
        
        Args:
            crop_path: Path del file crop salvato
            original_image: Path dell'immagine originale
            coordinates: Coordinate del centro del crop (x, y)
            crop_size: Dimensione del crop
            view_mode: Modalità di visualizzazione usata
        """
        if not self.current_project:
            return
        
        crop_info = {
            "crop_file": os.path.basename(crop_path),
            "crop_path": crop_path,
            "original_image": original_image,
            "original_name": os.path.basename(original_image),
            "coordinates": coordinates,
            "crop_size": crop_size,
            "view_mode": view_mode,
            "created_date": datetime.now().isoformat(),
            "file_size_mb": Path(crop_path).stat().st_size / (1024 * 1024) if Path(crop_path).exists() else 0
        }
        
        self.project_metadata["crops"].append(crop_info)
        self.project_metadata["statistics"]["total_crops"] += 1
        self.project_metadata["last_modified"] = datetime.now().isoformat()
        
        # Salva metadata aggiornati
        self._save_metadata()
    
    def get_project_paths(self) -> Dict[str, str]:
        """Restituisce i path delle cartelle del progetto"""
        if not self.current_project_path:
            return {}
        
        base_path = Path(self.current_project_path)
        return {
            "project": str(base_path),
            "originals": str(base_path / "originals"),
            "crops": str(base_path / "crops")
        }
    
    def get_source_info(self) -> Dict[str, Any]:
        """Restituisce informazioni sui file sorgente"""
        return self.project_metadata.get("source_info", {})
    
    def mark_images_loaded(self):
        """Marca che sono state caricate immagini"""
        self.images_loaded = True
    
    def mark_crop_saved(self):
        """Marca che è stato salvato un crop"""
        self.crops_saved = True
    
    def cleanup_empty_project(self):
        """Pulisce il progetto se vuoto (nessun crop salvato)"""
        if not self.current_project_path or self.crops_saved:
            return
        
        try:
            project_path = Path(self.current_project_path)
            
            # Verifica se ci sono crop salvati
            crops_dir = project_path / "crops"
            if crops_dir.exists():
                crop_files = list(crops_dir.glob("*.tif")) + list(crops_dir.glob("*.tiff"))
                if crop_files:
                    return  # Ci sono crop, non eliminare
            
            # Verifica se ci sono file nelle altre cartelle
            has_files = False
            for subdir in ["originals"]:
                subdir_path = project_path / subdir
                if subdir_path.exists():
                    files = list(subdir_path.iterdir())
                    if files:
                        has_files = True
                        break
            
            # Se non ci sono file significativi, elimina il progetto
            if not has_files:
                shutil.rmtree(project_path)
                print(f"Progetto vuoto eliminato: {self.current_project}")
        
        except Exception as e:
            print(f"Errore durante cleanup progetto: {e}")
    
    def _save_metadata(self):
        """Salva i metadata del progetto"""
        if not self.current_project_path:
            return
        
        metadata_path = Path(self.current_project_path) / "project_metadata.json"
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Errore salvataggio metadata: {e}")
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """Restituisce statistiche del progetto"""
        if not self.current_project:
            return {}
        
        stats = self.project_metadata.get("statistics", {})
        
        # Aggiorna statistiche in tempo reale
        if self.current_project_path:
            crops_dir = Path(self.current_project_path) / "crops"
            if crops_dir.exists():
                crop_files = list(crops_dir.glob("*.tif")) + list(crops_dir.glob("*.tiff"))
                stats["actual_crop_files"] = len(crop_files)
        
        return stats
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Lista tutti i progetti disponibili"""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "project_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        projects.append({
                            "name": metadata.get("project_name", project_dir.name),
                            "safe_name": project_dir.name,
                            "path": str(project_dir),
                            "created_date": metadata.get("created_date"),
                            "last_modified": metadata.get("last_modified"),
                            "gui_type": metadata.get("gui_type", "unknown"),
                            "crop_count": len(metadata.get("crops", []))
                        })
                    except Exception as e:
                        print(f"Errore lettura metadata per {project_dir.name}: {e}")
        
        return sorted(projects, key=lambda x: x.get("last_modified", ""), reverse=True)

    def load_project(self, project_path: str) -> bool:
        """
        Carica un progetto esistente

        Args:
            project_path: Percorso del progetto da caricare

        Returns:
            True se caricamento riuscito
        """
        try:
            project_path = Path(project_path)

            # Verifica che il progetto esista
            if not project_path.exists() or not project_path.is_dir():
                print(f"Progetto non trovato: {project_path}")
                return False

            # Verifica che ci sia il file metadata
            metadata_file = project_path / "project_metadata.json"
            if not metadata_file.exists():
                print(f"File metadata non trovato: {metadata_file}")
                return False

            # Carica metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Imposta come progetto corrente
            self.current_project = metadata.get("safe_name", project_path.name)
            self.current_project_path = str(project_path)
            self.project_metadata = metadata

            # Aggiorna timestamp ultimo accesso
            self.project_metadata["last_accessed"] = datetime.now().isoformat()
            self._save_metadata()

            # Reset flag
            self.images_loaded = False
            self.crops_saved = len(metadata.get("crops", [])) > 0

            print(f"Progetto caricato: {self.current_project}")
            return True

        except Exception as e:
            print(f"Errore caricamento progetto {project_path}: {e}")
            return False

    def get_project_info(self) -> dict:
        """Restituisce informazioni complete del progetto corrente"""
        if not self.current_project:
            return {}

        info = {
            "name": self.project_metadata.get("project_name", "N/A"),
            "safe_name": self.current_project,
            "path": self.current_project_path,
            "created_date": self.project_metadata.get("created_date"),
            "last_modified": self.project_metadata.get("last_modified"),
            "last_accessed": self.project_metadata.get("last_accessed"),
            "description": self.project_metadata.get("description", ""),
            "gui_type": self.project_metadata.get("gui_type", "unknown"),
            "crops_count": len(self.project_metadata.get("crops", [])),
            "source_info": self.project_metadata.get("source_info", {}),
            "statistics": self.project_metadata.get("statistics", {})
        }

        return info

    def add_source_images(self, new_source_paths: List[str]) -> bool:
        """
        Aggiunge nuove immagini sorgente al progetto corrente

        Args:
            new_source_paths: Lista dei nuovi path da aggiungere

        Returns:
            True se aggiunta riuscita
        """
        if not self.current_project or not new_source_paths:
            return False

        try:
            # Ottieni info sorgenti correnti
            current_source_info = self.project_metadata.get("source_info", {})
            current_paths = current_source_info.get("paths", [])

            # Combina path esistenti con nuovi (evita duplicati)
            all_paths = list(current_paths)
            for path in new_source_paths:
                if path not in all_paths:
                    all_paths.append(path)

            # Aggiorna source_info
            updated_source_info = self._analyze_source_paths(all_paths)
            updated_source_info["last_updated"] = datetime.now().isoformat()
            updated_source_info["added_images"] = len(new_source_paths)

            # Salva nel metadata
            self.project_metadata["source_info"] = updated_source_info
            self.project_metadata["last_modified"] = datetime.now().isoformat()

            # Salva metadata aggiornati
            self._save_metadata()

            print(f"Aggiunte {len(new_source_paths)} nuove immagini al progetto {self.current_project}")
            return True

        except Exception as e:
            print(f"Errore aggiunta immagini al progetto: {e}")
            return False

    def has_active_project(self) -> bool:
        """Verifica se c'è un progetto attivo"""
        return self.current_project is not None and self.current_project_path is not None
