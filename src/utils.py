"""
utils.py
Funciones auxiliares para procesamiento de imágenes
"""

import os
import sys
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from src.config import FONT_FILENAMES, FONT_SCALING_FACTORS


def resource_path(relative):
    """Para PyInstaller."""
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, relative)


def get_system_fonts():
    """Obtiene todas las fuentes disponibles en el sistema."""
    try:
        import tkinter.font as tkFont
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana temporal
        
        # Obtener todas las familias de fuentes
        font_families = sorted(tkFont.families())
        
        root.destroy()
        return font_families
    except Exception as e:
        print(f"Error obteniendo fuentes del sistema: {e}")
        # Fallback a fuentes básicas
        return ["Arial", "Times New Roman", "Courier New", "Verdana", "Impact", "Comic Sans MS"]


def load_font(font_family='arial_bold', size=72, scale_factor=1.0):
    """Carga una fuente buscando en los directorios del sistema."""
    
    # Obtener nombres de archivo candidatos para la familia de fuentes
    font_filenames = FONT_FILENAMES.get(font_family, FONT_FILENAMES['arial_bold'])
    scaled_size = int(size * scale_factor)
    
    # Obtener directorios de fuentes del sistema
    font_dirs = []
    if sys.platform == "win32":
        font_dirs.append(os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts"))
    elif sys.platform == "linux":
        font_dirs.extend(['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')])
    elif sys.platform == "darwin":
        font_dirs.extend(['/System/Library/Fonts', '/Library/Fonts', os.path.expanduser('~/Library/Fonts')])

    # Buscar la fuente en los directorios del sistema
    for font_dir in font_dirs:
        for filename in font_filenames:
            font_path = os.path.join(font_dir, filename)
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, scaled_size)
            except Exception:
                continue
    
    # Fallback a la fuente por defecto de PIL si no se encuentra
    return ImageFont.load_default(size)


def apply_cover_background(base, fondo_img):
    """Aplica una imagen de fondo tipo 'cover'"""
    if not fondo_img:
        return base
    
    W, H = base.size
    f = fondo_img.convert("RGBA")
    fw, fh = f.size
    
    # Escalar para cubrir completamente
    scale = max(W/fw, H/fh)
    f = f.resize((int(fw*scale), int(fh*scale)), Image.LANCZOS)
    
    # Centrar y recortar
    fx = (f.width - W) // 2
    fy = (f.height - H) // 2
    sub = f.crop((fx, fy, fx + W, fy + H))
    
    base.paste(sub, (0, 0), sub)
    return base


def draw_text_with_style(draw, text, position, font, color, style, width, height):
    """Dibuja texto con diferentes estilos"""
    x, y = position
    
    # Sombra
    if style.get('shadow', False):
        offset = style.get('shadow_offset', 4)
        blur = style.get('shadow_blur', 0)
        
        if blur > 0:
            # Crear capa temporal para sombra difuminada
            shadow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            shadow_draw.text((x + offset, y + offset), text, 
                           fill=(0, 0, 0, 180), font=font)
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur))
            draw._image.paste(shadow_layer, (0, 0), shadow_layer)
        else:
            draw.text((x + offset, y + offset), text, 
                     fill=(0, 0, 0, 180), font=font)
    
    # Contorno
    if style.get('outline', False):
        outline_width = style.get('outline_width', 3)
        outline_color = style.get('outline_color', (0, 0, 0))
        
        # Dibujar texto en todas las direcciones para simular contorno
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, 
                            fill=outline_color, font=font)
    
    # Texto principal
    draw.text((x, y), text, fill=color, font=font)


def create_rounded_rectangle_mask(size, radius=20):
    """Crea una máscara para esquinas redondeadas"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    return mask


def apply_shape_to_image(img, shape='square', size=300, radius=20):
    """Aplica diferentes formas a una imagen"""
    # Convertir a RGBA y escalar manteniendo aspect ratio
    img = img.convert("RGBA")
    img = ImageOps.pad(img, (size, size), color=(255, 255, 255, 0))  # Fondo transparente blanco
    
    if shape == 'circle':
        # Crear máscara circular
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Crear imagen final con fondo transparente
        result = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        result.paste(img, (0, 0), mask)
        return result
    elif shape == 'rounded':
        # Crear máscara redondeada
        mask = create_rounded_rectangle_mask((size, size), radius)
        
        # Crear imagen final con fondo transparente
        result = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        result.paste(img, (0, 0), mask)
        return result
    elif shape == 'square':
        # Ya está en forma cuadrada, solo asegurar bordes limpios
        return img
    
    return img


def add_shadow_to_image(base, img, position, shadow_offset=8, shadow_blur=12):
    """Añade sombra mejorada y más natural a una imagen"""
    x, y = position
    size = img.size[0]
    
    # Calcular espacio extra para el desenfoque de la sombra
    padding = shadow_blur + shadow_offset
    shadow_size = size + (padding * 2)
    
    # Crear sombra con espacio suficiente para el desenfoque
    shadow = Image.new("RGBA", (shadow_size, shadow_size), (0, 0, 0, 0))
    
    # Detectar la forma de la imagen y crear sombra correspondiente
    if img.mode == 'RGBA':
        # Extraer el canal alfa para determinar la forma
        alpha = img.split()[-1]
        
        # Crear sombra basada en la forma real de la imagen (centrada en el canvas de sombra)
        shadow_img = Image.new("RGBA", (shadow_size, shadow_size), (0, 0, 0, 0))
        
        # Pegar la forma de la imagen en el centro del canvas de sombra
        shadow_alpha = Image.new("L", (shadow_size, shadow_size), 0)
        shadow_alpha.paste(alpha, (padding, padding))
        
        # Crear la sombra con la forma correcta
        shadow_color = Image.new("RGBA", (shadow_size, shadow_size), (0, 0, 0, 80))
        shadow_color.putalpha(shadow_alpha)
        
        # Aplicar desenfoque gaussiano para efecto de sombra suave
        shadow_color = shadow_color.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Calcular posición para centrar la sombra respecto a la imagen
        shadow_x = x - padding
        shadow_y = y - padding
        
        # Pegar sombra
        base.paste(shadow_color, (shadow_x, shadow_y), shadow_color)
    else:
        # Para imágenes sin canal alfa, crear sombra rectangular suave
        shadow_rect = Image.new("RGBA", (shadow_size, shadow_size), (0, 0, 0, 60))
        shadow_rect = shadow_rect.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Calcular posición para centrar
        shadow_x = x - padding
        shadow_y = y - padding
        
        base.paste(shadow_rect, (shadow_x, shadow_y), shadow_rect)


def paste_with_shadow(base, img, position):
    """Pega una imagen con sombra automática mejorada"""
    add_shadow_to_image(base, img, position)
    base.paste(img, position, img)