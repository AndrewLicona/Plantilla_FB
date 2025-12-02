"""
ui/right_panel.py
Módulo para la construcción del panel derecho de configuración avanzada.
"""
import tkinter as tk
from tkinter import ttk
from config import HAS_TKDND, DND_FILES

def create_right_panel(parent, app):
    """Crea los widgets para el panel derecho y los añade al frame padre."""
    
    ttk.Label(parent, text="Fondo y Logo:", style='Header.TLabel').pack(pady=(0, 10))
    
    ttk.Button(parent, text="🖼️ Cargar Fondo", command=app.load_bg).pack(fill=tk.X, pady=3)
    app.bg_label = ttk.Label(parent, text="Sin fondo", style='Info.TLabel')
    app.bg_label.pack(fill=tk.X)
    
    ttk.Button(parent, text="🏷️ Cargar Logo", command=app.load_logo).pack(fill=tk.X, pady=3)
    app.logo_label = ttk.Label(parent, text="Sin logo", style='Info.TLabel')
    app.logo_label.pack(fill=tk.X)
    
    ttk.Label(parent, text="Tamaño Logo:").pack(anchor=tk.W, pady=(10, 0))
    ttk.Scale(parent, from_=0.05, to=0.8, variable=app.logo_size, command=lambda e: app.render_preview()).pack(fill=tk.X, padx=5)

    ttk.Label(parent, text="Posición X Logo:").pack(anchor=tk.W, pady=(10, 0))
    ttk.Scale(parent, from_=0, to=1, variable=app.logo_x, command=lambda e: app.render_preview()).pack(fill=tk.X, padx=5)

    ttk.Label(parent, text="Posición Y Logo:").pack(anchor=tk.W, pady=(10, 0))
    ttk.Scale(parent, from_=0, to=1, variable=app.logo_y, command=lambda e: app.render_preview()).pack(fill=tk.X, padx=5)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=15)
    
    ttk.Label(parent, text="Estilo de Título:", style='Header.TLabel').pack(pady=(0, 5))
    
    ttk.Label(parent, text="Fuente:").pack(anchor=tk.W)
    
    font_button_frame = ttk.Frame(parent)
    font_button_frame.pack(fill=tk.X, pady=2)
    
    fonts = [
        ("Arial Bold", "arial_bold"), ("Impact", "impact"), ("Comic Sans", "comic"),
        ("Times", "times")
    ]
    
    row, col = 0, 0
    for name, value in fonts:
        btn = ttk.Button(font_button_frame, text=name, command=lambda v=value: app.set_font(v), width=10)
        btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
        col += 1
        if col > 2:
            col = 0
            row += 1
    
    font_button_frame.columnconfigure(0, weight=1)
    font_button_frame.columnconfigure(1, weight=1)
    font_button_frame.columnconfigure(2, weight=1)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=10)
    
    effect_label_frame = ttk.Frame(parent)
    effect_label_frame.pack(fill=tk.X)
    
    ttk.Label(effect_label_frame, text="Efecto:").pack(side=tk.LEFT)
    ttk.Checkbutton(effect_label_frame, text="Aplicar a todos", variable=app.apply_to_all_style).pack(side=tk.RIGHT)

    effect_button_frame = ttk.Frame(parent)
    effect_button_frame.pack(fill=tk.X, pady=2)

    effects = [
        ("Simple", "simple"), ("Contorno", "contorno"),
        ("Sombra Suave", "sombra_suave"), ("Impacto", "impacto")
    ]
    
    row, col = 0, 0
    for name, value in effects:
        btn = ttk.Button(effect_button_frame, text=name, command=lambda v=value: app.on_style_change(v), width=10)
        btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
        col += 1
        if col > 2:
            col = 0
            row += 1
    
    effect_button_frame.columnconfigure(0, weight=1)
    effect_button_frame.columnconfigure(1, weight=1)
    effect_button_frame.columnconfigure(2, weight=1)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=15)
    ttk.Separator(parent).pack(fill=tk.X, pady=15)
    
    ttk.Button(parent, text="🗑️ Limpiar Todo", command=app.clear_all).pack(fill=tk.X, pady=5)
    
    if HAS_TKDND:
        ttk.Label(parent, text="✅ Drag & Drop activado", foreground="green").pack(pady=10)
        try:
            app.root.drop_target_register(DND_FILES)
            app.root.dnd_bind('<<Drop>>', app.on_drop)
        except:
            pass
