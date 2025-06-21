#!/usr/bin/env python3
"""
Project Selector - Finestra di dialogo per selezionare progetti esistenti

Fornisce un'interfaccia per visualizzare e selezionare progetti di labeling
esistenti con informazioni dettagliate.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
from datetime import datetime
import os


class ProjectSelectorDialog:
    """Finestra di dialogo per selezionare progetti esistenti"""
    
    def __init__(self, parent, project_manager, title="Seleziona Progetto"):
        """
        Inizializza la finestra di selezione progetti
        
        Args:
            parent: Finestra parent
            project_manager: Istanza del ProjectManager
            title: Titolo della finestra
        """
        self.parent = parent
        self.project_manager = project_manager
        self.selected_project = None
        self.result = None
        self.projects_data = {}  # Dizionario per salvare dati progetti
        
        # Crea finestra di dialogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Centra la finestra
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_projects()
        
        # Focus sulla finestra
        self.dialog.focus_set()
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Titolo
        title_label = ttk.Label(
            main_frame, 
            text="Seleziona un progetto esistente da caricare",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Frame lista progetti
        list_frame = ttk.LabelFrame(main_frame, text="Progetti Disponibili", padding=5)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview per progetti
        columns = ("name", "created", "modified", "crops", "type")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configura colonne
        self.tree.heading("name", text="Nome Progetto")
        self.tree.heading("created", text="Creato")
        self.tree.heading("modified", text="Modificato")
        self.tree.heading("crops", text="Crop")
        self.tree.heading("type", text="Tipo")
        
        self.tree.column("name", width=250)
        self.tree.column("created", width=120)
        self.tree.column("modified", width=120)
        self.tree.column("crops", width=60)
        self.tree.column("type", width=80)
        
        # Scrollbar per treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview e scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind eventi
        self.tree.bind("<<TreeviewSelect>>", self.on_project_select)
        self.tree.bind("<Double-1>", self.on_project_double_click)
        
        # Frame informazioni progetto
        info_frame = ttk.LabelFrame(main_frame, text="Informazioni Progetto", padding=5)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, wrap="word", state="disabled")
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")
        
        # Frame bottoni
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        # Bottoni azione
        ttk.Button(
            button_frame,
            text="🔄 Aggiorna Lista",
            command=self.load_projects
        ).pack(side="left")
        
        ttk.Button(
            button_frame,
            text="📁 Apri Cartella",
            command=self.open_project_folder
        ).pack(side="left", padx=(10, 0))
        
        # Bottoni dialogo
        ttk.Button(
            button_frame,
            text="Annulla",
            command=self.cancel
        ).pack(side="right")
        
        self.load_button = ttk.Button(
            button_frame,
            text="Seleziona",
            command=self.load_project,
            state="disabled"
        )
        self.load_button.pack(side="right", padx=(0, 10))
    
    def load_projects(self):
        """Carica la lista dei progetti"""
        # Pulisci treeview e dati
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.projects_data.clear()
        
        # Ottieni progetti
        projects = self.project_manager.list_projects()
        
        if not projects:
            # Nessun progetto trovato
            self.tree.insert("", "end", values=("Nessun progetto trovato", "", "", "", ""))
            return
        
        # Salva riferimento ai progetti per recupero successivo
        self.projects_data = {}

        # Popola treeview
        for i, project in enumerate(projects):
            # Formatta date
            created = self._format_date(project.get("created_date"))
            modified = self._format_date(project.get("last_modified"))

            # Inserisci nel treeview
            item = self.tree.insert("", "end", values=(
                project.get("name", "N/A"),
                created,
                modified,
                project.get("crop_count", 0),
                project.get("gui_type", "unknown")
            ))

            # Salva dati completi usando l'ID dell'item
            self.projects_data[item] = project
    
    def _format_date(self, date_str: str) -> str:
        """Formatta una data per visualizzazione"""
        if not date_str:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return date_str[:16] if len(date_str) > 16 else date_str
    
    def on_project_select(self, event):
        """Gestisce selezione progetto"""
        selection = self.tree.selection()
        if not selection:
            self.selected_project = None
            self.load_button.config(state="disabled")
            self.update_info_panel(None)
            return

        item = selection[0]

        # Recupera dati progetto dal dizionario
        if item in self.projects_data:
            self.selected_project = self.projects_data[item]
            self.load_button.config(state="normal")
            self.update_info_panel(self.selected_project)
        else:
            self.selected_project = None
            self.load_button.config(state="disabled")
            self.update_info_panel(None)
    
    def on_project_double_click(self, event):
        """Gestisce doppio click per caricare progetto"""
        if self.selected_project:
            self.load_project()
    
    def update_info_panel(self, project: Optional[Dict[str, Any]]):
        """Aggiorna il pannello informazioni"""
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        
        if not project:
            self.info_text.insert(tk.END, "Seleziona un progetto per vedere le informazioni")
        else:
            info = f"Nome: {project.get('name', 'N/A')}\n"
            info += f"Percorso: {project.get('path', 'N/A')}\n"
            info += f"Creato: {self._format_date(project.get('created_date'))}\n"
            info += f"Ultima modifica: {self._format_date(project.get('last_modified'))}\n"
            info += f"Tipo GUI: {project.get('gui_type', 'unknown')}\n"
            info += f"Numero crop: {project.get('crop_count', 0)}\n"
            
            # Aggiungi info sui file sorgente se disponibili
            if 'source_info' in project:
                source_info = project['source_info']
                info += f"\nSorgenti: {source_info.get('type', 'N/A')} ({source_info.get('count', 0)} file)\n"
            
            self.info_text.insert(tk.END, info)
        
        self.info_text.config(state="disabled")
    
    def open_project_folder(self):
        """Apre la cartella del progetto selezionato"""
        if not self.selected_project:
            messagebox.showwarning("Attenzione", "Seleziona un progetto prima")
            return
        
        project_path = self.selected_project.get("path")
        if not project_path or not os.path.exists(project_path):
            messagebox.showerror("Errore", "Cartella progetto non trovata")
            return
        
        try:
            os.startfile(project_path)  # Windows
        except AttributeError:
            os.system(f"xdg-open '{project_path}'")  # Linux
    
    def load_project(self):
        """Carica il progetto selezionato"""
        if not self.selected_project:
            messagebox.showwarning("Attenzione", "Seleziona un progetto prima")
            return
        
        self.result = self.selected_project
        self.dialog.destroy()
    
    def cancel(self):
        """Annulla la selezione"""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[Dict[str, Any]]:
        """Mostra la finestra e restituisce il progetto selezionato"""
        self.dialog.wait_window()
        return self.result
