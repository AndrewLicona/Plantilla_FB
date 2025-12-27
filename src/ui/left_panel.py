"""
ui/left_panel.py
Módulo para la construcción del panel izquierdo.
"""
import tkinter as tk
from tkinter import ttk
from src.config import SLOT_MAX

def create_left_panel(parent, app):
    """Crea los widgets para el panel izquierdo y los añade al frame padre."""
    
    ttk.Label(parent, text="Añadir imágenes (2-4):", style='Header.TLabel').pack(pady=(0, 10), anchor=tk.W)
    
    slots_container_frame = ttk.Frame(parent)
    slots_container_frame.pack(fill=tk.X, pady=5)
    
    slots_container_frame.columnconfigure(0, weight=1)
    slots_container_frame.columnconfigure(1, weight=1)
    
    for i in range(SLOT_MAX):
        slot_card_frame = ttk.Frame(slots_container_frame, relief=tk.RIDGE, borderwidth=1, padding=5)
        row = i // 2 
        col = i % 2
        slot_card_frame.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
        slot_card_frame.columnconfigure(0, weight=1)
        
        btn_img = ttk.Button(slot_card_frame, text=f"📁 Imagen {i+1}", width=12, command=lambda idx=i: app.add_image(idx))
        btn_img.grid(row=0, column=0, sticky="ew", padx=(0,2), pady=(0,2))

        rm = ttk.Button(slot_card_frame, text="❌", width=3, command=lambda idx=i: app.remove_image(idx))
        rm.grid(row=0, column=1, sticky="e", pady=(0,2))
        app.remove_buttons.append(rm)
        
        app.slot_buttons.append(btn_img)
        
        lbl = ttk.Label(slot_card_frame, text="", style='Info.TLabel', anchor=tk.CENTER)
        lbl.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,2))
        app.slot_labels.append(lbl)

    ttk.Button(parent, text="🗑️ Limpiar Imágenes", command=app.clear_slot_images).pack(fill=tk.X, pady=5)
    ttk.Separator(parent).pack(fill=tk.X, pady=10)
    
    ttk.Label(parent, text="Cantidad de imágenes:").pack(anchor=tk.W)
    
    slots_button_frame = ttk.Frame(parent)
    slots_button_frame.pack(fill=tk.X, pady=5)
    
    row, col = 0, 0
    for n in range(2, SLOT_MAX + 1):
        btn = ttk.Button(slots_button_frame, text=str(n), command=lambda num=n: app._update_n_slots_and_render(num), width=10)
        btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
        col += 1
        if col > 2:
            col = 0
            row += 1
    
    slots_button_frame.columnconfigure(0, weight=1)
    slots_button_frame.columnconfigure(1, weight=1)
    slots_button_frame.columnconfigure(2, weight=1)

    ttk.Separator(parent).pack(fill=tk.X, pady=15)

    ttk.Label(parent, text="Forma de Imágenes:", style='Header.TLabel').pack(pady=(0, 5), anchor=tk.W)

    shape_button_frame = ttk.Frame(parent)
    shape_button_frame.pack(fill=tk.X, pady=2)
    
    shapes = [("Cuadradas", "square"), ("Redondeadas", "rounded"), ("Círculos", "circle")]
    row, col = 0, 0
    for name, value in shapes:
        btn = ttk.Button(shape_button_frame, text=name, command=lambda v=value: app.set_image_shape(v), width=10)
        btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
        col += 1
        if col > 2:
            col = 0
            row += 1
    
    shape_button_frame.columnconfigure(0, weight=1)
    shape_button_frame.columnconfigure(1, weight=1)
    shape_button_frame.columnconfigure(2, weight=1)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=15)
    
    ttk.Label(parent, text="Configuración de Emojis:", style='Header.TLabel').pack(pady=(0, 10))

    # Selector de Paquete de Emojis
    ttk.Label(parent, text="Paquete de Emojis:").pack(anchor=tk.W)
    app.emoji_pack_selector = ttk.Combobox(parent, textvariable=app.emoji_pack, state="readonly")
    app.emoji_pack_selector.pack(fill=tk.X, padx=5, pady=(0, 10))
    app.emoji_pack_selector.bind("<<ComboboxSelected>>", app.on_emoji_pack_change)

    ttk.Label(parent, text="Tamaño Emoji:").pack(anchor=tk.W, pady=(10, 0))
    ttk.Scale(parent, from_=0.1, to=3.0, variable=app.emoji_size, command=lambda e: app.render_preview()).pack(fill=tk.X, padx=5)

    ttk.Label(parent, text="Posición X Emoji:").pack(anchor=tk.W, pady=(10, 0))
    ttk.Scale(parent, from_=-100, to=100, variable=app.emoji_x_offset, command=lambda e: app.render_preview()).pack(fill=tk.X, padx=5)

    ttk.Label(parent, text="Posición Y Emoji:").pack(anchor=tk.W, pady=(10, 0))
    ttk.Scale(parent, from_=-100, to=100, variable=app.emoji_y_offset, command=lambda e: app.render_preview()).pack(fill=tk.X, padx=5)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=15)
