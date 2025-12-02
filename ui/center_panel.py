"""
ui/center_panel.py
Módulo para la construcción del panel central de vista previa.
"""
import tkinter as tk
from tkinter import ttk
from config import CANVAS_SIZE

def create_center_panel(parent, app):
    """Crea los widgets para el panel central y los añade al frame padre."""
    canvas_frame = ttk.Frame(parent)
    canvas_frame.pack(pady=10)
    
    app.preview_canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE[0], height=CANVAS_SIZE[1], bg="#12121a", highlightthickness=2, highlightbackground="#444")
    app.preview_canvas.pack()
    
    title_frame = ttk.Frame(parent)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label_frame = ttk.Frame(title_frame)
    title_label_frame.pack(fill=tk.X)
    
    ttk.Label(title_label_frame, text="Título:", style='Header.TLabel').pack(side=tk.LEFT)
    ttk.Checkbutton(title_label_frame, text="Aplicar a todos", variable=app.apply_to_all_title).pack(side=tk.RIGHT)

    app.title_entry = ttk.Entry(title_frame, textvariable=app.title_text, font=('Arial', 12))
    app.title_entry.pack(fill=tk.X, pady=5)
    app.title_entry.bind("<KeyRelease>", lambda e: app.on_title_change())
    
    btn_frame = ttk.Frame(parent)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="💾 Guardar Plantilla", command=app.generate_and_save).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="🔄 Actualizar Vista", command=app.render_preview).pack(side=tk.LEFT, padx=5)
