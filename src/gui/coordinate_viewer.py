#!/usr/bin/env python3
"""
Coordinate Viewer - Visualizzatore con click per coordinate

Visualizzatore tkinter per immagini multispettrali che cattura le coordinate
del mouse quando si clicca sull'immagine, per il labeling e crop.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from PIL import Image, ImageTk
import tifffile
from typing import Optional, Callable, Tuple
import os


class CoordinateViewer:
    """Visualizzatore con click per coordinate per immagini multispettrali"""
    
    def __init__(self, parent, on_coordinate_click: Callable = None, on_save_callback: Callable = None):
        """
        Inizializza il visualizzatore
        
        Args:
            parent: Widget parent tkinter
            on_coordinate_click: Callback chiamato quando si clicca per coordinate (x, y)
            on_save_callback: Callback per salvare visualizzazioni
        """
        self.parent = parent
        self.on_coordinate_click = on_coordinate_click
        self.on_save_callback = on_save_callback
        
        # Dati immagine
        self.bands_data = None
        self.current_file = None
        self.current_band = 0
        self.view_mode = "bands"
        self.project_crops_dir = None
        self.image_type = None  # 'multispectral' o 'rgb'
        self.zoom_level = 1.0  # Livello di zoom corrente
        
        # Coordinate selezionate
        self.selected_coordinates = None  # (x, y) nelle coordinate originali
        self.click_marker = None  # Riferimento al marker visuale
        self.crop_preview = None  # Riferimento al rettangolo di anteprima crop
        self.crop_size = 64  # Dimensione crop di default
        
        # Nomi bande MicaSense
        self.band_names = [
            "Banda 1 - Blue (475nm)",
            "Banda 2 - Green (560nm)", 
            "Banda 3 - Red (668nm)",
            "Banda 4 - Red Edge (717nm)",
            "Banda 5 - Near-IR (840nm)"
        ]
        
        # Modalità di visualizzazione (aggiornate dinamicamente in base al tipo immagine)
        self.view_modes_multispectral = {
            "bands": "Bande Singole",
            "rgb": "RGB Naturale (3,2,1)",
            "false_color": "False Color IR (5,3,2)",
            "red_edge": "Red Edge Enhanced (4,3,2)",
            "ndvi_like": "NDVI-like (5,4,3)"
        }

        self.view_modes_rgb = {
            "rgb": "RGB Colori",
            "grayscale": "Bianco e Nero"
        }

        self.view_modes = self.view_modes_multispectral  # Default
        
        # Variabili per display
        self.display_image = None
        self.photo_image = None
        self.scale_factor = 1.0  # Fattore di scala per coordinate

        # Anteprima crop
        self.crop_preview_image = None
        self.crop_preview_photo = None

        self.setup_ui()

    def set_project_crops_dir(self, crops_dir: str):
        """Imposta la cartella crops del progetto"""
        self.project_crops_dir = crops_dir

    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        self.main_frame = ttk.LabelFrame(self.parent, text="Visualizzatore con Coordinate", padding=5)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame controlli
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill="x", pady=(0, 5))
        
        # Modalità visualizzazione (dropdown)
        mode_frame = ttk.LabelFrame(controls_frame, text="Modalità Visualizzazione", padding=5)
        mode_frame.pack(side="left", padx=(0, 10))

        self.mode_var = tk.StringVar(value="bands")
        self.mode_dropdown = ttk.Combobox(
            mode_frame, 
            textvariable=self.mode_var,
            values=list(self.view_modes.values()),
            state="readonly",
            width=25
        )
        self.mode_dropdown.pack(padx=5, pady=2)
        self.mode_dropdown.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        # Controlli banda (solo per modalità bande)
        self.band_frame = ttk.LabelFrame(controls_frame, text="Navigazione Banda", padding=5)
        self.band_frame.pack(side="left", padx=(0, 10))
        
        ttk.Button(self.band_frame, text="◀", command=self.prev_band, width=3).pack(side="left")
        self.band_label = ttk.Label(self.band_frame, text="1/5", width=6)
        self.band_label.pack(side="left", padx=5)
        ttk.Button(self.band_frame, text="▶", command=self.next_band, width=3).pack(side="left")
        
        # Info coordinate
        coord_frame = ttk.LabelFrame(controls_frame, text="Coordinate Selezionate", padding=5)
        coord_frame.pack(side="left", padx=(0, 10))
        
        self.coord_label = ttk.Label(coord_frame, text="Nessuna selezione", foreground="gray")
        self.coord_label.pack()
        
        ttk.Button(coord_frame, text="🗑️ Pulisci", command=self.clear_coordinates).pack(pady=(2, 0))

        # Controlli zoom
        zoom_frame = ttk.LabelFrame(controls_frame, text="Zoom", padding=5)
        zoom_frame.pack(side="left", padx=(0, 10))

        ttk.Button(zoom_frame, text="-", command=self.zoom_out, width=3).pack(side="left")
        self.zoom_label = ttk.Label(zoom_frame, text="100%", width=6)
        self.zoom_label.pack(side="left", padx=5)
        ttk.Button(zoom_frame, text="+", command=self.zoom_in, width=3).pack(side="left")

        # Bottoni azione
        action_frame = ttk.Frame(controls_frame)
        action_frame.pack(side="right")

        ttk.Button(action_frame, text="📂 Carica", command=self.load_image_dialog).pack(side="left", padx=2)
        ttk.Button(action_frame, text="📊 Info", command=self.show_image_info).pack(side="left", padx=2)
        
        # Area immagine principale
        self.setup_image_area()

        # Area anteprima crop
        self.setup_crop_preview_area()

        # Inizialmente disabilita controlli
        self.set_controls_enabled(False)
    
    def setup_image_area(self):
        """Configura l'area di visualizzazione immagine"""
        # Frame per immagine con scrollbar
        image_frame = ttk.Frame(self.main_frame)
        image_frame.pack(fill="both", expand=True)
        
        # Canvas per immagine
        self.canvas = tk.Canvas(image_frame, bg="white")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(image_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(image_frame, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack scrollbars e canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind click del mouse
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Bind eventi zoom
        self.canvas.bind("<Control-MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Control-Button-4>", self.on_mouse_wheel)  # Linux
        self.canvas.bind("<Control-Button-5>", self.on_mouse_wheel)  # Linux

        # Focus per eventi tastiera
        self.canvas.focus_set()
        self.canvas.bind("<Control-plus>", lambda e: self.zoom_in())
        self.canvas.bind("<Control-equal>", lambda e: self.zoom_in())  # + senza shift
        self.canvas.bind("<Control-minus>", lambda e: self.zoom_out())
        self.canvas.bind("<Control-KP_Add>", lambda e: self.zoom_in())  # + numpad
        self.canvas.bind("<Control-KP_Subtract>", lambda e: self.zoom_out())  # - numpad
        
        # Messaggio iniziale
        self.canvas.create_text(400, 300, text="Nessuna immagine caricata\nClicca per selezionare coordinate",
                               font=("Arial", 14), fill="gray", tags="message")

    def setup_crop_preview_area(self):
        """Configura l'area di anteprima del crop"""
        # Frame per anteprima crop
        preview_frame = ttk.LabelFrame(self.main_frame, text="Anteprima Crop", padding=5)
        preview_frame.pack(fill="x", pady=(5, 0))

        # Canvas per anteprima crop (dimensione fissa)
        self.crop_canvas = tk.Canvas(preview_frame, width=200, height=200, bg="white")
        self.crop_canvas.pack(side="left", padx=(0, 10))

        # Info crop
        info_frame = ttk.Frame(preview_frame)
        info_frame.pack(side="left", fill="both", expand=True)

        self.crop_info_label = ttk.Label(
            info_frame,
            text="Seleziona coordinate per vedere l'anteprima del crop\n(Sempre ridimensionata a 190x190px)",
            foreground="gray",
            wraplength=200
        )
        self.crop_info_label.pack(anchor="w")

        # Messaggio iniziale nel canvas crop
        self.crop_canvas.create_text(100, 100, text="Anteprima\nCrop",
                                     font=("Arial", 12), fill="gray", tags="crop_message")

    def load_image_dialog(self):
        """Apre dialog per caricare un'immagine"""
        file_path = filedialog.askopenfilename(
            title="Carica Immagine per Labeling",
            filetypes=[
                ("File TIFF Multispettrali", "*.tif *.tiff *.TIF *.TIFF"),
                ("Immagini RGB", "*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"),
                ("Tutte le immagini", "*.tif *.tiff *.TIF *.TIFF *.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"),
                ("Tutti i file", "*.*")
            ]
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path: str) -> bool:
        """
        Carica un'immagine (multispettrale o RGB)

        Args:
            file_path: Percorso del file immagine

        Returns:
            True se caricamento riuscito
        """
        try:
            # Importa qui per evitare import circolari
            try:
                from ..utils.image_utils import ImageUtils
            except ImportError:
                # Fallback per import assoluto
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from utils.image_utils import ImageUtils

            # Carica immagine usando la nuova funzione
            result = ImageUtils.load_image(file_path)
            if result is None:
                messagebox.showerror("Errore", "Impossibile caricare l'immagine")
                return False

            self.bands_data, self.image_type = result
            self.current_file = file_path

            # Verifica formato
            if len(self.bands_data.shape) != 3:
                messagebox.showerror("Errore", "Formato immagine non supportato")
                return False

            # Aggiorna modalità di visualizzazione in base al tipo immagine
            self._update_view_modes_for_image_type()

            # Reset visualizzazione con modalità predefinita appropriata
            self.current_band = 0
            self.zoom_level = 1.0
            self._set_default_view_mode()
            self.clear_coordinates()

            # Abilita controlli
            self.set_controls_enabled(True)

            # Aggiorna visualizzazione
            self.update_display()
            self.update_zoom_label()

            return True

        except Exception as e:
            error_msg = f"Impossibile caricare l'immagine:\n{str(e)}"
            print(f"[DEBUG] {error_msg}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Errore Caricamento", error_msg)
            return False

    def _update_view_modes_for_image_type(self):
        """Aggiorna le modalità di visualizzazione in base al tipo di immagine"""
        if self.image_type == 'rgb':
            self.view_modes = self.view_modes_rgb
        else:
            self.view_modes = self.view_modes_multispectral

        # Aggiorna dropdown
        self.mode_dropdown['values'] = list(self.view_modes.values())

    def _set_default_view_mode(self):
        """Imposta la modalità di visualizzazione predefinita"""
        if self.image_type == 'rgb':
            # Per immagini RGB, predefinita è RGB
            self.view_mode = "rgb"
            self.mode_var.set(self.view_modes["rgb"])
        elif self.image_type == 'multispectral':
            # Per multispettrali, prova RGB se ha almeno 3 bande, altrimenti bande singole
            if self.bands_data.shape[0] >= 3:
                self.view_mode = "rgb"
                self.mode_var.set(self.view_modes["rgb"])
            else:
                self.view_mode = "bands"
                self.mode_var.set(self.view_modes["bands"])
        else:
            # Fallback
            self.view_mode = "bands"
            self.mode_var.set(self.view_modes["bands"])

    def set_controls_enabled(self, enabled: bool):
        """Abilita/disabilita controlli"""
        state = "normal" if enabled else "disabled"
        
        # Dropdown modalità
        self.mode_dropdown.config(state="readonly" if enabled else "disabled")
        
        # Controlli banda
        for child in self.band_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=state)

    def on_mode_change(self, event=None):
        """Gestisce cambio modalità dal dropdown"""
        selected_text = self.mode_var.get()
        
        # Trova la chiave corrispondente
        for key, value in self.view_modes.items():
            if value == selected_text:
                self.view_mode = key
                break
        
        self.update_band_controls_visibility()
        self.update_display()

    def zoom_in(self):
        """Aumenta lo zoom"""
        if self.bands_data is None:
            return

        self.zoom_level = min(self.zoom_level * 1.2, 5.0)  # Max 5x
        self.update_display()
        self.update_zoom_label()

    def zoom_out(self):
        """Diminuisce lo zoom"""
        if self.bands_data is None:
            return

        self.zoom_level = max(self.zoom_level / 1.2, 0.1)  # Min 0.1x
        self.update_display()
        self.update_zoom_label()

    def on_mouse_wheel(self, event):
        """Gestisce zoom con mouse wheel + Ctrl"""
        if self.bands_data is None:
            return

        # Verifica che il mouse sia sopra il canvas
        if event.widget != self.canvas:
            return

        if event.delta > 0 or event.num == 4:  # Scroll up
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:  # Scroll down
            self.zoom_out()

    def update_zoom_label(self):
        """Aggiorna l'etichetta del livello di zoom"""
        zoom_percent = int(self.zoom_level * 100)
        self.zoom_label.config(text=f"{zoom_percent}%")

    def update_band_controls_visibility(self):
        """Mostra/nasconde controlli banda in base alla modalità e tipo immagine"""
        # I controlli banda sono visibili solo per immagini multispettrali in modalità bands
        show_band_controls = (self.image_type == 'multispectral' and self.view_mode == "bands")

        if show_band_controls:
            # Abilita controlli banda
            for child in self.band_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal")
        else:
            # Disabilita controlli banda
            for child in self.band_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="disabled")
    
    def prev_band(self):
        """Banda precedente"""
        if self.bands_data is None:
            return
        
        self.current_band = (self.current_band - 1) % self.bands_data.shape[0]
        if self.view_mode == "bands":
            self.update_display()
    
    def next_band(self):
        """Banda successiva"""
        if self.bands_data is None:
            return
        
        self.current_band = (self.current_band + 1) % self.bands_data.shape[0]
        if self.view_mode == "bands":
            self.update_display()
    
    def on_canvas_click(self, event):
        """Gestisce click del mouse sul canvas"""
        if self.bands_data is None or self.photo_image is None:
            return

        # Ottieni coordinate del click nel canvas
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # Converti in coordinate dell'immagine originale
        # Considera l'offset dell'immagine nel canvas (10, 10)
        img_x = int((canvas_x - 10) / self.scale_factor)
        img_y = int((canvas_y - 10) / self.scale_factor)

        # Verifica che le coordinate siano dentro l'immagine
        if (0 <= img_x < self.bands_data.shape[2] and
            0 <= img_y < self.bands_data.shape[1]):

            self.selected_coordinates = (img_x, img_y)
            self.update_coordinate_display()
            self.draw_click_marker(canvas_x, canvas_y)
            self.draw_crop_preview(canvas_x, canvas_y)
            self.generate_crop_preview()

            # Notifica callback
            if self.on_coordinate_click:
                self.on_coordinate_click(img_x, img_y)
    
    def draw_click_marker(self, canvas_x: float, canvas_y: float):
        """Disegna un marker nel punto cliccato"""
        # Rimuovi tutti i marker precedenti
        self.canvas.delete("marker")
        self.click_marker = None

        # Disegna nuovo marker (croce rossa)
        size = 10
        # Linea orizzontale
        line1 = self.canvas.create_line(
            canvas_x - size, canvas_y, canvas_x + size, canvas_y,
            fill="red", width=3, tags="marker"
        )
        # Linea verticale
        line2 = self.canvas.create_line(
            canvas_x, canvas_y - size, canvas_x, canvas_y + size,
            fill="red", width=3, tags="marker"
        )

        # Salva riferimento al primo elemento per compatibilità
        self.click_marker = line1
    
    def update_coordinate_display(self):
        """Aggiorna la visualizzazione delle coordinate"""
        if self.selected_coordinates:
            x, y = self.selected_coordinates
            self.coord_label.config(
                text=f"X: {x}, Y: {y}", 
                foreground="blue"
            )
        else:
            self.coord_label.config(
                text="Nessuna selezione", 
                foreground="gray"
            )
    
    def clear_coordinates(self):
        """Pulisce le coordinate selezionate"""
        self.selected_coordinates = None
        self.update_coordinate_display()

        # Rimuovi marker visuale
        if self.click_marker:
            self.canvas.delete(self.click_marker)
            self.click_marker = None

        # Rimuovi tutti i tag marker e anteprima crop
        self.canvas.delete("marker")
        self.canvas.delete("crop_preview")
        self.crop_preview = None

        # Pulisci anteprima crop
        self.clear_crop_preview()
    
    def get_selected_coordinates(self) -> Optional[Tuple[int, int]]:
        """Restituisce le coordinate selezionate"""
        return self.selected_coordinates

    def set_crop_size(self, crop_size: int):
        """Imposta la dimensione del crop per l'anteprima"""
        self.crop_size = crop_size
        self.update_crop_preview()
        self.generate_crop_preview()

    def update_crop_preview(self):
        """Aggiorna l'anteprima del crop"""
        # Rimuovi anteprima precedente
        if self.crop_preview:
            self.canvas.delete("crop_preview")
            self.crop_preview = None

        if not self.selected_coordinates or self.bands_data is None:
            return

        x, y = self.selected_coordinates

        # Calcola bounds del crop nelle coordinate canvas
        half_size = self.crop_size // 2
        canvas_x = x * self.scale_factor + 10
        canvas_y = y * self.scale_factor + 10
        canvas_half_size = half_size * self.scale_factor

        # Disegna rettangolo di anteprima
        x1 = canvas_x - canvas_half_size
        y1 = canvas_y - canvas_half_size
        x2 = canvas_x + canvas_half_size
        y2 = canvas_y + canvas_half_size

        self.crop_preview = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="yellow", width=2, dash=(5, 5),
            tags="crop_preview"
        )

    def draw_crop_preview(self, canvas_x: float, canvas_y: float):
        """Disegna l'anteprima del crop"""
        # Rimuovi anteprima precedente
        self.canvas.delete("crop_preview")

        # Calcola dimensioni del rettangolo in coordinate canvas
        canvas_half_size = (self.crop_size // 2) * self.scale_factor

        # Disegna rettangolo di anteprima
        x1 = canvas_x - canvas_half_size
        y1 = canvas_y - canvas_half_size
        x2 = canvas_x + canvas_half_size
        y2 = canvas_y + canvas_half_size

        self.crop_preview = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="yellow", width=2, dash=(5, 5),
            tags="crop_preview"
        )

    def generate_crop_preview(self):
        """Genera l'anteprima del crop"""
        if not self.selected_coordinates or self.bands_data is None:
            self.clear_crop_preview()
            return

        try:
            x, y = self.selected_coordinates

            # Calcola bounds del crop
            half_size = self.crop_size // 2
            x1 = max(0, x - half_size)
            y1 = max(0, y - half_size)
            x2 = min(self.bands_data.shape[2], x + half_size)
            y2 = min(self.bands_data.shape[1], y + half_size)

            # Verifica se il crop è valido
            actual_width = x2 - x1
            actual_height = y2 - y1

            if actual_width < self.crop_size or actual_height < self.crop_size:
                self.crop_info_label.config(
                    text=f"⚠️ Crop troppo vicino al bordo\nDimensioni: {actual_width}x{actual_height}px",
                    foreground="orange"
                )
                self.clear_crop_preview()
                return

            # Estrai il crop dai dati
            if self.view_mode == "bands" and self.image_type == 'multispectral':
                # Singola banda in grayscale per immagini multispettrali
                crop_data = self.bands_data[self.current_band, y1:y2, x1:x2]
                normalized = self._normalize_band(crop_data)
                crop_image = Image.fromarray((normalized * 255).astype(np.uint8), mode='L')
            else:
                # Composito RGB o altre modalità
                crop_image = self._create_crop_composite(x1, y1, x2, y2)

            if crop_image:
                # Ridimensiona SEMPRE a 190x190px per riempire la finestra (lascia 5px di margine)
                crop_image_resized = crop_image.resize((190, 190), Image.Resampling.LANCZOS)

                # Converti per tkinter
                self.crop_preview_photo = ImageTk.PhotoImage(crop_image_resized)

                # Mostra nel canvas centrato
                self.crop_canvas.delete("all")
                canvas_x = (200 - 190) // 2  # Centra i 190px nei 200px disponibili
                canvas_y = (200 - 190) // 2
                self.crop_canvas.create_image(canvas_x, canvas_y, anchor="nw", image=self.crop_preview_photo)

                # Aggiorna info
                self.crop_info_label.config(
                    text=f"✅ Crop: {self.crop_size}x{self.crop_size}px\nCentro: ({x}, {y})\nModalità: {self.view_modes[self.view_mode]}\n(Anteprima sempre 190x190px)",
                    foreground="green"
                )

        except Exception as e:
            print(f"Errore generazione anteprima crop: {e}")
            self.clear_crop_preview()

    def _create_crop_composite(self, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        """Crea composito RGB per il crop"""
        try:
            if self.view_mode == "rgb":
                if self.image_type == 'rgb':
                    # Per immagini RGB standard
                    crop_data = self.bands_data[:, y1:y2, x1:x2]
                    rgb_array = np.transpose(crop_data, (1, 2, 0))

                    # Normalizza se necessario
                    if rgb_array.max() <= 1.0:
                        rgb_array = (rgb_array * 255).astype(np.uint8)
                    else:
                        rgb_array = rgb_array.astype(np.uint8)

                    return Image.fromarray(rgb_array, mode='RGB')
                else:
                    # Per immagini multispettrali RGB (3,2,1)
                    red = self._normalize_band(self.bands_data[2, y1:y2, x1:x2])
                    green = self._normalize_band(self.bands_data[1, y1:y2, x1:x2])
                    blue = self._normalize_band(self.bands_data[0, y1:y2, x1:x2])
            elif self.view_mode == "grayscale":
                # Modalità bianco e nero per immagini RGB
                crop_data = self.bands_data[:, y1:y2, x1:x2]
                rgb_array = np.transpose(crop_data, (1, 2, 0))

                # Normalizza se necessario
                if rgb_array.max() <= 1.0:
                    rgb_array = rgb_array * 255

                # Conversione a grayscale
                gray_array = (0.299 * rgb_array[:, :, 0] +
                             0.587 * rgb_array[:, :, 1] +
                             0.114 * rgb_array[:, :, 2]).astype(np.uint8)

                return Image.fromarray(gray_array, mode='L')
            elif self.view_mode == "false_color":
                red = self._normalize_band(self.bands_data[4, y1:y2, x1:x2])
                green = self._normalize_band(self.bands_data[2, y1:y2, x1:x2])
                blue = self._normalize_band(self.bands_data[1, y1:y2, x1:x2])
            elif self.view_mode == "red_edge":
                red = self._normalize_band(self.bands_data[3, y1:y2, x1:x2])
                green = self._normalize_band(self.bands_data[2, y1:y2, x1:x2])
                blue = self._normalize_band(self.bands_data[1, y1:y2, x1:x2])
            elif self.view_mode == "ndvi_like":
                red = self._normalize_band(self.bands_data[4, y1:y2, x1:x2])
                green = self._normalize_band(self.bands_data[3, y1:y2, x1:x2])
                blue = self._normalize_band(self.bands_data[2, y1:y2, x1:x2])
            else:
                # Fallback alla prima banda
                band_data = self.bands_data[0, y1:y2, x1:x2]
                normalized = self._normalize_band(band_data)
                return Image.fromarray((normalized * 255).astype(np.uint8), mode='L')

            # Per modalità multispettrali
            if self.view_mode in ["false_color", "red_edge", "ndvi_like"]:
                rgb_array = np.stack([red, green, blue], axis=2)
                img_array = (rgb_array * 255).astype(np.uint8)
                return Image.fromarray(img_array, mode='RGB')

        except Exception as e:
            print(f"Errore creazione composito crop: {e}")
            return None

    def clear_crop_preview(self):
        """Pulisce l'anteprima del crop"""
        self.crop_canvas.delete("all")
        self.crop_canvas.create_text(100, 100, text="Anteprima\nCrop",
                                    font=("Arial", 12), fill="gray", tags="crop_message")
        self.crop_info_label.config(
            text="Seleziona coordinate per vedere l'anteprima del crop\n(Sempre ridimensionata a 190x190px)",
            foreground="gray"
        )
        self.crop_preview_photo = None

    def update_display(self):
        """Aggiorna la visualizzazione"""
        if self.bands_data is None:
            return

        try:
            if self.view_mode == "bands":
                self._display_single_band()
            elif self.view_mode == "rgb":
                if self.image_type == 'rgb':
                    self._display_rgb_image()
                else:
                    self._display_rgb()
            elif self.view_mode == "grayscale":
                self._display_grayscale()
            elif self.view_mode == "false_color":
                self._display_false_color()
            elif self.view_mode == "red_edge":
                self._display_red_edge()
            elif self.view_mode == "ndvi_like":
                self._display_ndvi_like()

            # Rigenera anteprima crop se coordinate selezionate
            if self.selected_coordinates:
                self.generate_crop_preview()

        except Exception as e:
            messagebox.showerror("Errore Visualizzazione", f"Errore nella visualizzazione:\n{e}")

    def _display_single_band(self):
        """Visualizza singola banda"""
        band_data = self.bands_data[self.current_band]
        normalized = self._normalize_band(band_data)

        # Converti in immagine PIL
        img_array = (normalized * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode='L')

        self._show_image(pil_image, f"Banda {self.current_band + 1} - {self.band_names[self.current_band]}")

        # Aggiorna label banda
        self.band_label.config(text=f"{self.current_band + 1}/{self.bands_data.shape[0]}")

    def _display_rgb(self):
        """Visualizza composizione RGB naturale (bande 3,2,1)"""
        if self.bands_data.shape[0] < 3:
            self._show_error("RGB richiede almeno 3 bande")
            return

        # RGB naturale: Red(3), Green(2), Blue(1) - indici 2,1,0
        red = self._normalize_band(self.bands_data[2])
        green = self._normalize_band(self.bands_data[1])
        blue = self._normalize_band(self.bands_data[0])

        rgb_array = np.stack([red, green, blue], axis=2)
        img_array = (rgb_array * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode='RGB')

        self._show_image(pil_image, "RGB Naturale (3,2,1)")

    def _display_false_color(self):
        """Visualizza False Color IR (5,3,2) - vegetazione in rosso"""
        if self.bands_data.shape[0] < 5:
            self._show_error("False Color IR richiede 5 bande")
            return

        # False Color IR: NIR(5), Red(3), Green(2) - indici 4,2,1
        red = self._normalize_band(self.bands_data[4])    # NIR -> Red
        green = self._normalize_band(self.bands_data[2])  # Red -> Green
        blue = self._normalize_band(self.bands_data[1])   # Green -> Blue

        rgb_array = np.stack([red, green, blue], axis=2)
        img_array = (rgb_array * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode='RGB')

        self._show_image(pil_image, "False Color IR (5,3,2) - Vegetazione in rosso")

    def _display_red_edge(self):
        """Visualizza Red Edge Enhanced (4,3,2) - stress vegetazione"""
        if self.bands_data.shape[0] < 4:
            self._show_error("Red Edge Enhanced richiede almeno 4 bande")
            return

        # Red Edge Enhanced: RedEdge(4), Red(3), Green(2) - indici 3,2,1
        red = self._normalize_band(self.bands_data[3])    # Red Edge -> Red
        green = self._normalize_band(self.bands_data[2])  # Red -> Green
        blue = self._normalize_band(self.bands_data[1])   # Green -> Blue

        rgb_array = np.stack([red, green, blue], axis=2)
        img_array = (rgb_array * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode='RGB')

        self._show_image(pil_image, "Red Edge Enhanced (4,3,2) - Stress vegetazione")

    def _display_ndvi_like(self):
        """Visualizza NDVI-like (5,4,3) - salute vegetazione"""
        if self.bands_data.shape[0] < 5:
            self._show_error("NDVI-like richiede 5 bande")
            return

        # NDVI-like: NIR(5), RedEdge(4), Red(3) - indici 4,3,2
        red = self._normalize_band(self.bands_data[4])    # NIR -> Red
        green = self._normalize_band(self.bands_data[3])  # Red Edge -> Green
        blue = self._normalize_band(self.bands_data[2])   # Red -> Blue

        rgb_array = np.stack([red, green, blue], axis=2)
        img_array = (rgb_array * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode='RGB')

        self._show_image(pil_image, "NDVI-like (5,4,3) - Salute vegetazione")

    def _display_rgb_image(self):
        """Visualizza immagine RGB standard"""
        # Per immagini RGB, i dati sono già in formato (3, height, width)
        # Trasponi in (height, width, 3) per PIL
        rgb_array = np.transpose(self.bands_data, (1, 2, 0))

        # Normalizza se necessario (0-255)
        if rgb_array.max() <= 1.0:
            rgb_array = (rgb_array * 255).astype(np.uint8)
        else:
            rgb_array = rgb_array.astype(np.uint8)

        pil_image = Image.fromarray(rgb_array, mode='RGB')
        self._show_image(pil_image, "RGB Colori")

    def _display_grayscale(self):
        """Visualizza immagine RGB in bianco e nero"""
        # Converti RGB in grayscale usando i pesi standard
        rgb_array = np.transpose(self.bands_data, (1, 2, 0))

        # Normalizza se necessario
        if rgb_array.max() <= 1.0:
            rgb_array = rgb_array * 255

        # Conversione a grayscale: 0.299*R + 0.587*G + 0.114*B
        gray_array = (0.299 * rgb_array[:, :, 0] +
                     0.587 * rgb_array[:, :, 1] +
                     0.114 * rgb_array[:, :, 2]).astype(np.uint8)

        pil_image = Image.fromarray(gray_array, mode='L')
        self._show_image(pil_image, "Bianco e Nero")

    def _show_image(self, pil_image: Image.Image, title: str):
        """Mostra immagine nel canvas con supporto zoom"""
        original_size = pil_image.size

        # Applica zoom
        if self.zoom_level != 1.0:
            new_width = int(original_size[0] * self.zoom_level)
            new_height = int(original_size[1] * self.zoom_level)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Ridimensiona se troppo grande (solo se zoom <= 1.0)
        max_size = 800
        if self.zoom_level <= 1.0 and (pil_image.width > max_size or pil_image.height > max_size):
            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            # Calcola fattore di scala per coordinate
            self.scale_factor = min(pil_image.width / original_size[0],
                                  pil_image.height / original_size[1])
        else:
            # Fattore di scala è il livello di zoom
            self.scale_factor = self.zoom_level

        # Converti per tkinter
        self.photo_image = ImageTk.PhotoImage(pil_image)

        # Mostra nel canvas
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, anchor="nw", image=self.photo_image)

        # Ridisegna marker e anteprima se presenti
        if self.selected_coordinates:
            x, y = self.selected_coordinates
            canvas_x = x * self.scale_factor + 10
            canvas_y = y * self.scale_factor + 10
            self.draw_click_marker(canvas_x, canvas_y)
            self.draw_crop_preview(canvas_x, canvas_y)

        # Aggiorna scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Aggiorna titolo frame con zoom
        zoom_info = f" (Zoom: {int(self.zoom_level * 100)}%)" if self.zoom_level != 1.0 else ""
        self.main_frame.config(text=f"Visualizzatore - {title}{zoom_info}")

    def _show_error(self, message: str):
        """Mostra messaggio di errore nel canvas"""
        self.canvas.delete("all")
        self.canvas.create_text(400, 300, text=message,
                               font=("Arial", 14), fill="red")

    def _normalize_band(self, band_data: np.ndarray) -> np.ndarray:
        """Normalizza banda per visualizzazione"""
        band_min = np.percentile(band_data, 2)
        band_max = np.percentile(band_data, 98)

        if band_max > band_min:
            normalized = (band_data - band_min) / (band_max - band_min)
            return np.clip(normalized, 0, 1)
        else:
            return np.zeros_like(band_data)

    def show_image_info(self):
        """Mostra informazioni sull'immagine"""
        if self.bands_data is None:
            messagebox.showwarning("Attenzione", "Nessuna immagine caricata")
            return

        info = f"File: {os.path.basename(self.current_file) if self.current_file else 'N/A'}\n"
        info += f"Dimensioni: {self.bands_data.shape[2]} x {self.bands_data.shape[1]} pixel\n"
        info += f"Bande: {self.bands_data.shape[0]}\n"
        info += f"Tipo dati: {self.bands_data.dtype}\n"
        info += f"Modalità: {self.view_modes[self.view_mode]}\n"

        if self.selected_coordinates:
            x, y = self.selected_coordinates
            info += f"\nCoordinate selezionate: X={x}, Y={y}\n"

            if self.view_mode == "bands":
                band_data = self.bands_data[self.current_band]
                pixel_value = band_data[y, x]
                info += f"Valore pixel (banda {self.current_band + 1}): {pixel_value}\n"

        if self.view_mode == "bands":
            band_data = self.bands_data[self.current_band]
            info += f"\nBanda corrente: {self.current_band + 1}\n"
            info += f"Min: {band_data.min()}\n"
            info += f"Max: {band_data.max()}\n"
            info += f"Media: {band_data.mean():.2f}\n"

        messagebox.showinfo("Informazioni Immagine", info)
