"""
config.py
Configuración central del generador de plantillas
"""

# Tamaños
CANVAS_SIZE = (540, 540)        # Preview en GUI
FINAL_SIZE = (1080, 1080)       # Salida final
SLOT_MAX = 4

# Colores
DEFAULT_BG_COLOR = (18, 18, 24)
TITLE_COLOR = (255, 255, 255)
TITLE_SHADOW_COLOR = (0, 0, 0, 180)

# Nombres de archivo de fuentes a buscar en el sistema
FONT_FILENAMES = {
    'arial_bold': ['arialbd.ttf', 'Arial-Bold.ttf'],
    'impact': ['impact.ttf'],
    'comic': ['comicbd.ttf', 'Comic-Sans-MS-Bold.ttf'],
    'times': ['timesbd.ttf', 'Times-New-Roman-Bold.ttf'],
    'burbank': ['Burbank-Big-Condensed-Bold.ttf', 'Burbank.ttf'],
    'montserrat': ['Montserrat-Regular.ttf', 'Montserrat.ttf']
}

# Factores de escala para fuentes (ajuste fino para tamaños consistentes)
FONT_SCALING_FACTORS = {
    'arial_bold': 1.0,
    'impact': 1.0,
    'comic': 1.0,
    'times': 1.0,
    'burbank': 1.0,  # Burbank often appears larger, so scale down
    'montserrat': 1.0# Montserrat can also be a bit large
}

# Estilos de título disponibles
TITLE_STYLES = {
    'simple': {
        'outline': False,
        'shadow': True,
        'shadow_offset': 4,
        'shadow_blur': 0
    },
    'contorno': {
        'outline': True,
        'outline_width': 4,
        'outline_color': (0, 0, 0),
        'shadow': False
    },
    'sombra_suave': {
        'outline': False,
        'shadow': True,
        'shadow_offset': 6,
        'shadow_blur': 10
    },
    'impacto': {
        'outline': True,
        'outline_width': 6,
        'outline_color': (0, 0, 0),
        'shadow': True,
        'shadow_offset': 4,
        'shadow_blur': 0
    }
}

# Layouts para diferentes cantidades de imágenes
IMAGE_LAYOUTS = {
    2: {
        'positions': [
            {'x': 0.30, 'y': 0.45, 'size': 0.35},  # Izquierda
            {'x': 0.70, 'y': 0.45, 'size': 0.35},  # Derecha
        ]
    },
    3: {
        'positions': [
            {'x': 0.30, 'y': 0.35, 'size': 0.28},  # Arriba izquierda
            {'x': 0.70, 'y': 0.35, 'size': 0.28},  # Arriba derecha
            {'x': 0.50, 'y': 0.65, 'size': 0.28},  # Abajo centro
        ]
    },
    4: {
        'positions': [
            {'x': 0.28, 'y': 0.38, 'size': 0.25},  # Arriba izquierda
            {'x': 0.72, 'y': 0.38, 'size': 0.25},  # Arriba derecha
            {'x': 0.28, 'y': 0.68, 'size': 0.25},  # Abajo izquierda
            {'x': 0.72, 'y': 0.68, 'size': 0.25},  # Abajo derecha
        ]
    }
}

# Posiciones relativas (como % del tamaño total)
TITLE_POSITION = {'y': 0.08}