#!/usr/bin/env python3
"""
main.py
GUI principal del generador de plantillas de reacciones
"""

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
from config import CANVAS_SIZE, FINAL_SIZE, SLOT_MAX, HAS_TKDND, DND_FILES, TkinterDnD
from composer import compose_template
from ui.batch_panel import create_batch_panel, add_batch_group, update_batch_treeview
from ui.left_panel import create_left_panel
from ui.center_panel import create_center_panel
from ui.right_panel import create_right_panel


# --- Constantes ---
SETTINGS_FILE = "settings.json"


class TemplateGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Plantillas - Reacciones PRO")
        self.root.geometry("1300x800")
        
        # Estado
        self.slots = [None] * SLOT_MAX
        self.default_emojis = self.load_default_emojis()
        self.n_slots = 3
        self.bg_img = None
        self.logo_img = None
        self.bg_img_path = None
        self.logo_img_path = None
        
        self.slot_buttons = []
        self.slot_labels = []
        self.remove_buttons = []
        
        # Variables de configuración
        self.title_text = tk.StringVar(value="¡VOTA POR TU CRACK!")
        self.font_family = tk.StringVar(value="arial_bold")
        self.title_style = tk.StringVar(value="impacto")
        self.image_shape = tk.StringVar(value="square")
        self.logo_size = tk.DoubleVar(value=0.20)
        self.logo_x = tk.DoubleVar(value=0.50)
        self.logo_y = tk.DoubleVar(value=0.50)
        self.emoji_size = tk.DoubleVar(value=1.0)
        self.emoji_x_offset = tk.DoubleVar(value=0)
        self.emoji_y_offset = tk.DoubleVar(value=0)
        
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
            "emoji_size": self.emoji_size.get(),
            "emoji_x_offset": self.emoji_x_offset.get(),
            "emoji_y_offset": self.emoji_y_offset.get(),
            "n_slots": self.n_slots,
            "bg_img_path": self.bg_img_path,
            "logo_img_path": self.logo_img_path,
            "batch_groups": self.batch_groups,
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error guardando la configuración: {e}")

    def load_settings(self):
        """Carga la configuración desde un archivo JSON."""
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
            
            self.title_text.set(settings.get("title_text", self.title_text.get()))
            self.font_family.set(settings.get("font_family", self.font_family.get()))
            self.title_style.set(settings.get("title_style", self.title_style.get()))
            self.image_shape.set(settings.get("image_shape", self.image_shape.get()))
            self.logo_size.set(settings.get("logo_size", self.logo_size.get()))
            self.logo_x.set(settings.get("logo_x", self.logo_x.get()))
            self.logo_y.set(settings.get("logo_y", self.logo_y.get()))
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
        self._update_slot_visibility()
        self.render_preview()
        if hasattr(self, 'batch_tree'):
            update_batch_treeview(self)

    def load_default_emojis(self):
        """Carga los emojis desde el directorio assets"""
        emojis = []
        assets_path = "assets"
        if not os.path.exists(assets_path):
            return []
            
        emoji_files = sorted([f for f in os.listdir(assets_path) if f.startswith("fc_reaccion") and f.endswith(".png")])
        
        for filename in emoji_files:
            try:
                path = os.path.join(assets_path, filename)
                emoji_img = Image.open(path).convert("RGBA")
                emojis.append(emoji_img)
            except Exception as e:
                print(f"Error al cargar emoji {filename}: {e}")
        return emojis

    def setup_styles(self):
        """Configura el tema visual"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Info.TLabel', foreground='gray')

    def build_ui(self):
        """Construye la interfaz completa"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left = ttk.LabelFrame(main_frame, text="📸 Imágenes", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        center = ttk.LabelFrame(main_frame, text="👁️ Vista Previa", padding=10)
        center.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        config_tab_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(config_tab_frame, text="Avanzado ⚙️")

        self.batch_tab_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.batch_tab_frame, text="Lotes 📦")
        
        main_frame.columnconfigure(0, weight=1, minsize=280)
        main_frame.columnconfigure(1, weight=2, minsize=560)
        main_frame.columnconfigure(2, weight=1, minsize=320)
        main_frame.rowconfigure(0, weight=1)
        
        create_left_panel(left, self)
        create_center_panel(center, self)
        create_right_panel(config_tab_frame, self)
        create_batch_panel(self.batch_tab_frame, self)

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
            
            parent_frame = self.slot_buttons[i].winfo_parent()
            slot_card_frame_widget = self.root.nametowidget(parent_frame)

            if is_visible:
                slot_card_frame_widget.grid()
                state = 'normal'
            else:
                slot_card_frame_widget.grid_remove()
                state = 'disabled'
            
            self.slot_buttons[i].config(state=state)
            self.remove_buttons[i].config(state=state)
            
            if not is_visible:
                self.slot_labels[i].config(text="", style='Info.TLabel')
        
        self.render_preview()

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
                from utils import load_font
                draw = ImageDraw.Draw(placeholder)
                fnt = load_font('arial_bold', 120)
                bbox = draw.textbbox((0, 0), "?", font=fnt)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                draw.text((150 - tw//2, 150 - th//2), "?", fill=(200, 200, 200), font=fnt)
                imgs.append(placeholder)
            
            emojis = self.default_emojis[:slots_count]
            
            preview = compose_template(
                CANVAS_SIZE, self.bg_img, imgs, emojis, self.title_text.get(), self.logo_img,
                font_family=self.font_family.get(),
                title_style=self.title_style.get(),
                image_shape=self.image_shape.get(),
                logo_size=self.logo_size.get(),
                logo_x=self.logo_x.get(),
                logo_y=self.logo_y.get(),
                num_slots=slots_count,
                emoji_size=self.emoji_size.get(),
                emoji_x_offset=self.emoji_x_offset.get(),
                emoji_y_offset=self.emoji_y_offset.get()
            )
            
            self.preview_tk = ImageTk.PhotoImage(preview)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(CANVAS_SIZE[0]//2, CANVAS_SIZE[1]//2, image=self.preview_tk)
        except Exception as e:
            messagebox.showerror("Error en preview", str(e))
            import traceback
            traceback.print_exc()

    def generate_and_save(self):
        """Generar y guardar plantilla final"""
        slots_count = self.n_slots
        imgs = [s for s in self.slots[:slots_count] if s is not None]
        
        if len(imgs) < slots_count:
            messagebox.showerror("Error", f"Faltan imágenes. Necesitas {slots_count}.")
            return
        
        emojis = self.default_emojis[:slots_count]
        
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
                emoji_y_offset=self.emoji_y_offset.get()
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