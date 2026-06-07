"""
ui/left_panel.py
Módulo para la construcción del panel izquierdo.
"""
import tkinter as tk
from tkinter import ttk
from src.config import SLOT_MAX

def create_left_panel(parent, app):
    """Crea los widgets para el panel izquierdo y los añade al frame padre."""
    
    # Contenedor principal para imágenes y cantidad
    main_container = ttk.LabelFrame(parent, text="📁 Gestión de Imágenes", padding=10)
    main_container.pack(fill=tk.X, pady=(0, 10))
    
    # Sección de botones de cantidad en la parte superior
    ttk.Label(main_container, text="Cantidad de imágenes:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
    
    quantity_frame = ttk.Frame(main_container)
    quantity_frame.pack(fill=tk.X, pady=(0, 10))
    
    for n in range(2, SLOT_MAX + 1):
        btn = ttk.Button(quantity_frame, text=str(n), command=lambda num=n: app._update_n_slots_and_render(num), width=8)
        btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    
    # Separador
    ttk.Separator(main_container, orient='horizontal').pack(fill=tk.X, pady=5)
    
    # Sección de slots de imágenes - diseño optimizado sin cajas anidadas
    slots_frame = ttk.Frame(main_container)
    slots_frame.pack(fill=tk.X, pady=5)
    
    for i in range(SLOT_MAX):
        # Botón de imagen directamente con estilo de tarjeta
        btn_img = ttk.Button(
            slots_frame, 
            text=f"📁 Imagen {i+1}", 
            width=16,
            command=lambda idx=i: app.add_image(idx)
        )
        
        # Layout 2x2 optimizado
        row = i // 2
        col = i % 2
        btn_img.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
        
        # Agregar menú contextual para eliminar imagen
        context_menu = tk.Menu(slots_frame, tearoff=0)
        context_menu.add_command(label="🗑️ Eliminar imagen", command=lambda idx=i: app.remove_image(idx))
        
        def show_context_menu(event):
            if app.slots[i] is not None:  # Solo mostrar si hay imagen
                context_menu.post(event.x_root, event.y_root)
        
        btn_img.bind("<Button-3>", show_context_menu)
        
        app.slot_buttons.append(btn_img)
        
        # Label de estado como parte del mismo botón (más compacto)
        lbl = ttk.Label(slots_frame, text="", style='Info.TLabel', anchor=tk.CENTER, font=('Arial', 7))
        lbl.grid(row=row*2+1, column=col, sticky="ew", padx=2, pady=(0,2))
        app.slot_labels.append(lbl)
    
    # Configurar columnas para distribución equitativa
    slots_frame.columnconfigure(0, weight=1)
    slots_frame.columnconfigure(1, weight=1)

    # Botón de limpiar más compacto
    ttk.Button(main_container, text="🗑️ Limpiar Todo", command=app.clear_slot_images, width=20).pack(pady=(10, 0))
    
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
