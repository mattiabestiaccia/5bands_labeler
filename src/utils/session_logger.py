#!/usr/bin/env python3
"""
Session Logger - Logging delle sessioni di labeling

Crea un file di log per ogni sessione di lavoro all'interno
della cartella del progetto corrente, tracciando tutte le attività.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class SessionLogger:
    """Gestore logging sessioni di labeling"""
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Inizializza il logger della sessione
        
        Args:
            project_path: Path del progetto corrente
        """
        self.project_path = project_path
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start = datetime.now().isoformat()
        self.log_file_path = None
        
        # Dati della sessione
        self.session_data = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.session_start,
                "end_time": None,
                "project_path": project_path,
                "total_duration_seconds": 0
            },
            "activities": [],
            "statistics": {
                "images_loaded": 0,
                "crops_created": 0,
                "view_mode_changes": 0,
                "coordinates_selected": 0,
                "files_processed": set()
            }
        }
        
        if project_path:
            self.setup_log_file()
    
    def setup_log_file(self):
        """Configura il file di log nella cartella del progetto"""
        if not self.project_path:
            return
        
        project_dir = Path(self.project_path)
        if not project_dir.exists():
            return
        
        # Nome file log con timestamp
        log_filename = f"session_log_{self.session_id}.json"
        self.log_file_path = project_dir / log_filename
        
        # Salva dati iniziali della sessione
        self._save_log()
        
        # Log attività di inizio sessione
        self.log_activity("session_start", {
            "session_id": self.session_id,
            "project_path": self.project_path
        })
    
    def log_activity(self, activity_type: str, details: Dict[str, Any] = None):
        """
        Registra un'attività nella sessione
        
        Args:
            activity_type: Tipo di attività (es. 'image_loaded', 'crop_created')
            details: Dettagli specifici dell'attività
        """
        if details is None:
            details = {}
        
        timestamp = datetime.now().isoformat()
        
        activity = {
            "timestamp": timestamp,
            "type": activity_type,
            "details": details
        }
        
        self.session_data["activities"].append(activity)
        
        # Aggiorna statistiche
        self._update_statistics(activity_type, details)
        
        # Salva aggiornamenti se il file è configurato
        if self.log_file_path:
            self._save_log()
    
    def _update_statistics(self, activity_type: str, details: Dict[str, Any]):
        """Aggiorna le statistiche della sessione"""
        stats = self.session_data["statistics"]
        
        # Assicura che files_processed sia un set
        if not isinstance(stats["files_processed"], set):
            stats["files_processed"] = set(stats["files_processed"])
        
        if activity_type == "image_loaded":
            stats["images_loaded"] += 1
            file_path = details.get("file_path")
            if file_path:
                stats["files_processed"].add(file_path)
        
        elif activity_type == "crop_created":
            stats["crops_created"] += 1
        
        elif activity_type == "view_mode_changed":
            stats["view_mode_changes"] += 1
        
        elif activity_type == "coordinate_selected":
            stats["coordinates_selected"] += 1
    
    def log_image_loaded(self, file_path: str, image_shape: tuple = None, 
                        bands: int = None):
        """Log caricamento immagine"""
        details = {
            "file_path": file_path,
            "filename": os.path.basename(file_path)
        }
        
        if image_shape:
            details["image_shape"] = image_shape
        if bands:
            details["bands"] = bands
        
        self.log_activity("image_loaded", details)
    
    def log_crop_created(self, crop_path: str, original_image: str,
                        coordinates: tuple, crop_size: int, view_mode: str):
        """Log creazione crop"""
        details = {
            "crop_path": crop_path,
            "crop_filename": os.path.basename(crop_path),
            "original_image": original_image,
            "original_filename": os.path.basename(original_image),
            "coordinates": coordinates,
            "crop_size": crop_size,
            "view_mode": view_mode
        }
        
        self.log_activity("crop_created", details)
    
    def log_view_mode_changed(self, new_mode: str, previous_mode: str = None):
        """Log cambio modalità visualizzazione"""
        details = {
            "new_mode": new_mode
        }
        if previous_mode:
            details["previous_mode"] = previous_mode
        
        self.log_activity("view_mode_changed", details)
    
    def log_coordinate_selected(self, coordinates: tuple, image_file: str = None):
        """Log selezione coordinate"""
        details = {
            "coordinates": coordinates
        }
        if image_file:
            details["image_file"] = image_file
            details["image_filename"] = os.path.basename(image_file)
        
        self.log_activity("coordinate_selected", details)
    
    def log_project_action(self, action: str, project_info: Dict[str, Any] = None):
        """Log azioni relative al progetto"""
        details = {"action": action}
        if project_info:
            details.update(project_info)
        
        self.log_activity("project_action", details)
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log errori"""
        details = {
            "error_type": error_type,
            "error_message": error_message
        }
        if context:
            details["context"] = context
        
        self.log_activity("error", details)
    
    def end_session(self):
        """Termina la sessione e salva i dati finali"""
        end_time = datetime.now().isoformat()
        self.session_data["session_info"]["end_time"] = end_time
        
        # Calcola durata totale
        start_dt = datetime.fromisoformat(self.session_start)
        end_dt = datetime.now()
        duration = (end_dt - start_dt).total_seconds()
        self.session_data["session_info"]["total_duration_seconds"] = round(duration, 2)
        
        # Converti set a lista per serializzazione JSON
        self.session_data["statistics"]["files_processed"] = list(
            self.session_data["statistics"]["files_processed"]
        )
        
        # Log attività di fine sessione
        self.log_activity("session_end", {
            "duration_seconds": duration,
            "total_activities": len(self.session_data["activities"]),
            "total_crops": self.session_data["statistics"]["crops_created"]
        })
        
        # Salva log finale
        if self.log_file_path:
            self._save_log()
    
    def _save_log(self):
        """Salva il log su file"""
        if not self.log_file_path:
            return
        
        try:
            # Prepara dati per serializzazione
            data_to_save = self.session_data.copy()
            
            # Converti set a lista se necessario
            if isinstance(data_to_save["statistics"]["files_processed"], set):
                data_to_save["statistics"]["files_processed"] = list(
                    data_to_save["statistics"]["files_processed"]
                )
            
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Errore salvataggio log sessione: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Restituisce un riassunto della sessione corrente"""
        stats = self.session_data["statistics"].copy()
        
        # Converti set a lista per il riassunto
        if isinstance(stats["files_processed"], set):
            stats["files_processed"] = list(stats["files_processed"])
        
        return {
            "session_id": self.session_id,
            "start_time": self.session_start,
            "activities_count": len(self.session_data["activities"]),
            "statistics": stats,
            "log_file": str(self.log_file_path) if self.log_file_path else None
        }
    
    def set_project_path(self, project_path: str):
        """Imposta il path del progetto e configura il logging"""
        self.project_path = project_path
        self.session_data["session_info"]["project_path"] = project_path
        
        if project_path:
            self.setup_log_file()