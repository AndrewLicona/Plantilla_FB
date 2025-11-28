"""
utils.py
Funciones auxiliares para procesamiento de imágenes
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from config import FONT_FILENAMES, FONT_SCALING_FACTORS


def resource_path(relative):
    """Para PyInstaller."""
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, relative)


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
    # Usar ImageOps.pad para escalar y rellenar manteniendo el aspect ratio
    img = ImageOps.pad(img.convert("RGBA"), (size, size), color=(0, 0, 0, 0))
    
    if shape == 'circle':
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        img.putalpha(mask)
    elif shape == 'rounded':
        mask = create_rounded_rectangle_mask((size, size), radius)
        img.putalpha(mask)
    elif shape == 'square':
        # Ya está en forma cuadrada, solo asegurar bordes limpios
        pass
    
    return img


def add_shadow_to_image(base, img, position, shadow_offset=15, shadow_blur=10):
    """Añade sombra a una imagen"""
    x, y = position
    size = img.size[0]
    
    # Crear sombra
    shadow = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    
    # Forma según la imagen
    if img.mode == 'RGBA':
        # Detectar si es circular o cuadrada
        sdraw.rectangle((15, 15, size + 15, size + 15), fill=(0, 0, 0, 140))
    
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    # Pegar sombra
    base.paste(shadow, (x - 20 + shadow_offset, y + shadow_offset), shadow)


def paste_with_shadow(base, img, position):
    """Pega una imagen con sombra automática"""
    add_shadow_to_image(base, img, position)
    base.paste(img, position, img)