"""
composer.py
Lógica principal para componer las plantillas
"""

from PIL import Image, ImageDraw, ImageFilter
from src.config import (
    DEFAULT_BG_COLOR, IMAGE_LAYOUTS, TITLE_POSITION, 
    TITLE_COLOR, TITLE_STYLES, FONT_SCALING_FACTORS
)
from src.utils import (
    apply_cover_background, draw_text_with_style,
    apply_shape_to_image, paste_with_shadow, load_font
)


def compose_template(
    final_size, 
    fondo_img, 
    slots_imgs, 
    emojis_imgs_or_texts, 
    title_text,
    logo_img,
    font_family='arial_bold',
    title_style='simple',
    image_shape='rounded',
    logo_size=0.2,
    logo_x=0.5,
    logo_y=0.5,
    emoji_size=0.45,
    emoji_x_offset=0,
    emoji_y_offset=0,
    num_slots=3
):
    """
    Genera la plantilla completa con layout adaptativo
    
    Args:
        final_size: Tupla (ancho, alto) del tamaño final
        fondo_img: Imagen de fondo (PIL Image o None)
        slots_imgs: Lista de imágenes para los slots
        emojis_imgs_or_texts: Lista de emojis (imágenes o texto)
        title_text: Texto del título
        logo_img: Imagen del logo (PIL Image o None)
        font_family: Familia de fuente ('arial_bold', 'impact', 'comic', 'times')
        title_style: Estilo del título ('simple', 'contorno', 'sombra_suave', 'impacto')
        image_shape: Forma de las imágenes ('square', 'rounded', 'circle')
        logo_size: Ancho máximo del logo como porcentaje del ancho total
        logo_x: Posición X del logo (0-1)
        logo_y: Posición Y del logo (0-1)
        emoji_size: Tamaño de los emojis como porcentaje del tamaño de la imagen
        emoji_x_offset: Desplazamiento X del emoji
        emoji_y_offset: Desplazamiento Y del emoji
    """
    W, H = final_size
    base = Image.new("RGBA", (W, H), DEFAULT_BG_COLOR)
    draw = ImageDraw.Draw(base)

    # 1. FONDO
    if fondo_img:
        base = apply_cover_background(base, fondo_img)

    # 2. TÍTULO
    if title_text.strip():
        font_title = load_font(font_family, size=int(H * 0.08), scale_factor=FONT_SCALING_FACTORS.get(font_family, 1.0))
        style = TITLE_STYLES.get(title_style, TITLE_STYLES['simple'])
        
        bbox = draw.textbbox((0, 0), title_text, font=font_title)
        text_width = bbox[2] - bbox[0]
        
        x_title = (W - text_width) // 2
        y_title = int(H * TITLE_POSITION['y'])
        
        draw_text_with_style(draw, title_text, (x_title, y_title), 
                           font_title, TITLE_COLOR, style, W, H)

    # 3. IMÁGENES Y EMOJIS
    n = num_slots
    if n == 0:
        return base.convert("RGB")
    
    layout = IMAGE_LAYOUTS.get(n, IMAGE_LAYOUTS[4])
    positions = layout['positions']
    
    font_emoji = load_font('arial_bold', size=int(H * 0.08 * emoji_size / 0.45), scale_factor=FONT_SCALING_FACTORS.get('arial_bold', 1.0))
    
    # Preparar todas las imágenes (reales o placeholders) y emojis
    prepared_images = []
    prepared_emojis = []

    for i in range(n):
        pos_config = positions[i]
        size_img = int(W * pos_config['size'])
        
        # Get actual image or create placeholder
        img_data = slots_imgs[i] if i < len(slots_imgs) and slots_imgs[i] is not None else None
        
        if img_data:
            processed_img = apply_shape_to_image(img_data, image_shape, size_img, radius=30)
            prepared_images.append((processed_img, pos_config))
        else:
            # Crear placeholder si no hay imagen
            placeholder = Image.new("RGBA", (size_img, size_img), (80, 80, 90, 255))
            draw_ph = ImageDraw.Draw(placeholder)
            fnt_ph = load_font('arial_bold', int(size_img * 0.4), scale_factor=FONT_SCALING_FACTORS.get('arial_bold', 1.0)) # Scaled to image size
            bbox_ph = draw_ph.textbbox((0, 0), "?", font=fnt_ph)
            tw_ph = bbox_ph[2] - bbox_ph[0]
            th_ph = bbox[3] - bbox_ph[1]
            draw_ph.text(((size_img - tw_ph)//2, (size_img - th_ph)//2), "?", 
                         fill=(200, 200, 200), font=fnt_ph)
            prepared_images.append((placeholder, pos_config))

        # Get actual emoji or use default
        emoji_data = emojis_imgs_or_texts[i] if i < len(emojis_imgs_or_texts) and emojis_imgs_or_texts[i] is not None else None
        
        prepared_emojis.append(emoji_data)


    # Primero, pegar todas las imágenes
    for i, (img, pos_config) in enumerate(prepared_images):
        x = int(W * pos_config['x']) - img.width // 2
        y = int(H * pos_config['y']) - img.height // 2
        paste_with_shadow(base, img, (x, y))

    # Segundo, pegar todos los emojis encima
    for i, emoji_data in enumerate(prepared_emojis):
        if not emoji_data:
            continue
            
        pos_config = positions[i]
        size_img = int(W * pos_config['size'])
        x_img = int(W * pos_config['x']) - size_img // 2
        y_img = int(H * pos_config['y']) - size_img // 2

        if isinstance(emoji_data, Image.Image):
            em = emoji_data.convert("RGBA")
            em_w = int(size_img * emoji_size)
            em = em.resize((em_w, em_w), Image.LANCZOS)
            
            emoji_x_final = x_img + int(emoji_x_offset)
            emoji_y_final = y_img + size_img - em.height + int(emoji_y_offset)
            
            base.paste(em, (emoji_x_final, emoji_y_final), em)
        
        elif str(emoji_data).strip():
            txt = str(emoji_data)
            bbox = draw.textbbox((0, 0), txt, font=font_emoji)
            th = bbox[3] - bbox[1]

            emoji_x_final = x_img + int(emoji_x_offset)
            emoji_y_final = y_img + size_img - th + int(emoji_y_offset)
            
            draw.text((emoji_x_final + 2, emoji_y_final + 2), txt, 
                     fill=(0, 0, 0, 180), font=font_emoji)
            draw.text((emoji_x_final, emoji_y_final), txt, 
                     fill=(255, 255, 255), font=font_emoji)

    # 4. LOGO (dinámico)
    if logo_img:
        lw, lh = logo_img.size
        max_w = int(W * logo_size)
        scale = min(1.0, max_w / lw)
        
        new_lw = int(lw * scale)
        new_lh = int(lh * scale)
        logo = logo_img.resize((new_lw, new_lh), Image.LANCZOS).convert("RGBA")
        
        x = int(W * logo_x) - new_lw // 2
        y = int(H * logo_y) - new_lh // 2
        
        base.paste(logo, (x, y), logo)
    
    return base.convert("RGB")