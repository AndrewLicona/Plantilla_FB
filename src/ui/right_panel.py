"""
ui/right_panel.py
Módulo para la construcción del panel derecho de configuración avanzada.
"""
import tkinter as tk
from tkinter import ttk
from src.config import HAS_TKDND, DND_FILES
from src.utils import get_system_fonts

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
    
    # Solo 3 opciones principales de fuentes
    font_options = [
        "Arial (Moderna)",
        "Impact (Bold)", 
        "Times (Clásica)"
    ]
    
    # Crear combobox para fuentes
    app.font_selector = ttk.Combobox(parent, values=font_options, state="readonly")
    app.font_selector.pack(fill=tk.X, padx=5, pady=2)
    app.font_selector.set("Arial (Moderna)")
    
    # Mapeo directo de opciones a fuentes internas
    def map_option_to_internal_font(option):
        """Mapea una opción del combobox a una fuente interna"""
        if "Arial" in option:
            return 'arial_bold'
        elif "Impact" in option:
            return 'impact'
        elif "Times" in option:
            return 'times'
        else:
            return 'arial_bold'
    
    # Evento de cambio
    def on_font_change(event):
        selected_option = app.font_selector.get()
        internal_font = map_option_to_internal_font(selected_option)
        app.set_font(internal_font)
    
    app.font_selector.bind("<<ComboboxSelected>>", on_font_change)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=10)
    
    effect_label_frame = ttk.Frame(parent)
    effect_label_frame.pack(fill=tk.X)
    
    ttk.Label(effect_label_frame, text="Efecto:").pack(side=tk.LEFT)
    ttk.Checkbutton(effect_label_frame, text="Aplicar a todos", variable=app.apply_to_all_style).pack(side=tk.RIGHT)

    # Opciones de efectos en combobox
    effect_options = [
        "Simple (Limpio)",
        "Contorno (Borde)",
        "Sombra Suave",
        "Impacto (3D)"
    ]
    
    # Crear combobox para efectos
    app.effect_selector = ttk.Combobox(parent, values=effect_options, state="readonly")
    app.effect_selector.pack(fill=tk.X, padx=5, pady=2)
    app.effect_selector.set("Simple (Limpio)")
    
    # Mapeo de opciones a efectos internos
    def map_option_to_effect(option):
        """Mapea una opción del combobox a un efecto interno"""
        if "Simple" in option:
            return 'simple'
        elif "Contorno" in option:
            return 'contorno'
        elif "Sombra" in option:
            return 'sombra_suave'
        elif "Impacto" in option:
            return 'impacto'
        else:
            return 'simple'
    
    # Evento de cambio de efecto
    def on_effect_change(event):
        selected_option = app.effect_selector.get()
        internal_effect = map_option_to_effect(selected_option)
        app.on_style_change(internal_effect)
    
    app.effect_selector.bind("<<ComboboxSelected>>", on_effect_change)
    
    # Selector de color del texto - layout optimizado
    color_frame = ttk.Frame(parent)
    color_frame.pack(fill=tk.X, pady=2)
    
    ttk.Label(color_frame, text="Color:", width=8).pack(side=tk.LEFT, padx=(0, 5))
    
    # Variable para el color
    app.text_color = tk.StringVar(value="#FFFFFF")  # Blanco por defecto
    
    # Botón para seleccionar color
    def choose_text_color():
        from tkinter import colorchooser
        color = colorchooser.askcolor(initialcolor=app.text_color.get())
        if color[1]:  # Si el usuario no canceló
            app.text_color.set(color[1])
            app.color_button.config(bg=color[1])
            app.render_preview()
    
    # Botón de color más compacto
    app.color_button = tk.Button(color_frame, text="Elegir", bg=app.text_color.get(), 
                                 command=choose_text_color, width=12, height=1)
    app.color_button.pack(side=tk.RIGHT, padx=5)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=10)
    
    ttk.Button(parent, text="🗑️ Limpiar", command=app.clear_all).pack(fill=tk.X, pady=5)
    
    if HAS_TKDND:
        ttk.Label(parent, text="✅ Drag & Drop activado", foreground="green").pack(pady=10)
        # El bloque try-except se elimina para permitir que los errores de DND aparezcan
        # y poder depurarlos, en lugar de que fallen silenciosamente.
        app.root.drop_target_register(DND_FILES)
        app.root.dnd_bind('<<Drop>>', app.on_drop)
