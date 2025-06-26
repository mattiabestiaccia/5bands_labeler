#!/usr/bin/env python3
"""
Labeling GUI - Interfaccia principale per labeling immagini multispettrali

Interfaccia che include:
- Caricamento immagini
- Creazione progetti
- Visualizzazione con click per coordinate
- Controlli crop
- Salvataggio crop
- Cleanup automatico progetti vuoti
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path
from typing import List, Tuple
import numpy as np

from gui.file_selector import FileSelector
from gui.coordinate_viewer import CoordinateViewer
from gui.crop_controls import CropControls
from gui.project_selector import ProjectSelectorDialog
from core.project_manager import ProjectManager
from core.image_cropper import ImageCropper


class LabelingGUI:
    """Interfaccia principale per labeling immagini multispettrali"""
    
    def __init__(self):
        """Inizializza l'interfaccia principale"""
        self.root = tk.Tk()
        self.root.title("Labeler Multispettrale 5 Bande")
        self.root.geometry("1600x1000")
        
        # Managers
        self.project_manager = ProjectManager()
        self.image_cropper = ImageCropper()
        
        # Stato applicazione
        self.current_project_path = None
        self.current_image_data = None
        self.current_image_file = None
        
        self.setup_ui()
        self.setup_menu()
        
        # Gestione chiusura finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale con pannelli
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pannello sinistro - Controlli
        left_frame = ttk.Frame(main_paned, width=450)
        main_paned.add(left_frame, weight=1)
        
        # Pannello destro - Visualizzazione
        right_frame = ttk.Frame(main_paned, width=1150)
        main_paned.add(right_frame, weight=2)
        
        # === PANNELLO SINISTRO ===
        
        # Selettore file
        self.file_selector = FileSelector(
            left_frame,
            self.on_selection_change,
            self.on_file_double_click,
            self._has_active_project
        )
        
        # Informazioni progetto
        self.setup_project_info(left_frame)
        
        # Controlli crop
        self.crop_controls = CropControls(left_frame, self.on_crop_save, self.on_crop_size_change, 
                                        self.on_superpixel_generated, self.on_superpixel_mode_change)
        
        # === PANNELLO DESTRO ===
        
        # Visualizzatore con coordinate
        self.coordinate_viewer = CoordinateViewer(right_frame, self.on_coordinate_click)
        self.coordinate_viewer.on_superpixel_selected = self.on_superpixel_selected
        self.coordinate_viewer.on_view_mode_change = self.on_view_mode_change
        
        # Barra di stato
        self.setup_status_bar()
    
    def setup_project_info(self, parent):
        """Configura il pannello informazioni progetto"""
        self.project_frame = ttk.LabelFrame(parent, text="Progetto Corrente", padding=10)
        self.project_frame.pack(fill="x", padx=10, pady=5)
        
        # Nome progetto
        name_frame = ttk.Frame(self.project_frame)
        name_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(name_frame, text="Nome:").pack(side="left")
        self.project_name_var = tk.StringVar()
        self.project_name_entry = ttk.Entry(name_frame, textvariable=self.project_name_var)
        self.project_name_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Bottoni progetto
        buttons_frame = ttk.Frame(self.project_frame)
        buttons_frame.pack(fill="x")

        ttk.Button(buttons_frame, text="📁 Nuovo Progetto",
                  command=self.create_new_project).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="🗂️ Apri Cartella",
                  command=self.open_project_folder).pack(side="left")
        
        # Info progetto
        self.project_info_label = ttk.Label(self.project_frame, 
                                           text="Nessun progetto attivo", 
                                           foreground="gray")
        self.project_info_label.pack(anchor="w", pady=(5, 0))
    
    def setup_status_bar(self):
        """Configura la barra di stato"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill="x", side="bottom")
        
        self.status_label = ttk.Label(self.status_frame, text="Pronto - Labeler Multispettrale")
        self.status_label.pack(side="left", padx=5)
        
        # Indicatore progetto
        self.project_status_label = ttk.Label(self.status_frame, text="Nessun progetto")
        self.project_status_label.pack(side="right", padx=5)
    
    def setup_menu(self):
        """Configura il menu principale"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Nuovo Progetto", command=self.create_new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.on_closing)
        
        # Menu Visualizza
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizza", menu=view_menu)
        view_menu.add_command(label="Apri Cartella Progetto", command=self.open_project_folder)
        
        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
    
    def on_selection_change(self, selected_paths, selection_type):
        """Gestisce il cambio di selezione file"""
        self.log(f"Selezione: {selection_type} - {len(selected_paths)} elementi")

        if selected_paths:
            if self.current_project_path:
                # C'è già un progetto attivo, aggiungi le immagini
                self.add_images_to_current_project(selected_paths)
            else:
                # Nessun progetto attivo, crea nuovo progetto
                self.create_new_project()

        # Carica automaticamente la prima immagine nel visualizzatore
        self.load_first_image_in_viewer(selected_paths, selection_type)

    def _has_active_project(self) -> bool:
        """Callback per verificare se c'è un progetto attivo"""
        return self.project_manager.has_active_project()

    def load_first_image_in_viewer(self, selected_paths, selection_type):
        """Carica la prima immagine disponibile nel visualizzatore"""
        if not selected_paths:
            return

        try:
            first_image_path = None

            if selection_type == "single_file":
                first_image_path = selected_paths[0]
            elif selection_type == "multiple_files":
                first_image_path = selected_paths[0]
            elif selection_type == "folder":
                # Trova il primo file TIFF nella cartella
                tiff_files = self.file_selector._find_tiff_files(selected_paths[0])
                if tiff_files:
                    first_image_path = tiff_files[0]

            if first_image_path and os.path.exists(first_image_path):
                success = self.coordinate_viewer.load_image(first_image_path)
                if success:
                    self.current_image_file = first_image_path
                    self.current_image_data = self.coordinate_viewer.bands_data
                    
                    # Aggiorna controlli crop con info immagine
                    if self.current_image_data is not None:
                        height, width = self.current_image_data.shape[1], self.current_image_data.shape[2]
                        self.crop_controls.set_image_info(
                            os.path.basename(first_image_path), width, height
                        )
                        
                        # Passa i dati immagine ai controlli crop per superpixel
                        view_mode = getattr(self.coordinate_viewer, 'view_mode', 'rgb')
                        self.crop_controls.set_current_image_data(
                            self.current_image_data, 'multispectral', view_mode
                        )
                    
                    # Marca immagine caricata con informazioni per il log
                    image_shape = self.current_image_data.shape if self.current_image_data is not None else None
                    bands = self.current_image_data.shape[0] if self.current_image_data is not None else None
                    self.project_manager.mark_images_loaded(first_image_path, image_shape, bands)
                    self.log(f"📷 Immagine caricata: {os.path.basename(first_image_path)}")
                else:
                    self.log(f"❌ Impossibile caricare: {os.path.basename(first_image_path)}")

        except Exception as e:
            self.log(f"❌ Errore caricamento immagine: {e}")

    def create_new_project(self):
        """Crea un nuovo progetto"""
        # Ottieni selezione corrente
        selected_paths, selection_type = self.file_selector.get_selection()
        
        # Nome progetto
        project_name = self.project_name_var.get().strip()
        if not project_name:
            project_name = None  # Auto-generato
        
        # Crea progetto
        try:
            project_path = self.project_manager.create_project(project_name, selected_paths)
            self.current_project_path = project_path

            # Imposta cartella crops nel visualizzatore
            project_paths = self.project_manager.get_project_paths()
            if "crops" in project_paths:
                self.coordinate_viewer.set_project_crops_dir(project_paths["crops"])

            # Aggiorna UI
            self.update_project_info()
            self.log(f"✅ Progetto creato: {os.path.basename(project_path)}")

        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile creare progetto:\n{e}")

    def add_images_to_current_project(self, new_paths: List[str]):
        """Aggiunge nuove immagini al progetto corrente"""
        try:
            if not self.project_manager.has_active_project():
                self.log("❌ Nessun progetto attivo per aggiungere immagini")
                return

            # Aggiunge le immagini al progetto
            success = self.project_manager.add_source_images(new_paths)

            if success:
                # Aggiorna informazioni progetto
                self.update_project_info()

                # Mostra messaggio di conferma
                project_info = self.project_manager.get_project_info()
                project_name = project_info.get("name", "N/A")

                self.log(f"✅ Aggiunte {len(new_paths)} immagini al progetto {project_name}")

                # Mostra notifica all'utente
                messagebox.showinfo(
                    "Immagini Aggiunte",
                    f"Aggiunte {len(new_paths)} nuove immagini al progetto:\n"
                    f"{project_name}\n\n"
                    f"Le nuove immagini sono ora disponibili per il labeling."
                )
            else:
                self.log("❌ Errore aggiunta immagini al progetto")
                messagebox.showerror("Errore", "Impossibile aggiungere le immagini al progetto")

        except Exception as e:
            self.log(f"❌ Errore aggiunta immagini: {e}")
            messagebox.showerror("Errore", f"Errore durante l'aggiunta delle immagini:\n{e}")

    def load_existing_project(self):
        """Carica un progetto esistente"""
        try:
            # Mostra finestra di selezione progetti
            dialog = ProjectSelectorDialog(self.root, self.project_manager, "Carica Progetto Esistente")
            selected_project = dialog.show()

            if not selected_project:
                return  # Utente ha annullato

            # Carica il progetto
            project_path = selected_project.get("path")
            if not project_path:
                messagebox.showerror("Errore", "Percorso progetto non valido")
                return

            success = self.project_manager.load_project(project_path)
            if success:
                self.current_project_path = project_path

                # Imposta cartella crops nel visualizzatore
                project_paths = self.project_manager.get_project_paths()
                if "crops" in project_paths:
                    self.coordinate_viewer.set_project_crops_dir(project_paths["crops"])

                # Aggiorna UI
                self.update_project_info()

                # Aggiorna nome progetto nel campo
                project_info = self.project_manager.get_project_info()
                if project_info:
                    self.project_name_var.set(project_info.get("name", ""))

                # Carica automaticamente le immagini sorgente
                self.load_project_source_images()

                self.log(f"✅ Progetto caricato: {selected_project.get('name', 'N/A')}")

                # Mostra informazioni progetto caricato
                crops_count = project_info.get("crops_count", 0)
                if crops_count > 0:
                    messagebox.showinfo(
                        "Progetto Caricato",
                        f"Progetto caricato con successo!\n\n"
                        f"Nome: {project_info.get('name', 'N/A')}\n"
                        f"Crop esistenti: {crops_count}\n"
                        f"Ultimo accesso: {project_info.get('last_accessed', 'N/A')}\n\n"
                        f"Immagini sorgente ricaricate automaticamente.\n"
                        f"Puoi continuare ad aggiungere nuovi crop."
                    )
            else:
                messagebox.showerror("Errore", "Impossibile caricare il progetto")

        except Exception as e:
            messagebox.showerror("Errore Caricamento", f"Errore durante il caricamento:\n{e}")

    def load_project_source_images(self):
        """Carica automaticamente le immagini sorgente del progetto"""
        try:
            # Ottieni i file sorgente dal progetto
            source_paths, selection_type = self.project_manager.get_source_files_for_loading()

            if not source_paths or selection_type == "none":
                self.log("⚠️ Nessuna immagine sorgente trovata nel progetto")
                return

            # Imposta la selezione nel FileSelector (senza notificare per evitare loop)
            self.file_selector.selected_paths = source_paths
            self.file_selector.selection_type = selection_type
            self.file_selector.update_preview()

            # Carica automaticamente la prima immagine nel visualizzatore
            self.load_first_image_in_viewer(source_paths, selection_type)

            self.log(f"📷 Immagini sorgente ricaricate: {selection_type} ({len(source_paths)} elementi)")

        except Exception as e:
            self.log(f"⚠️ Errore caricamento immagini sorgente: {e}")
            print(f"Errore caricamento immagini sorgente: {e}")

    def update_project_info(self):
        """Aggiorna le informazioni del progetto"""
        if not self.current_project_path:
            self.project_info_label.config(text="Nessun progetto attivo", foreground="gray")
            self.project_status_label.config(text="Nessun progetto")
            return

        project_info = self.project_manager.get_project_info()
        if not project_info:
            # Fallback per progetti senza info complete
            project_name = os.path.basename(self.current_project_path)
            source_info = self.project_manager.get_source_info()

            info_text = f"Cartella: {project_name}\n"
            info_text += f"Sorgenti: {source_info.get('type', 'N/A')} ({source_info.get('count', 0)})"

            self.project_info_label.config(text=info_text, foreground="blue")
            self.project_status_label.config(text=f"Progetto: {project_name}")
        else:
            # Informazioni complete del progetto
            project_name = project_info.get("name", "N/A")
            crops_count = project_info.get("crops_count", 0)
            gui_type = project_info.get("gui_type", "unknown")
            source_info = project_info.get("source_info", {})
            source_count = source_info.get("count", 0)

            info_text = f"Nome: {project_name}\n"
            info_text += f"Cartella: {os.path.basename(self.current_project_path)}\n"
            info_text += f"Immagini: {source_count}\n"
            info_text += f"Crop esistenti: {crops_count}\n"
            info_text += f"Tipo: {gui_type}"

            # Colore basato sul numero di crop
            color = "green" if crops_count > 0 else "blue"
            self.project_info_label.config(text=info_text, foreground=color)
            self.project_status_label.config(text=f"Progetto: {project_name} ({crops_count} crop)")
    
    def open_project_folder(self):
        """Apre la cartella del progetto corrente"""
        if not self.current_project_path:
            messagebox.showwarning("Attenzione", "Nessun progetto attivo")
            return
        
        try:
            os.startfile(self.current_project_path)  # Windows
        except AttributeError:
            os.system(f"xdg-open '{self.current_project_path}'")  # Linux

    def on_file_double_click(self, file_path):
        """Gestisce doppio click su file per caricarlo nel visualizzatore"""
        try:
            success = self.coordinate_viewer.load_image(file_path)
            if success:
                self.current_image_file = file_path
                self.current_image_data = self.coordinate_viewer.bands_data
                
                # Aggiorna controlli crop con info immagine
                if self.current_image_data is not None:
                    height, width = self.current_image_data.shape[1], self.current_image_data.shape[2]
                    self.crop_controls.set_image_info(
                        os.path.basename(file_path), width, height
                    )
                    
                    # Passa i dati immagine ai controlli crop per superpixel
                    view_mode = getattr(self.coordinate_viewer, 'view_mode', 'rgb')
                    self.crop_controls.set_current_image_data(
                        self.current_image_data, 'multispectral', view_mode
                    )
                
                self.project_manager.mark_images_loaded()
                self.log(f"🖼️ Immagine caricata: {os.path.basename(file_path)}")
            else:
                self.log(f"❌ Impossibile caricare: {os.path.basename(file_path)}")
        except Exception as e:
            self.log(f"❌ Errore caricamento: {e}")
    
    def on_coordinate_click(self, x: int, y: int):
        """Gestisce click per coordinate dal visualizzatore"""
        self.log(f"📍 Coordinate selezionate: X={x}, Y={y}")

        # Log selezione coordinate
        self.project_manager.log_coordinate_selected((x, y), self.current_image_file)

        # Aggiorna controlli crop
        self.crop_controls.set_coordinates(x, y)

    def on_crop_size_change(self, crop_size: int):
        """Gestisce cambio dimensione crop"""
        # Aggiorna dimensione crop nel visualizzatore per l'anteprima
        self.coordinate_viewer.set_crop_size(crop_size)
    
    def on_view_mode_change(self, new_mode: str, previous_mode: str = None):
        """Gestisce cambio modalità visualizzazione"""
        self.log(f"🔄 Modalità: {previous_mode} → {new_mode}")
        
        # Log cambio modalità
        self.project_manager.log_view_mode_changed(new_mode, previous_mode)
    
    def on_crop_save(self, crop_size: int, coordinates: tuple, filename: str):
        """Gestisce salvataggio crop"""
        if self.current_image_data is None or not self.current_image_file:
            messagebox.showwarning("Attenzione", "Nessuna immagine caricata")
            return
        
        if not self.current_project_path:
            messagebox.showwarning("Attenzione", "Nessun progetto attivo")
            return
        
        try:
            # Determina percorso output
            project_paths = self.project_manager.get_project_paths()
            crops_dir = project_paths.get("crops")
            if not crops_dir:
                messagebox.showerror("Errore", "Cartella crops non trovata")
                return
            
            output_path = os.path.join(crops_dir, filename)
            
            # Esegui crop
            x, y = coordinates
            success = self.image_cropper.crop_multispectral_image(
                self.current_image_data, x, y, crop_size, output_path
            )
            
            if success:
                # Registra crop nel progetto
                view_mode = self.coordinate_viewer.view_mode
                self.project_manager.add_crop(
                    output_path, self.current_image_file, coordinates, crop_size, view_mode
                )
                self.project_manager.mark_crop_saved()
                
                self.log(f"✂️ Crop salvato: {filename}")
                messagebox.showinfo("Successo", f"Crop salvato con successo:\n{filename}")
            else:
                messagebox.showerror("Errore", "Impossibile salvare il crop")
                
        except Exception as e:
            messagebox.showerror("Errore Crop", f"Errore durante il crop:\n{e}")
            self.log(f"❌ Errore crop: {e}")
    
    def on_superpixel_generated(self, segments, overlay):
        """
        Callback chiamato quando vengono generati superpixel
        
        Args:
            segments: Array segmentazione (H, W)
            overlay: Array overlay RGBA (H, W, 4)
        """
        try:
            self.log("✅ Superpixel generati, aggiornamento visualizzazione...")
            
            # Passa i superpixel al coordinate viewer per la visualizzazione
            self.coordinate_viewer.set_superpixel_segments(segments, overlay)
            
            self.log(f"✅ Visualizzazione superpixel aggiornata - {len(np.unique(segments))} segmenti")
            
        except Exception as e:
            self.log(f"❌ Errore aggiornamento superpixel: {e}")
            messagebox.showerror("Errore Superpixel", f"Errore nella visualizzazione superpixel:\n{e}")
    
    def on_superpixel_mode_change(self, show_superpixel: bool):
        """
        Callback chiamato quando cambia la modalità crop/superpixel
        
        Args:
            show_superpixel: True per mostrare superpixel, False per nasconderli
        """
        try:
            # Verifica che tutti i componenti siano inizializzati
            if not hasattr(self, 'crop_controls') or not hasattr(self, 'coordinate_viewer'):
                return
            
            # Controlla la modalità corrente
            current_mode = self.crop_controls.get_current_mode()
            
            if show_superpixel and current_mode == "superpixel":
                # Modalità superpixel: mostra overlay e abilita selezione
                self.coordinate_viewer.toggle_superpixel_display(True)
                self.coordinate_viewer.set_superpixel_mode()  # Abilita selezione superpixel
                self.log("🔸 Modalità Superpixel attivata")
            else:
                # Modalità crop: nascondi overlay  
                self.coordinate_viewer.toggle_superpixel_display(False)
                self.coordinate_viewer.set_crop_mode()  # Abilita crop mode
                self.log("✂️ Modalità Crop attivata")
                
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"❌ Errore cambio modalità: {e}")
            else:
                print(f"[DEBUG] Errore cambio modalità: {e}")
    
    def on_superpixel_selected(self, superpixel_id: int, x: int, y: int):
        """
        Callback chiamato quando viene selezionato un superpixel
        
        Args:
            superpixel_id: ID del superpixel selezionato
            x, y: Coordinate del click
        """
        try:
            self.log(f"🔸 Superpixel selezionato: ID {superpixel_id} alle coordinate ({x}, {y})")
            
            # Ottieni bounds del superpixel per calcolare crop con padding
            bounds = self.coordinate_viewer.get_selected_superpixel_bounds()
            
            if bounds:
                min_x, min_y, max_x, max_y = bounds
                self.log(f"📐 Bounds superpixel: ({min_x}, {min_y}) -> ({max_x}, {max_y})")
                
                # Genera crop del superpixel
                self.crop_selected_superpixel(superpixel_id, bounds)
            else:
                self.log("❌ Impossibile calcolare bounds del superpixel")
                
        except Exception as e:
            self.log(f"❌ Errore gestione selezione superpixel: {e}")
    
    def crop_selected_superpixel(self, superpixel_id: int, bounds: Tuple[int, int, int, int]):
        """
        Crea crop del superpixel selezionato con padding
        
        Args:
            superpixel_id: ID del superpixel
            bounds: Tuple (min_x, min_y, max_x, max_y)
        """
        try:
            # Verifica che ci sia un progetto attivo
            if not self.current_project_path:
                self.log("❌ Nessun progetto attivo")
                messagebox.showerror("Errore", "Nessun progetto attivo. Crea o carica un progetto prima di salvare.")
                return
            
            # Verifica che ci siano dati immagine
            if self.current_image_data is None:
                self.log("❌ Nessuna immagine caricata")
                messagebox.showerror("Errore", "Nessuna immagine caricata.")
                return
            
            min_x, min_y, max_x, max_y = bounds
            
            # Calcola dimensioni superpixel
            sp_width = max_x - min_x + 1
            sp_height = max_y - min_y + 1
            
            # Calcola padding (10% delle dimensioni o minimo 5 pixel)
            padding_x = max(5, int(sp_width * 0.1))
            padding_y = max(5, int(sp_height * 0.1))
            
            # Calcola centro del superpixel
            center_x = (min_x + max_x) // 2
            center_y = (min_y + max_y) // 2
            
            # Calcola dimensioni crop quadrato con padding
            crop_dimension = max(sp_width + 2 * padding_x, sp_height + 2 * padding_y)
            
            # Assicurati che sia almeno 32x32
            crop_dimension = max(crop_dimension, 32)
            
            self.log(f"✂️ Generazione crop superpixel: {crop_dimension}x{crop_dimension}px centrato in ({center_x}, {center_y})")
            
            # Crea nome file e percorso
            filename = f"superpixel_{superpixel_id}_{center_x}_{center_y}_{crop_dimension}x{crop_dimension}.tif"
            crops_dir = os.path.join(self.current_project_path, "crops")
            
            # Assicurati che la cartella crops esista
            os.makedirs(crops_dir, exist_ok=True)
            
            output_path = os.path.join(crops_dir, filename)
            
            self.log(f"📁 Salvataggio in: {output_path}")
            
            # Chiama il sistema di crop esistente
            success = self.image_cropper.crop_multispectral_image(
                self.current_image_data,
                center_x, center_y,
                crop_dimension,
                output_path,
                preserve_bands=True  # Mantieni tutte le bande per multispettrali
            )
            
            if success:
                self.log(f"✅ Crop superpixel salvato: {filename}")
                messagebox.showinfo("Successo", f"Crop superpixel salvato:\n{filename}")
            else:
                self.log("❌ Errore salvataggio crop superpixel")
                messagebox.showerror("Errore", "Impossibile salvare il crop del superpixel")
                
        except Exception as e:
            self.log(f"❌ Errore crop superpixel: {e}")
            messagebox.showerror("Errore Crop Superpixel", f"Errore durante il crop:\n{e}")
            import traceback
            traceback.print_exc()
    
    def log(self, message):
        """Aggiunge messaggio al log"""
        print(f"[Labeler] {message}")
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def show_about(self):
        """Mostra informazioni sull'applicazione"""
        about_text = """Labeler Multispettrale 5 Bande v1.0

Labeler per immagini multispettrali MicaSense Red Edge.

Funzionalità:
• Caricamento immagini TIFF 5 bande
• Visualizzazione bande singole con navigazione
• RGB Naturale (3,2,1)
• False Color IR (5,3,2) - vegetazione in rosso
• Red Edge Enhanced (4,3,2) - stress vegetazione
• NDVI-like (5,4,3) - salute vegetazione
• Click per selezionare coordinate
• Crop quadrati centrati sulle coordinate
• Dimensioni crop personalizzabili (16-512px)
• Salvataggio crop con nomi automatici
• Gestione progetti automatica

Struttura progetto:
proj/originals/ - immagini originali
proj/crops/ - crop salvati

Utilizzo:
1. Carica immagini (file singoli, multipli o cartelle)
2. Clicca sull'immagine per selezionare coordinate
3. Imposta dimensione crop desiderata
4. Salva crop con il pulsante "Salva Crop"
"""

        messagebox.showinfo("Informazioni", about_text)

    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        # Termina sessione di logging
        self.project_manager.end_session()
        
        # Pulizia progetto vuoto
        if self.project_manager.current_project:
            self.project_manager.cleanup_empty_project()

        self.root.destroy()

    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()


def main():
    """Funzione principale"""
    app = LabelingGUI()
    app.run()


if __name__ == "__main__":
    main()
