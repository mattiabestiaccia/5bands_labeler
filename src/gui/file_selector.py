#!/usr/bin/env python3
"""
File Selector - Componenti per selezione file e cartelle per labeling

Fornisce widget tkinter per la selezione di immagini singole, multiple
o cartelle per il labeling multispettrale.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from typing import List, Optional, Callable


class FileSelector:
    """Widget per selezione file e cartelle con preview"""

    def __init__(self, parent, on_selection_change: Callable = None, on_file_double_click: Callable = None,
                 has_active_project_callback: Callable = None):
        """
        Inizializza il selettore file

        Args:
            parent: Widget parent tkinter
            on_selection_change: Callback chiamato quando cambia la selezione
            on_file_double_click: Callback chiamato al doppio click su un file
            has_active_project_callback: Callback per verificare se c'è un progetto attivo
        """
        self.parent = parent
        self.on_selection_change = on_selection_change
        self.on_file_double_click_callback = on_file_double_click
        self.has_active_project_callback = has_active_project_callback
        self.selected_paths = []
        self.selection_type = "none"  # "none", "single_file", "multiple_files", "folder"

        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        self.main_frame = ttk.LabelFrame(self.parent, text="Selezione File/Cartelle", padding=10)
        self.main_frame.pack(fill="x", padx=10, pady=5)
        
        # Frame bottoni
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill="x", pady=(0, 10))
        
        # Bottoni selezione
        ttk.Button(
            buttons_frame, 
            text="📄 Seleziona File Singolo",
            command=self.select_single_file
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            buttons_frame, 
            text="📄📄 Seleziona File Multipli",
            command=self.select_multiple_files
        ).pack(side="left", padx=5)
        
        ttk.Button(
            buttons_frame, 
            text="📁 Seleziona Cartella",
            command=self.select_folder
        ).pack(side="left", padx=5)
        
        ttk.Button(
            buttons_frame, 
            text="🗑️ Pulisci",
            command=self.clear_selection
        ).pack(side="right")
        
        # Area preview selezione
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="Selezione Corrente", padding=5)
        self.preview_frame.pack(fill="both", expand=True)
        
        # Testo info selezione
        self.info_label = ttk.Label(self.preview_frame, text="Nessuna selezione", foreground="gray")
        self.info_label.pack(anchor="w")
        
        # Lista file (scrollable)
        list_frame = ttk.Frame(self.preview_frame)
        list_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox
        self.files_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            height=6,
            selectmode="single"
        )
        self.files_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Bind doppio click per aprire file
        self.files_listbox.bind("<Double-Button-1>", self.on_file_double_click)

    def _has_active_project(self) -> bool:
        """Verifica se c'è un progetto attivo"""
        if self.has_active_project_callback:
            return self.has_active_project_callback()
        return False

    def _add_paths_to_selection(self, new_paths: List[str], new_type: str):
        """Aggiunge nuovi path alla selezione esistente o li sostituisce"""
        if not new_paths:
            return

        if self._has_active_project() and self.selected_paths:
            # C'è un progetto attivo e già delle immagini: aggiungi
            self._merge_selections(new_paths, new_type)
        else:
            # Nessun progetto o nessuna selezione precedente: sostituisci
            self.selected_paths = new_paths
            self.selection_type = new_type

    def _merge_selections(self, new_paths: List[str], new_type: str):
        """Unisce la nuova selezione con quella esistente"""
        # Gestisce i diversi casi di merge
        if self.selection_type == "folder" and new_type != "folder":
            # Caso: cartella esistente + nuovi file
            # Espandi la cartella esistente in file individuali
            if len(self.selected_paths) == 1 and os.path.isdir(self.selected_paths[0]):
                folder_path = self.selected_paths[0]
                image_files = self._find_supported_image_files(folder_path)
                # Sostituisci la cartella con i suoi file
                self.selected_paths = image_files[:]

            # Aggiungi i nuovi file evitando duplicati
            for path in new_paths:
                if path not in self.selected_paths:
                    self.selected_paths.append(path)

            # Cambia tipo a multiple_files
            self.selection_type = "multiple_files"

        elif new_type == "folder" and self.selection_type != "folder":
            # Caso: file esistenti + nuova cartella
            # Espandi la nuova cartella e aggiungi i suoi file
            folder_path = new_paths[0]
            image_files = self._find_supported_image_files(folder_path)

            # Aggiungi i file della cartella evitando duplicati
            for file_path in image_files:
                if file_path not in self.selected_paths:
                    self.selected_paths.append(file_path)

            # Cambia tipo a multiple_files
            self.selection_type = "multiple_files"

        elif self.selection_type == "folder" and new_type == "folder":
            # Caso: cartella esistente + nuova cartella
            # Espandi entrambe le cartelle
            all_files = []

            # Espandi cartella esistente
            if len(self.selected_paths) == 1 and os.path.isdir(self.selected_paths[0]):
                folder_path = self.selected_paths[0]
                all_files.extend(self._find_supported_image_files(folder_path))

            # Espandi nuova cartella
            folder_path = new_paths[0]
            new_files = self._find_supported_image_files(folder_path)
            for file_path in new_files:
                if file_path not in all_files:
                    all_files.append(file_path)

            self.selected_paths = all_files
            self.selection_type = "multiple_files"

        else:
            # Caso: file + file (incluso single_file che diventa multiple_files)
            for path in new_paths:
                if path not in self.selected_paths:
                    self.selected_paths.append(path)

            # Aggiorna il tipo se necessario
            if self.selection_type == "single_file" and len(self.selected_paths) > 1:
                self.selection_type = "multiple_files"

    def select_single_file(self):
        """Seleziona un singolo file immagine"""
        file_path = filedialog.askopenfilename(
            title="Seleziona Immagine per Labeling",
            filetypes=[
                ("File TIFF Multispettrali", "*.tif *.tiff *.TIF *.TIFF"),
                ("Immagini RGB", "*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"),
                ("Tutte le immagini", "*.tif *.tiff *.TIF *.TIFF *.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"),
                ("Tutti i file", "*.*")
            ]
        )

        if file_path:
            self._add_paths_to_selection([file_path], "single_file")
            self.update_preview()
            self._notify_change()

    def select_multiple_files(self):
        """Seleziona file multipli immagine"""
        file_paths = filedialog.askopenfilenames(
            title="Seleziona Immagini per Labeling",
            filetypes=[
                ("File TIFF Multispettrali", "*.tif *.tiff *.TIF *.TIFF"),
                ("Immagini RGB", "*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"),
                ("Tutte le immagini", "*.tif *.tiff *.TIF *.TIFF *.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"),
                ("Tutti i file", "*.*")
            ]
        )

        if file_paths:
            self._add_paths_to_selection(list(file_paths), "multiple_files")
            self.update_preview()
            self._notify_change()

    def select_folder(self):
        """Seleziona una cartella"""
        folder_path = filedialog.askdirectory(
            title="Seleziona Cartella con Immagini per Labeling"
        )

        if folder_path:
            # Verifica che la cartella contenga file immagine supportati
            image_files = self._find_supported_image_files(folder_path)
            if not image_files:
                messagebox.showwarning(
                    "Cartella Vuota",
                    "La cartella selezionata non contiene file immagine supportati."
                )
                return

            self._add_paths_to_selection([folder_path], "folder")
            self.update_preview()
            self._notify_change()

    def clear_selection(self):
        """Pulisce la selezione corrente"""
        self.selected_paths = []
        self.selection_type = "none"
        self.update_preview()
        self._notify_change()

    def _find_supported_image_files(self, folder_path: str) -> List[str]:
        """Trova file immagine supportati in una cartella"""
        image_files = []
        folder = Path(folder_path)

        # Supporta TIFF multispettrali e immagini RGB standard (case insensitive)
        patterns = [
            "*.tif", "*.tiff", "*.TIF", "*.TIFF",
            "*.png", "*.PNG",
            "*.jpg", "*.JPG", "*.jpeg", "*.JPEG"
        ]

        for pattern in patterns:
            image_files.extend(folder.glob(pattern))

        return [str(f) for f in sorted(image_files)]

    def _find_tiff_files(self, folder_path: str) -> List[str]:
        """Trova file TIFF in una cartella (retrocompatibilità)"""
        tiff_files = []
        folder = Path(folder_path)

        for pattern in ["*.tif", "*.tiff", "*.TIF", "*.TIFF"]:
            tiff_files.extend(folder.glob(pattern))

        return [str(f) for f in sorted(tiff_files)]
    
    def update_preview(self):
        """Aggiorna la preview della selezione"""
        # Pulisci listbox
        self.files_listbox.delete(0, tk.END)

        if not self.selected_paths:
            self.info_label.config(text="Nessuna selezione", foreground="gray")
            return

        if self.selection_type == "single_file":
            file_path = self.selected_paths[0]
            self.info_label.config(
                text=f"File singolo: {os.path.basename(file_path)}",
                foreground="blue"
            )
            self.files_listbox.insert(0, os.path.basename(file_path))

        elif self.selection_type == "multiple_files":
            count = len(self.selected_paths)
            self.info_label.config(
                text=f"File multipli: {count} file selezionati",
                foreground="green"
            )
            for path in self.selected_paths:
                self.files_listbox.insert(tk.END, os.path.basename(path))

        elif self.selection_type == "folder":
            # Gestisce il caso di una singola cartella
            if len(self.selected_paths) == 1 and os.path.isdir(self.selected_paths[0]):
                folder_path = self.selected_paths[0]
                image_files = self._find_supported_image_files(folder_path)
                self.info_label.config(
                    text=f"Cartella: {os.path.basename(folder_path)} ({len(image_files)} file immagine)",
                    foreground="purple"
                )
                for file_path in image_files[:20]:  # Mostra max 20 file
                    self.files_listbox.insert(tk.END, os.path.basename(file_path))

                if len(image_files) > 20:
                    self.files_listbox.insert(tk.END, f"... e altri {len(image_files) - 20} file")
            else:
                # Caso inconsistente: selection_type è "folder" ma selected_paths contiene file
                # Questo può succedere durante il merge - tratta come multiple_files
                count = len(self.selected_paths)
                self.info_label.config(
                    text=f"File multipli: {count} file selezionati",
                    foreground="green"
                )
                for path in self.selected_paths[:20]:
                    self.files_listbox.insert(tk.END, os.path.basename(path))

                if len(self.selected_paths) > 20:
                    self.files_listbox.insert(tk.END, f"... e altri {len(self.selected_paths) - 20} file")

                # Correggi il tipo di selezione per coerenza
                self.selection_type = "multiple_files"
    
    def on_file_double_click(self, event):
        """Gestisce doppio click su file nella lista"""
        selection = self.files_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        file_path = None

        if self.selection_type == "single_file":
            file_path = self.selected_paths[0]
        elif self.selection_type == "multiple_files":
            if index < len(self.selected_paths):
                file_path = self.selected_paths[index]
            else:
                return
        elif self.selection_type == "folder":
            # Gestisce cartella singola
            if len(self.selected_paths) == 1 and os.path.isdir(self.selected_paths[0]):
                folder_path = self.selected_paths[0]
                image_files = self._find_supported_image_files(folder_path)
                if index < len(image_files):
                    file_path = image_files[index]
                else:
                    return
            else:
                # Caso inconsistente: selection_type è "folder" ma selected_paths contiene file
                # Tratta come multiple_files
                if index < len(self.selected_paths):
                    potential_path = self.selected_paths[index]
                    if os.path.isfile(potential_path):
                        file_path = potential_path
                    else:
                        return
                else:
                    return
        else:
            return

        # Verifica che il file esista e sia valido
        if file_path and os.path.isfile(file_path):
            # Chiama callback per caricare nel visualizzatore
            if self.on_file_double_click_callback:
                self.on_file_double_click_callback(file_path)
            else:
                # Fallback: mostra info file
                self._show_file_info(file_path)
    
    def _show_file_info(self, file_path: str):
        """Mostra informazioni su un file"""
        try:
            stat = os.stat(file_path)
            size_mb = stat.st_size / (1024 * 1024)
            
            info = f"File: {os.path.basename(file_path)}\n"
            info += f"Percorso: {file_path}\n"
            info += f"Dimensione: {size_mb:.1f} MB"
            
            messagebox.showinfo("Informazioni File", info)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile leggere il file:\n{e}")
    
    def _notify_change(self):
        """Notifica il cambio di selezione"""
        if self.on_selection_change:
            self.on_selection_change(self.selected_paths, self.selection_type)
    
    def get_selection(self) -> tuple:
        """Restituisce la selezione corrente"""
        return self.selected_paths, self.selection_type
    
    def has_selection(self) -> bool:
        """Verifica se c'è una selezione"""
        return len(self.selected_paths) > 0

    def set_selection(self, selected_paths: List[str], selection_type: str):
        """
        Imposta la selezione programmaticamente (per caricamento progetti)

        Args:
            selected_paths: Lista dei path selezionati
            selection_type: Tipo di selezione ("single_file", "multiple_files", "folder")
        """
        self.selected_paths = selected_paths
        self.selection_type = selection_type
        self.update_preview()
        self._notify_change()
