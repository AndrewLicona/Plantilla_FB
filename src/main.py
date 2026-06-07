#!/usr/bin/env python3
"""
main.py
GUI principal del generador de plantillas de reacciones
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
from src.config import CANVAS_SIZE, FINAL_SIZE, SLOT_MAX, HAS_TKDND, DND_FILES, TkinterDnD
from src.composer import compose_template
from src.ui.batch_panel import create_batch_panel, add_batch_group, update_batch_treeview
from src.ui.left_panel import create_left_panel
from src.ui.center_panel import create_center_panel
from src.ui.right_panel import create_right_panel


# --- Constantes ---
SETTINGS_FILE = "settings.json"


class TemplateGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Plantillas - Reacciones PRO")
        self.root.geometry("1300x800")
        
        # Estado
        self.slots = [None] * SLOT_MAX
        self.current_emojis = []
        self.n_slots = 3
        self.bg_img = None
        self.logo_img = None
        self.bg_img_path = None
        self.logo_img_path = None
        
        self.slot_buttons = []
        self.slot_labels = []
        
        # Estado de paneles colapsables
        self.left_panel_visible = True
        self.right_panel_visible = True
        
        # Variables de configuración
        self.title_text = tk.StringVar(value="¡VOTA POR TU CRACK!")
        self.font_family = tk.StringVar(value="Arial")
        self.title_style = tk.StringVar(value="impacto")
        self.image_shape = tk.StringVar(value="square")
        self.logo_size = tk.DoubleVar(value=0.20)
        self.logo_x = tk.DoubleVar(value=0.50)
        self.logo_y = tk.DoubleVar(value=0.50)
        self.emoji_pack = tk.StringVar(value="default")
        self.emoji_size = tk.DoubleVar(value=1.0)
        self.emoji_x_offset = tk.DoubleVar(value=0)
        self.emoji_y_offset = tk.DoubleVar(value=0)
        self.text_color = tk.StringVar(value="#FFFFFF")
        
        # Variables para la edición global
        self.apply_to_all_title = tk.IntVar(value=0)
        self.apply_to_all_style = tk.IntVar(value=0)

        self.preview_tk = None
        
        # Lista para almacenar grupos de imágenes para procesamiento por lotes
        self.batch_groups = []
        
        # Cargar configuración guardada
        self.load_settings()
        
        # Configurar estilo
        self.setup_styles()
        
        # Construir UI
        self.build_ui()
        
        # Cargar estado inicial después de construir la UI
        self._load_initial_state()

        # Guardar al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Guardar configuración al cerrar y salir."""
        self.save_settings()
        self.root.destroy()
    
    def save_settings(self):
        """Guarda la configuración actual en un archivo JSON."""
        settings = {
            "title_text": self.title_text.get(),
            "font_family": self.font_family.get(),
            "title_style": self.title_style.get(),
            "image_shape": self.image_shape.get(),
            "logo_size": self.logo_size.get(),
            "logo_x": self.logo_x.get(),
            "logo_y": self.logo_y.get(),
            "emoji_pack": self.emoji_pack.get(),
            "emoji_size": self.emoji_size.get(),
            "emoji_x_offset": self.emoji_x_offset.get(),
            "emoji_y_offset": self.emoji_y_offset.get(),
            "n_slots": self.n_slots,
            "bg_img_path": self.bg_img_path,
            "logo_img_path": self.logo_img_path,
            "batch_groups": self.batch_groups,
        }
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando la configuración: {e}")

    def load_settings(self):
        """Carga la configuración desde un archivo JSON."""
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            self.title_text.set(settings.get("title_text", self.title_text.get()))
            self.font_family.set(settings.get("font_family", self.font_family.get()))
            self.title_style.set(settings.get("title_style", self.title_style.get()))
            self.image_shape.set(settings.get("image_shape", self.image_shape.get()))
            self.logo_size.set(settings.get("logo_size", self.logo_size.get()))
            self.logo_x.set(settings.get("logo_x", self.logo_x.get()))
            self.logo_y.set(settings.get("logo_y", self.logo_y.get()))
            self.emoji_pack.set(settings.get("emoji_pack", self.emoji_pack.get()))
            self.emoji_size.set(settings.get("emoji_size", self.emoji_size.get()))
            self.emoji_x_offset.set(settings.get("emoji_x_offset", self.emoji_x_offset.get()))
            self.emoji_y_offset.set(settings.get("emoji_y_offset", self.emoji_y_offset.get()))
            self.n_slots = settings.get("n_slots", self.n_slots)

            self.bg_img_path = settings.get("bg_img_path")
            if self.bg_img_path and os.path.exists(self.bg_img_path):
                self.bg_img = Image.open(self.bg_img_path).convert("RGBA")
            
            self.logo_img_path = settings.get("logo_img_path")
            if self.logo_img_path and os.path.exists(self.logo_img_path):
                self.logo_img = Image.open(self.logo_img_path).convert("RGBA")
            
            self.batch_groups = settings.get("batch_groups", [])

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error cargando configuración, se usará la default: {e}")
        except Exception as e:
            print(f"Error inesperado cargando configuración: {e}")
            
    def _load_initial_state(self):
        """Carga el estado inicial de la UI después de que todos los widgets estén construidos."""
        self.update_emoji_packs()
        self.load_current_emojis()
        self._update_slot_visibility()
        self.render_preview()
        if hasattr(self, 'batch_tree'):
            update_batch_treeview(self)

    def update_emoji_packs(self):
        """Escanea el directorio de emojis y actualiza el selector de paquetes."""
        packs_path = "assets/emojis"
        if not os.path.exists(packs_path):
            self.emoji_pack_selector['values'] = ["default"]
            return

        try:
            packs = [d for d in os.listdir(packs_path) if os.path.isdir(os.path.join(packs_path, d))]
            if not packs:
                packs = ["default"]
            
            self.emoji_pack_selector['values'] = packs
            if self.emoji_pack.get() not in packs:
                self.emoji_pack.set(packs[0])
        except Exception as e:
            print(f"Error al buscar paquetes de emojis: {e}")
            self.emoji_pack_selector['values'] = ["default"]


    def load_current_emojis(self):
        """Carga los emojis del paquete actualmente seleccionado."""
        pack_name = self.emoji_pack.get()
        emojis_path = os.path.join("assets/emojis", pack_name)
        self.current_emojis = []

        if not os.path.exists(emojis_path):
            print(f"Advertencia: No se encontró el paquete de emojis '{pack_name}'")
            return
            
        emoji_files = sorted([f for f in os.listdir(emojis_path) if f.endswith(".png")])
        
        for filename in emoji_files:
            try:
                path = os.path.join(emojis_path, filename)
                emoji_img = Image.open(path).convert("RGBA")
                self.current_emojis.append(emoji_img)
            except Exception as e:
                print(f"Error al cargar emoji {filename} del paquete {pack_name}: {e}")

    def on_emoji_pack_change(self, event=None):
        """Se llama cuando el paquete de emojis cambia."""
        self.load_current_emojis()
        self.render_preview()

    def setup_styles(self):
        """Configura el tema visual"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Info.TLabel', foreground='gray')

    def create_tooltip(self, widget, text):
        """Crea un tooltip para un widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief=tk.SOLID, borderwidth=1, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def build_ui(self):
        """Construye la interfaz completa"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo con botón de toggle integrado
        self.left_container = ttk.Frame(main_frame)
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.left_frame = ttk.LabelFrame(self.left_container, text="📁 Imágenes", padding=10)
        self.left_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botón de toggle flotante para panel izquierdo - posición ajustada
        self.left_toggle_btn = ttk.Button(main_frame, text="◀", command=self.toggle_left_panel, width=2)
        self.left_toggle_btn.grid(row=0, column=0, sticky="ne", padx=(0, 8), pady=(8, 0))
        self.create_tooltip(self.left_toggle_btn, "Colapsar panel izquierdo (Ctrl+← o F9)")
        
        # Panel central
        center = ttk.LabelFrame(main_frame, text="👁️ Vista Previa", padding=10)
        center.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Panel derecho con botón de toggle integrado
        self.right_container = ttk.Frame(main_frame)
        self.right_container.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self.notebook = ttk.Notebook(self.right_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Botón de toggle flotante para panel derecho - posición mejorada
        self.right_toggle_btn = ttk.Button(main_frame, text="▶", command=self.toggle_right_panel, width=2)
        self.right_toggle_btn.grid(row=0, column=2, sticky="ne", padx=(0, 8), pady=(8, 0))
        self.create_tooltip(self.right_toggle_btn, "Colapsar panel derecho (Ctrl+→ o F10)")
        
        config_tab_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(config_tab_frame, text="Avanzado ⚙️")

        self.batch_tab_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.batch_tab_frame, text="Lotes 📦")
        
        # Configuración de columnas con pesos dinámicos
        main_frame.columnconfigure(0, weight=1, minsize=50)  # Mínimo pequeño cuando colapsado
        main_frame.columnconfigure(1, weight=2, minsize=560)
        main_frame.columnconfigure(2, weight=1, minsize=50)  # Mínimo pequeño cuando colapsado
        main_frame.rowconfigure(0, weight=1)
        
        create_left_panel(self.left_frame, self)
        create_center_panel(center, self)
        create_right_panel(config_tab_frame, self)
        create_batch_panel(self.batch_tab_frame, self)
        
        # Atajos de teclado para paneles
        self.root.bind('<Control-Left>', lambda e: self.toggle_left_panel())
        self.root.bind('<Control-Right>', lambda e: self.toggle_right_panel())
        self.root.bind('<F9>', lambda e: self.toggle_left_panel())
        self.root.bind('<F10>', lambda e: self.toggle_right_panel())

    def toggle_left_panel(self):
        """Alterna la visibilidad del panel izquierdo."""
        self.left_panel_visible = not self.left_panel_visible
        main_frame = self.left_container.master
        
        if self.left_panel_visible:
            # Expandir panel
            self.left_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            main_frame.columnconfigure(0, weight=1, minsize=280)
            self.left_toggle_btn.config(text="◀")
            self.update_tooltip(self.left_toggle_btn, "Colapsar panel izquierdo (Ctrl+← o F9)")
        else:
            # Colapsar panel
            self.left_container.grid_remove()
            main_frame.columnconfigure(0, weight=0, minsize=50)
            self.left_toggle_btn.config(text="▶")
            self.update_tooltip(self.left_toggle_btn, "Expandir panel izquierdo (Ctrl+← o F9)")
        self.root.update_idletasks()

    def toggle_right_panel(self):
        """Alterna la visibilidad del panel derecho."""
        self.right_panel_visible = not self.right_panel_visible
        main_frame = self.right_container.master
        
        if self.right_panel_visible:
            # Expandir panel
            self.right_container.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
            main_frame.columnconfigure(2, weight=1, minsize=320)
            self.right_toggle_btn.config(text="▶")
            self.update_tooltip(self.right_toggle_btn, "Colapsar panel derecho (Ctrl+→ o F10)")
        else:
            # Colapsar panel
            self.right_container.grid_remove()
            main_frame.columnconfigure(2, weight=0, minsize=50)
            self.right_toggle_btn.config(text="◀")
            self.update_tooltip(self.right_toggle_btn, "Expandir panel derecho (Ctrl+→ o F10)")
        self.root.update_idletasks()

    def update_tooltip(self, widget, text):
        """Actualiza el texto de un tooltip."""
        # Eliminar eventos anteriores
        widget.unbind("<Enter>")
        widget.unbind("<Leave>")
        # Crear nuevo tooltip
        self.create_tooltip(widget, text)

    def set_image_shape(self, shape_name):
        self.image_shape.set(shape_name)
        self.render_preview()

    def set_font(self, font_name):
        self.font_family.set(font_name)
        self.render_preview()

    def set_title_style(self, style_name):
        self.title_style.set(style_name)
        self.render_preview()

    def on_style_change(self, style_name):
        """Se llama cuando el estilo del título cambia."""
        self.set_title_style(style_name)
        if self.apply_to_all_style.get():
            for group in self.batch_groups:
                group["title_style"] = style_name
            messagebox.showinfo("Actualización Global", f"El estilo '{style_name}' se ha aplicado a todos los grupos del lote.")

    def on_title_change(self):
        """Se llama cuando el texto del título cambia."""
        self.render_preview()
        if self.apply_to_all_title.get():
            new_title = self.title_text.get()
            for group in self.batch_groups:
                group["title_text"] = new_title
            update_batch_treeview(self)

    def _update_n_slots_and_render(self, new_n_slots):
        self.n_slots = new_n_slots
        self._update_slot_visibility()
        self.render_preview()

    def _update_slot_visibility(self):
        for i in range(SLOT_MAX):
            is_visible = (i < self.n_slots)
            state = 'normal' if is_visible else 'disabled'
            
            self.slot_buttons[i].config(state=state)
            
            if not is_visible:
                self.slot_labels[i].config(text="", style='Info.TLabel')

    def add_image(self, idx):
        paths = filedialog.askopenfilenames(
            title="Selecciona imagen(es)",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp"), ("Todos", "*.*")]
        )
        if not paths:
            return
        
        for i, p in enumerate(paths):
            slot = idx + i
            if slot >= SLOT_MAX:
                break
            try:
                self.slots[slot] = Image.open(p).convert("RGBA")
                self.slot_labels[slot].config(text="✓ Cargada", style='Success.TLabel')
                self.slot_buttons[slot].config(text=f"📁 Cambiar {slot+1}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar:\n{str(e)}")
        
        self.render_preview()

    def clear_slot_images(self):
        if messagebox.askyesno("Confirmar", "¿Limpiar todas las imágenes de los slots?"):
            self.slots = [None] * SLOT_MAX
            for i in range(SLOT_MAX):
                self.slot_labels[i].config(text="", style='Info.TLabel')
                self.slot_buttons[i].config(text=f"📁 Imagen {i+1}")
            self.render_preview()

    def remove_image(self, idx):
        self.slots[idx] = None
        self.slot_labels[idx].config(text="", style='Info.TLabel')
        self.slot_buttons[idx].config(text=f"📁 Imagen {idx+1}")
        self.render_preview()

    def load_bg(self):
        p = filedialog.askopenfilename(title="Selecciona fondo", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp")])
        if p:
            try:
                self.bg_img = Image.open(p).convert("RGBA")
                self.bg_img_path = p
                self.bg_label.config(text="✓ Fondo cargado", style='Success.TLabel')
            except Exception as e:
                messagebox.showerror("Error", str(e))
        self.render_preview()

    def load_logo(self):
        p = filedialog.askopenfilename(title="Selecciona logo", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp")])
        if p:
            try:
                self.logo_img = Image.open(p).convert("RGBA")
                self.logo_img_path = p
                self.logo_label.config(text="✓ Logo cargado", style='Success.TLabel')
            except Exception as e:
                messagebox.showerror("Error", str(e))
        self.render_preview()

    def clear_all(self):
        if messagebox.askyesno("Confirmar", "¿Limpiar todo?"):
            self.slots = [None] * SLOT_MAX
            self.bg_img = None
            self.logo_img = None
            self.bg_img_path = None
            self.logo_img_path = None
            self.title_text.set("¡VOTA POR TU CRACK!")
            
            for i in range(SLOT_MAX):
                self.slot_labels[i].config(text="", style='Info.TLabel')
                self.slot_buttons[i].config(text=f"📁 Imagen {i+1}")
            
            self.bg_label.config(text="Sin fondo", style='Info.TLabel')
            self.logo_label.config(text="Sin logo", style='Info.TLabel')
            
            self.render_preview()

    def on_drop(self, event):
        paths = self.root.splitlist(event.data)
        
        # --- Lógica de Detección por Coordenadas ---
        is_drop_on_batch_tab = False
        try:
            # Forzar la actualización de la geometría de los widgets
            self.batch_tab_frame.update_idletasks()
            
            # Coordenadas del drop
            x_drop, y_drop = event.x_root, event.y_root
            
            # Geometría del área de la pestaña de lotes
            x_tab = self.batch_tab_frame.winfo_rootx()
            y_tab = self.batch_tab_frame.winfo_rooty()
            width_tab = self.batch_tab_frame.winfo_width()
            height_tab = self.batch_tab_frame.winfo_height()

            # Comprobar si el drop ocurrió dentro de los límites de la pestaña
            if (x_tab <= x_drop <= x_tab + width_tab and
                y_tab <= y_drop <= y_tab + height_tab):
                is_drop_on_batch_tab = True
        except Exception as e:
            print(f"Error detectando el target del drop: {e}")
            is_drop_on_batch_tab = False # Volver a un estado seguro

        if is_drop_on_batch_tab:
            num_dropped_images = len(paths)
            if num_dropped_images in [2, 3, 4]:
                add_batch_group(self, paths=paths)
                # Cambiar a la pestaña de lotes si no está ya seleccionada
                self.notebook.select(self.batch_tab_frame)
            else:
                messagebox.showwarning("Cantidad Incorrecta", "Arrastra 2, 3 o 4 imágenes para crear un grupo en la pestaña de lotes.")
        else:
            # Lógica existente para arrastrar y soltar en slots individuales
            for p in paths:
                for i in range(SLOT_MAX):
                    if self.slots[i] is None:
                        try:
                            self.slots[i] = Image.open(p).convert("RGBA")
                            self.slot_labels[i].config(text="✓ Cargada", style='Success.TLabel')
                            break
                        except Exception as e:
                            messagebox.showerror("Error", f"Error al cargar:\n{str(e)}")
            self.render_preview()

    def render_preview(self):
        """Renderizar vista previa"""
        try:
            slots_count = self.n_slots
            imgs = [s for s in self.slots[:slots_count] if s is not None]
            
            while len(imgs) < slots_count:
                placeholder = Image.new("RGBA", (300, 300), (80, 80, 90, 255))
                from PIL import ImageDraw
                from src.utils import load_font
                draw = ImageDraw.Draw(placeholder)
                fnt = load_font('arial_bold', 120)
                bbox = draw.textbbox((0, 0), "?", font=fnt)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                draw.text((150 - tw//2, 150 - th//2), "?", fill=(200, 200, 200), font=fnt)
                imgs.append(placeholder)
            
            emojis = self.current_emojis[:slots_count]
            
            preview = compose_template(
                CANVAS_SIZE, self.bg_img, imgs, emojis, self.title_text.get(), self.logo_img,
                font_family=self.font_family.get(),
                title_style=self.title_style.get(),
                image_shape=self.image_shape.get(),
                logo_size=self.logo_size.get(),
                logo_x=self.logo_x.get(),
                logo_y=self.logo_y.get(),
                emoji_size=self.emoji_size.get(),
                emoji_x_offset=self.emoji_x_offset.get(),
                emoji_y_offset=self.emoji_y_offset.get(),
                num_slots=slots_count,
                text_color=self.text_color.get()
            )
            
            # Convertir a PhotoImage y mostrar
            self.preview_img = ImageTk.PhotoImage(preview)
            self.preview_canvas.delete("all")
            # Centrar la imagen en el canvas (540x540 / 2 = 270,270)
            self.preview_canvas.create_image(270, 270, image=self.preview_img)
            
        except Exception as e:
            print(f"Error en render_preview: {e}")
            # Mostrar placeholder en caso de error
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(270, 270, text="Error en preview", fill="red")

    def generate_and_save(self):
        """Generar y guardar plantilla final"""
        slots_count = self.n_slots
        imgs = [s for s in self.slots[:slots_count] if s is not None]
        
        if len(imgs) < slots_count:
            messagebox.showerror("Error", f"Faltan imágenes. Necesitas {slots_count}.")
            return
        
        emojis = self.current_emojis[:slots_count]
        
        try:
            out = compose_template(
                FINAL_SIZE, self.bg_img, imgs, emojis, self.title_text.get(), self.logo_img,
                font_family=self.font_family.get(),
                title_style=self.title_style.get(),
                image_shape=self.image_shape.get(),
                logo_size=self.logo_size.get(),
                logo_x=self.logo_x.get(),
                logo_y=self.logo_y.get(),
                num_slots=slots_count,
                emoji_size=self.emoji_size.get(),
                emoji_x_offset=self.emoji_x_offset.get(),
                emoji_y_offset=self.emoji_y_offset.get(),
                text_color=self.text_color.get()
            )
            
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")],
                initialfile="plantilla_reaccion.png"
            )
            
            if not path:
                return
            
            base_path, ext = os.path.splitext(path)
            counter = 0
            new_path = path
            while os.path.exists(new_path):
                counter += 1
                new_path = f"{base_path} ({counter}){ext}"
            
            out.save(new_path, quality=95)
            messagebox.showinfo("✅ Éxito", f"Plantilla guardada en:\n{new_path}")
            
            self.save_settings()

        except Exception as e:
            messagebox.showerror("Error al guardar", f"Error al guardar:\n{str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Función principal"""
    try:
        if HAS_TKDND and TkinterDnD:
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()
        
        app = TemplateGeneratorApp(root)
        root.mainloop()
    except Exception as e:
        print("Error al iniciar:", e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()