"""
ui/batch_panel.py
Módulo para la construcción y lógica del panel de procesamiento por lotes.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from datetime import datetime
from src.composer import compose_template
from src.config import FINAL_SIZE, SLOT_MAX

def on_batch_group_select(event, app):
    """
    Se ejecuta cuando un usuario selecciona un grupo en el Treeview.
    Actualiza los controles de la UI principal con la configuración del grupo seleccionado.
    """
    selected_items = app.batch_tree.selection()
    if not selected_items:
        return

    selected_item = selected_items[0]
    index = app.batch_tree.index(selected_item)
    
    if index < len(app.batch_groups):
        group = app.batch_groups[index]
        
        # Actualizar las variables de la app con la configuración del grupo
        app.title_text.set(group.get("title_text", ""))
        app.font_family.set(group.get("font_family", "arial_bold"))
        app.title_style.set(group.get("title_style", "impacto"))
        app.image_shape.set(group.get("image_shape", "square"))
        app.logo_size.set(group.get("logo_size", 0.20))
        app.logo_x.set(group.get("logo_x", 0.50))
        app.logo_y.set(group.get("logo_y", 0.50))
        app.emoji_size.set(group.get("emoji_size", 1.0))
        app.emoji_x_offset.set(group.get("emoji_x_offset", 0))
        app.emoji_y_offset.set(group.get("emoji_y_offset", 0))

        # Cargar las imágenes del grupo en los slots principales de la app
        app.slots = [None] * SLOT_MAX # Limpiar slots
        for slot_idx, path in enumerate(group["paths"]):
            if slot_idx < SLOT_MAX:
                try:
                    app.slots[slot_idx] = Image.open(path).convert("RGBA")
                except Exception as e:
                    print(f"Error cargando imagen para visualización del grupo: {e}")
                    app.slots[slot_idx] = None
        app.n_slots = group["count"] # Actualizar el contador de slots
        app._update_slot_visibility() # Actualizar la visibilidad de los slots en el panel izquierdo
        
        # Actualizar la vista previa para reflejar la selección
        app.render_preview()

def save_changes_to_group(app):
    """
    Guarda la configuración actual de la UI en el grupo seleccionado en el Treeview.
    """
    selected_items = app.batch_tree.selection()
    if not selected_items:
        messagebox.showwarning("Sin Selección", "Por favor, selecciona un grupo para guardar los cambios.")
        return

    selected_item = selected_items[0]
    index = app.batch_tree.index(selected_item)

    if index < len(app.batch_groups):
        # Actualizar el diccionario del grupo con los valores actuales de la UI
        app.batch_groups[index].update({
            "title_text": app.title_text.get(),
            "font_family": app.font_family.get(),
            "title_style": app.title_style.get(),
            "image_shape": app.image_shape.get(),
            "logo_size": app.logo_size.get(),
            "logo_x": app.logo_x.get(),
            "logo_y": app.logo_y.get(),
            "emoji_size": app.emoji_size.get(),
            "emoji_x_offset": app.emoji_x_offset.get(),
            "emoji_y_offset": app.emoji_y_offset.get(),
        })
        # Actualizar el Treeview para reflejar el nuevo título
        update_batch_treeview(app)
        messagebox.showinfo("Éxito", "Cambios guardados en el grupo seleccionado.")

def create_batch_panel(parent, app):
    """Crea los widgets para el panel de lotes y los añade al frame padre."""
    ttk.Label(parent, text="Configuración de Lotes:", style='Header.TLabel').pack(pady=(0, 10), anchor=tk.W)

    add_group_frame = ttk.Frame(parent)
    add_group_frame.pack(fill=tk.X, pady=5)

    ttk.Button(add_group_frame, text="➕ Añadir Grupo de Imágenes", command=lambda: add_batch_group(app)).pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    ttk.Separator(parent).pack(fill=tk.X, pady=10)

    # Guardar el treeview en la instancia de la app para acceso global
    app.batch_tree = ttk.Treeview(parent, columns=("Num. Imágenes", "Título", "Rutas"), show="headings")
    app.batch_tree.heading("Num. Imágenes", text="Imágenes")
    app.batch_tree.heading("Título", text="Título")
    app.batch_tree.heading("Rutas", text="Rutas de Archivo")
    app.batch_tree.column("Num. Imágenes", width=80, anchor=tk.CENTER)
    app.batch_tree.column("Título", width=120, anchor=tk.W)
    app.batch_tree.column("Rutas", width=150, anchor=tk.W)
    app.batch_tree.pack(fill=tk.BOTH, expand=True)

    # Vincular el evento de selección
    app.batch_tree.bind('<<TreeviewSelect>>', lambda event: on_batch_group_select(event, app))

    tree_scroll = ttk.Scrollbar(parent, orient="vertical", command=app.batch_tree.yview)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    app.batch_tree.configure(yscrollcommand=tree_scroll.set)

    # Frame para botones de edición y acción
    action_buttons_frame = ttk.Frame(parent)
    action_buttons_frame.pack(fill=tk.X, pady=5)
    action_buttons_frame.columnconfigure(0, weight=1)
    action_buttons_frame.columnconfigure(1, weight=1)

    edit_buttons_frame = ttk.Frame(action_buttons_frame)
    edit_buttons_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    edit_buttons_frame.columnconfigure(0, weight=1)
    edit_buttons_frame.columnconfigure(1, weight=1)
    
    ttk.Button(edit_buttons_frame, text="💾 Guardar Cambios", command=lambda: save_changes_to_group(app)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
    ttk.Button(edit_buttons_frame, text="🗑️ Eliminar Grupo", command=lambda: remove_batch_group(app)).pack(side=tk.LEFT, expand=True, fill=tk.X)

    ttk.Button(action_buttons_frame, text="💥 Limpiar Lotes", command=lambda: clear_all_batch_groups(app)).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    ttk.Button(parent, text="▶️ Iniciar Lote", command=lambda: start_batch_processing(app)).pack(fill=tk.X, pady=(5,0))


def add_batch_group(app, paths=None):
    """Permite al usuario añadir un grupo de imágenes para procesamiento por lotes."""
    if paths is None:
        paths = filedialog.askopenfilenames(
            title="Selecciona 2, 3 o 4 imágenes para el grupo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp"), ("Todos", "*.*")]
        )
    if not paths:
        return
    
    num_images = len(paths)
    if num_images not in [2, 3, 4]:
        messagebox.showwarning("Cantidad Incorrecta", "Por favor, selecciona 2, 3 o 4 imágenes por grupo.")
        return

    # Captura la configuración actual de la app
    group_settings = {
        "count": num_images,
        "paths": list(paths),
        "title_text": app.title_text.get(),
        "font_family": app.font_family.get(),
        "title_style": app.title_style.get(),
        "image_shape": app.image_shape.get(),
        "logo_size": app.logo_size.get(),
        "logo_x": app.logo_x.get(),
        "logo_y": app.logo_y.get(),
        "emoji_size": app.emoji_size.get(),
        "emoji_x_offset": app.emoji_x_offset.get(),
        "emoji_y_offset": app.emoji_y_offset.get(),
    }

    app.batch_groups.append(group_settings)
    update_batch_treeview(app)


def remove_batch_group(app):
    """Elimina el grupo seleccionado del Treeview."""
    selected_item = app.batch_tree.selection()
    if not selected_item:
        messagebox.showwarning("Ningún Grupo Seleccionado", "Por favor, selecciona un grupo para eliminar.")
        return

    # Pedir confirmación antes de eliminar
    confirm = messagebox.askyesno(
        "Confirmar Eliminación",
        "¿Estás seguro de que quieres eliminar el grupo seleccionado?"
    )
    
    if confirm:
        index = app.batch_tree.index(selected_item[0])
        del app.batch_groups[index]
        update_batch_treeview(app)
        messagebox.showinfo("Grupo Eliminado", "El grupo ha sido eliminado correctamente.")

def clear_all_batch_groups(app):
    """Elimina todos los grupos de la lista de lotes."""
    if not app.batch_groups:
        messagebox.showinfo("Lista Vacía", "No hay lotes que limpiar.")
        return
        
    confirm = messagebox.askyesno(
        "Confirmar Limpieza Total",
        "¿Estás seguro de que quieres eliminar TODOS los lotes de la lista?\nEsta acción no se puede deshacer."
    )
    
    if confirm:
        app.batch_groups.clear()
        update_batch_treeview(app)
        messagebox.showinfo("Lotes Eliminados", "Se han eliminado todos los lotes de la lista.")


def update_batch_treeview(app):
    """Actualiza la visualización de los grupos en el Treeview."""
    if not hasattr(app, 'batch_tree'):
        return
    for iid in app.batch_tree.get_children():
        app.batch_tree.delete(iid)

    for i, group in enumerate(app.batch_groups):
        display_paths = [os.path.basename(p) for p in group["paths"]]
        paths_str = ", ".join(display_paths[:2])
        if len(display_paths) > 2:
            paths_str += f", ... ({len(display_paths) - 2} más)"
        
        title = group.get("title_text", "")
        app.batch_tree.insert("", "end", iid=str(i), values=(group["count"], title, paths_str))

    # Forzar la actualización de la UI para asegurar que los cambios se muestren
    app.batch_tree.update_idletasks()


def start_batch_processing(app):
    """Inicia el procesamiento de todos los grupos."""
    if not app.batch_groups:
        messagebox.showwarning("Sin Grupos", "No hay grupos de imágenes para procesar.")
        return

    output_dir = filedialog.askdirectory(title="Selecciona la carpeta de destino para las imágenes generadas")
    if not output_dir:
        return

    app.save_settings() 

    try:
        # Generar un timestamp único para este lote
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        for i, group in enumerate(app.batch_groups):
            num_images_in_group = group["count"]
            image_paths = group["paths"]
            
            # Cargar imágenes para el grupo actual en una lista local
            current_slots = [None] * num_images_in_group
            for slot_idx in range(num_images_in_group):
                try:
                    current_slots[slot_idx] = Image.open(image_paths[slot_idx]).convert("RGBA")
                except Exception as e:
                    print(f"Error al cargar imagen del lote {image_paths[slot_idx]}: {e}")
            
            # Usar la configuración específica del grupo
            generated_image = compose_template(
                FINAL_SIZE, app.bg_img, 
                [s for s in current_slots if s is not None],
                app.current_emojis[:num_images_in_group],
                group.get("title_text", app.title_text.get()), 
                app.logo_img,
                font_family=group.get("font_family", app.font_family.get()),
                title_style=group.get("title_style", app.title_style.get()),
                image_shape=group.get("image_shape", app.image_shape.get()),
                logo_size=group.get("logo_size", app.logo_size.get()),
                logo_x=group.get("logo_x", app.logo_x.get()),
                logo_y=group.get("logo_y", app.logo_y.get()),
                num_slots=num_images_in_group,
                emoji_size=group.get("emoji_size", app.emoji_size.get()),
                emoji_x_offset=group.get("emoji_x_offset", app.emoji_x_offset.get()),
                emoji_y_offset=group.get("emoji_y_offset", app.emoji_y_offset.get())
            )
            
            output_filename = os.path.join(output_dir, f"plantilla_lote_{timestamp}_{i+1}.png")
            generated_image.save(output_filename, quality=95)
        
        messagebox.showinfo("Procesamiento de Lotes Completado", 
                            "Todas las imágenes del lote han sido generadas y guardadas.")

    except Exception as e:
        messagebox.showerror("Error en Lote", f"Ocurrió un error durante el procesamiento por lotes:\n{str(e)}")
    finally:
        # Restaura la UI principal a su estado visual
        if hasattr(app, '_update_slot_visibility'):
            app._update_slot_visibility()
        if hasattr(app, 'render_preview'):
            app.render_preview()