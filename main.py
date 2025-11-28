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
from config import CANVAS_SIZE, FINAL_SIZE, SLOT_MAX
from composer import compose_template

# --- Constantes ---
SETTINGS_FILE = "settings.json"

# Intentar importar tkinterdnd2
HAS_TKDND = False
try:
    import importlib
    _tkdnd_mod = importlib.import_module("tkinterdnd2")
    DND_FILES = getattr(_tkdnd_mod, "DND_FILES", None)
    TkinterDnD = getattr(_tkdnd_mod, "TkinterDnD", None)
    HAS_TKDND = (DND_FILES is not None and TkinterDnD is not None)
except Exception:
    HAS_TKDND = False


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
        
        self.preview_tk = None
        
        # Cargar configuración guardada
        self.load_settings()
        
        # Configurar estilo
        self.setup_styles()
        
        # Construir UI
        self.build_ui()
        self._update_slot_visibility()
        
        # Renderizar preview inicial
        self.render_preview()

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

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error cargando configuración, se usará la default: {e}")
        except Exception as e:
            print(f"Error inesperado cargando configuración: {e}")

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
        
        right = ttk.LabelFrame(main_frame, text="⚙️ Configuración", padding=10)
        right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        main_frame.columnconfigure(0, weight=1, minsize=280)
        main_frame.columnconfigure(1, weight=2, minsize=560)
        main_frame.columnconfigure(2, weight=1, minsize=320)
        main_frame.rowconfigure(0, weight=1)
        
        self.build_left_panel(left)
        self.build_center_panel(center)
        self.build_right_panel(right)

    def build_left_panel(self, parent):
        """Panel izquierdo: imágenes, formas y emojis"""
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
            
            btn_img = ttk.Button(slot_card_frame, text=f"📁 Imagen {i+1}", width=12, command=lambda idx=i: self.add_image(idx))
            btn_img.grid(row=0, column=0, sticky="ew", padx=(0,2), pady=(0,2))

            rm = ttk.Button(slot_card_frame, text="❌", width=3, command=lambda idx=i: self.remove_image(idx))
            rm.grid(row=0, column=1, sticky="e", pady=(0,2))
            self.remove_buttons.append(rm)
            
            self.slot_buttons.append(btn_img)
            
            lbl = ttk.Label(slot_card_frame, text="", style='Info.TLabel', anchor=tk.CENTER)
            lbl.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,2))
            self.slot_labels.append(lbl)

        ttk.Button(parent, text="🗑️ Limpiar Imágenes", command=self.clear_slot_images).pack(fill=tk.X, pady=5)
        ttk.Separator(parent).pack(fill=tk.X, pady=10)
        
        ttk.Label(parent, text="Cantidad de imágenes:").pack(anchor=tk.W)
        
        slots_button_frame = ttk.Frame(parent)
        slots_button_frame.pack(fill=tk.X, pady=5)
        
        row, col = 0, 0
        for n in range(2, SLOT_MAX + 1):
            btn = ttk.Button(slots_button_frame, text=str(n), command=lambda num=n: self._update_n_slots_and_render(num), width=10)
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
            btn = ttk.Button(shape_button_frame, text=name, command=lambda v=value: self.set_image_shape(v), width=10)
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

        ttk.Label(parent, text="Tamaño Emoji:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(parent, from_=0.1, to=3.0, variable=self.emoji_size, command=lambda e: self.render_preview()).pack(fill=tk.X, padx=5)

        ttk.Label(parent, text="Posición X Emoji:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(parent, from_=-100, to=100, variable=self.emoji_x_offset, command=lambda e: self.render_preview()).pack(fill=tk.X, padx=5)

        ttk.Label(parent, text="Posición Y Emoji:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(parent, from_=-100, to=100, variable=self.emoji_y_offset, command=lambda e: self.render_preview()).pack(fill=tk.X, padx=5)
        
        ttk.Separator(parent).pack(fill=tk.X, pady=15)

    def set_image_shape(self, shape_name):
        self.image_shape.set(shape_name)
        self.render_preview()

    def build_center_panel(self, parent):
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(pady=10)
        
        self.preview_canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE[0], height=CANVAS_SIZE[1], bg="#12121a", highlightthickness=2, highlightbackground="#444")
        self.preview_canvas.pack()
        
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(title_frame, text="Título:", style='Header.TLabel').pack(anchor=tk.W)
        self.title_entry = ttk.Entry(title_frame, textvariable=self.title_text, font=('Arial', 12))
        self.title_entry.pack(fill=tk.X, pady=5)
        self.title_entry.bind("<KeyRelease>", lambda e: self.render_preview())
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="💾 Guardar Plantilla", command=self.generate_and_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Actualizar Vista", command=self.render_preview).pack(side=tk.LEFT, padx=5)

    def build_right_panel(self, parent):
        ttk.Label(parent, text="Fondo y Logo:", style='Header.TLabel').pack(pady=(0, 10))
        
        ttk.Button(parent, text="🖼️ Cargar Fondo", command=self.load_bg).pack(fill=tk.X, pady=3)
        self.bg_label = ttk.Label(parent, text="Sin fondo", style='Info.TLabel')
        self.bg_label.pack(fill=tk.X)
        
        ttk.Button(parent, text="🏷️ Cargar Logo", command=self.load_logo).pack(fill=tk.X, pady=3)
        self.logo_label = ttk.Label(parent, text="Sin logo", style='Info.TLabel')
        self.logo_label.pack(fill=tk.X)
        
        ttk.Label(parent, text="Tamaño Logo:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(parent, from_=0.05, to=0.8, variable=self.logo_size, command=lambda e: self.render_preview()).pack(fill=tk.X, padx=5)

        ttk.Label(parent, text="Posición X Logo:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(parent, from_=0, to=1, variable=self.logo_x, command=lambda e: self.render_preview()).pack(fill=tk.X, padx=5)

        ttk.Label(parent, text="Posición Y Logo:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(parent, from_=0, to=1, variable=self.logo_y, command=lambda e: self.render_preview()).pack(fill=tk.X, padx=5)
        
        ttk.Separator(parent).pack(fill=tk.X, pady=15)
        
        ttk.Label(parent, text="Estilo de Título:", style='Header.TLabel').pack(pady=(0, 5))
        
        ttk.Label(parent, text="Fuente:").pack(anchor=tk.W)
        
        font_button_frame = ttk.Frame(parent)
        font_button_frame.pack(fill=tk.X, pady=2)
        
        fonts = [
            ("Arial Bold", "arial_bold"), ("Impact", "impact"), ("Comic Sans", "comic"),
            ("Times", "times"), ("Burbank", "burbank"), ("Montserrat", "montserrat")
        ]
        
        row, col = 0, 0
        for name, value in fonts:
            btn = ttk.Button(font_button_frame, text=name, command=lambda v=value: self.set_font(v), width=10)
            btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        font_button_frame.columnconfigure(0, weight=1)
        font_button_frame.columnconfigure(1, weight=1)
        font_button_frame.columnconfigure(2, weight=1)
        
        ttk.Separator(parent).pack(fill=tk.X, pady=10)
        
        ttk.Label(parent, text="Efecto:").pack(anchor=tk.W)

        effect_button_frame = ttk.Frame(parent)
        effect_button_frame.pack(fill=tk.X, pady=2)

        effects = [
            ("Simple", "simple"), ("Contorno", "contorno"),
            ("Sombra Suave", "sombra_suave"), ("Impacto", "impacto")
        ]
        
        row, col = 0, 0
        for name, value in effects:
            btn = ttk.Button(effect_button_frame, text=name, command=lambda v=value: self.set_title_style(v), width=10)
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
        
        ttk.Button(parent, text="🗑️ Limpiar Todo", command=self.clear_all).pack(fill=tk.X, pady=5)
        
        if HAS_TKDND:
            ttk.Label(parent, text="✅ Drag & Drop activado", foreground="green").pack(pady=10)
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind('<<Drop>>', self.on_drop)
            except:
                pass

    def set_font(self, font_name):
        self.font_family.set(font_name)
        self.render_preview()

    def set_title_style(self, style_name):
        self.title_style.set(style_name)
        self.render_preview()

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
        for p in paths:
            for i in range(SLOT_MAX):
                if self.slots[i] is None:
                    try:
                        self.slots[i] = Image.open(p).convert("RGBA")
                        self.slot_labels[i].config(text="✓ Cargada", style='Success.TLabel')
                        break
                    except:
                        pass
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
