#!/usr/bin/env python3
"""
Crop Controls - Controlli per il crop delle immagini

Fornisce widget tkinter per configurare le dimensioni del crop e
gestire il salvataggio dei ritagli quadrati.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Tuple
import os


class CropControls:
    """Widget per controlli del crop"""

    def __init__(self, parent, on_crop_save: Callable = None, on_crop_size_change: Callable = None):
        """
        Inizializza i controlli crop

        Args:
            parent: Widget parent tkinter
            on_crop_save: Callback chiamato per salvare il crop (size, coordinates, filename)
            on_crop_size_change: Callback chiamato quando cambia la dimensione del crop
        """
        self.parent = parent
        self.on_crop_save = on_crop_save
        self.on_crop_size_change = on_crop_size_change
        
        # Stato controlli
        self.current_coordinates = None
        self.current_image_size = None  # (width, height)
        self.current_filename = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        self.main_frame = ttk.LabelFrame(self.parent, text="Controlli Crop", padding=10)
        self.main_frame.pack(fill="x", padx=10, pady=5)
        
        # Frame dimensioni crop
        size_frame = ttk.LabelFrame(self.main_frame, text="Dimensioni Crop", padding=5)
        size_frame.pack(fill="x", pady=(0, 10))
        
        # Controlli dimensioni
        dims_frame = ttk.Frame(size_frame)
        dims_frame.pack(fill="x")

        ttk.Label(dims_frame, text="Dimensione (pixel):").pack(side="left")

        self.size_var = tk.IntVar(value=64)
        self.size_spinbox = ttk.Spinbox(
            dims_frame,
            from_=16,
            to=512,
            increment=1,
            textvariable=self.size_var,
            width=8
        )
        self.size_spinbox.pack(side="left", padx=(5, 5))

        # Slider per dimensioni
        self.size_scale = ttk.Scale(
            dims_frame,
            from_=16,
            to=512,
            orient="horizontal",
            variable=self.size_var,
            length=150
        )
        self.size_scale.pack(side="left", padx=(5, 0))
        
        # Bottoni dimensioni predefinite
        preset_frame1 = ttk.Frame(size_frame)
        preset_frame1.pack(fill="x", pady=(5, 0))

        ttk.Label(preset_frame1, text="Preset comuni:").pack(side="left")

        for size in [32, 64, 128, 256]:
            ttk.Button(
                preset_frame1,
                text=f"{size}px",
                command=lambda s=size: self.set_crop_size(s),
                width=6
            ).pack(side="left", padx=2)

        # Preset aggiuntivi
        preset_frame2 = ttk.Frame(size_frame)
        preset_frame2.pack(fill="x", pady=(2, 0))

        ttk.Label(preset_frame2, text="Altri:").pack(side="left")

        for size in [16, 48, 96, 192, 384, 512]:
            ttk.Button(
                preset_frame2,
                text=f"{size}px",
                command=lambda s=size: self.set_crop_size(s),
                width=6
            ).pack(side="left", padx=1)
        
        # Frame coordinate
        coord_frame = ttk.LabelFrame(self.main_frame, text="Coordinate Centro", padding=5)
        coord_frame.pack(fill="x", pady=(0, 10))
        
        # Visualizzazione coordinate
        self.coord_display_frame = ttk.Frame(coord_frame)
        self.coord_display_frame.pack(fill="x")
        
        ttk.Label(self.coord_display_frame, text="Centro:").pack(side="left")
        self.coord_label = ttk.Label(
            self.coord_display_frame, 
            text="Nessuna selezione", 
            foreground="gray"
        )
        self.coord_label.pack(side="left", padx=(5, 0))
        
        # Controlli manuali coordinate
        manual_frame = ttk.Frame(coord_frame)
        manual_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(manual_frame, text="X:").pack(side="left")
        self.x_var = tk.IntVar(value=0)
        self.x_spinbox = ttk.Spinbox(
            manual_frame,
            from_=0,
            to=9999,
            textvariable=self.x_var,
            width=8
        )
        self.x_spinbox.pack(side="left", padx=(2, 10))
        
        ttk.Label(manual_frame, text="Y:").pack(side="left")
        self.y_var = tk.IntVar(value=0)
        self.y_spinbox = ttk.Spinbox(
            manual_frame,
            from_=0,
            to=9999,
            textvariable=self.y_var,
            width=8
        )
        self.y_spinbox.pack(side="left", padx=(2, 10))
        
        ttk.Button(
            manual_frame,
            text="📍 Applica",
            command=self.apply_manual_coordinates
        ).pack(side="left", padx=(10, 0))
        
        # Frame anteprima crop
        preview_frame = ttk.LabelFrame(self.main_frame, text="Anteprima Crop", padding=5)
        preview_frame.pack(fill="x", pady=(0, 10))
        
        self.preview_label = ttk.Label(
            preview_frame,
            text="Seleziona coordinate per vedere l'anteprima",
            foreground="gray"
        )
        self.preview_label.pack()
        
        # Frame salvataggio
        save_frame = ttk.LabelFrame(self.main_frame, text="Salvataggio", padding=5)
        save_frame.pack(fill="x")
        
        # Nome file
        name_frame = ttk.Frame(save_frame)
        name_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(name_frame, text="Nome:").pack(side="left")
        self.filename_var = tk.StringVar()
        self.filename_entry = ttk.Entry(
            name_frame,
            textvariable=self.filename_var,
            width=30
        )
        self.filename_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Bottoni salvataggio
        button_frame = ttk.Frame(save_frame)
        button_frame.pack(fill="x", pady=(5, 0))
        
        self.save_button = ttk.Button(
            button_frame,
            text="✂️ Salva Crop",
            command=self.save_crop,
            state="disabled"
        )
        self.save_button.pack(side="left")
        
        ttk.Button(
            button_frame,
            text="🔄 Auto Nome",
            command=self.generate_auto_filename
        ).pack(side="left", padx=(10, 0))
        
        # Bind eventi per aggiornamento anteprima
        self.size_var.trace('w', self.update_preview)
        self.x_var.trace('w', self.update_preview)
        self.y_var.trace('w', self.update_preview)
    
    def set_crop_size(self, size: int):
        """Imposta la dimensione del crop"""
        self.size_var.set(size)
        self.update_preview()

        # Notifica callback per aggiornare anteprima nel visualizzatore
        if self.on_crop_size_change:
            self.on_crop_size_change(size)
    
    def set_coordinates(self, x: int, y: int):
        """Imposta le coordinate dal click sull'immagine"""
        self.current_coordinates = (x, y)
        self.x_var.set(x)
        self.y_var.set(y)
        
        self.coord_label.config(
            text=f"X: {x}, Y: {y}",
            foreground="blue"
        )
        
        self.update_preview()
        self.generate_auto_filename()
    
    def apply_manual_coordinates(self):
        """Applica coordinate inserite manualmente"""
        x = self.x_var.get()
        y = self.y_var.get()
        
        # Verifica validità coordinate
        if self.current_image_size:
            width, height = self.current_image_size
            if not (0 <= x < width and 0 <= y < height):
                messagebox.showwarning(
                    "Coordinate Non Valide",
                    f"Le coordinate devono essere tra 0-{width-1} (X) e 0-{height-1} (Y)"
                )
                return
        
        self.current_coordinates = (x, y)
        self.coord_label.config(
            text=f"X: {x}, Y: {y}",
            foreground="blue"
        )
        
        self.update_preview()
        self.generate_auto_filename()
    
    def set_image_info(self, filename: str, width: int, height: int):
        """Imposta informazioni sull'immagine corrente"""
        self.current_filename = filename
        self.current_image_size = (width, height)
        
        # Aggiorna limiti spinbox
        self.x_spinbox.config(to=width-1)
        self.y_spinbox.config(to=height-1)
        
        self.update_preview()
    
    def update_preview(self, *args):
        """Aggiorna l'anteprima del crop"""
        if not self.current_coordinates or not self.current_image_size:
            self.preview_label.config(
                text="Seleziona coordinate per vedere l'anteprima",
                foreground="gray"
            )
            self.save_button.config(state="disabled")
            return
        
        x, y = self.current_coordinates
        size = self.size_var.get()
        width, height = self.current_image_size
        
        # Calcola bounds del crop
        half_size = size // 2
        x1 = max(0, x - half_size)
        y1 = max(0, y - half_size)
        x2 = min(width, x + half_size)
        y2 = min(height, y + half_size)
        
        actual_width = x2 - x1
        actual_height = y2 - y1
        
        # Verifica se il crop è valido
        if actual_width < size or actual_height < size:
            self.preview_label.config(
                text=f"⚠️ Crop troppo vicino al bordo: {actual_width}x{actual_height}px",
                foreground="orange"
            )
            self.save_button.config(state="disabled")
        else:
            self.preview_label.config(
                text=f"✅ Crop: {size}x{size}px centrato in ({x}, {y})",
                foreground="green"
            )
            self.save_button.config(state="normal")

        # Notifica callback per aggiornare anteprima nel visualizzatore
        if self.on_crop_size_change:
            self.on_crop_size_change(size)
    
    def generate_auto_filename(self):
        """Genera automaticamente un nome file"""
        if not self.current_filename or not self.current_coordinates:
            return
        
        base_name = os.path.splitext(self.current_filename)[0]
        x, y = self.current_coordinates
        size = self.size_var.get()
        
        filename = f"{base_name}_crop_{x}_{y}_{size}x{size}.tif"
        self.filename_var.set(filename)
    
    def save_crop(self):
        """Salva il crop"""
        if not self.current_coordinates:
            messagebox.showwarning("Attenzione", "Nessuna coordinata selezionata")
            return
        
        filename = self.filename_var.get().strip()
        if not filename:
            messagebox.showwarning("Attenzione", "Inserisci un nome file")
            return
        
        size = self.size_var.get()
        x, y = self.current_coordinates
        
        # Chiama callback per salvare
        if self.on_crop_save:
            self.on_crop_save(size, (x, y), filename)
    
    def clear_coordinates(self):
        """Pulisce le coordinate"""
        self.current_coordinates = None
        self.coord_label.config(
            text="Nessuna selezione",
            foreground="gray"
        )
        self.x_var.set(0)
        self.y_var.set(0)
        self.filename_var.set("")
        self.update_preview()
    
    def get_crop_info(self) -> Optional[dict]:
        """Restituisce informazioni sul crop corrente"""
        if not self.current_coordinates:
            return None
        
        return {
            'coordinates': self.current_coordinates,
            'size': self.size_var.get(),
            'filename': self.filename_var.get().strip()
        }
