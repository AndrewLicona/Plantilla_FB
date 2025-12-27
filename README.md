# 🎨 Generador de Plantillas de Reacciones PRO

Aplicación mejorada para crear plantillas personalizadas con layouts adaptativos, múltiples estilos y formas.

## 📁 Estructura del Proyecto

```
proyecto/
│
├── src/                 # Código fuente de la aplicación
│   ├── __init__.py      # Marca el directorio 'src' como un paquete Python
│   ├── main.py          # Interfaz gráfica principal (ejecutar este)
│   ├── config.py        # Configuración (tamaños, colores, layouts)
│   ├── utils.py         # Funciones de utilidad (fuentes, formas, sombras)
│   ├── composer.py      # Lógica de composición de plantillas
│   └── ui/              # Módulos de la interfaz de usuario
│       ├── __init__.py  # Marca 'ui' como un subpaquete
│       ├── batch_panel.py
│       ├── center_panel.py
│       ├── left_panel.py
│       └── right_panel.py
│
└── README.md            # Esta documentación
```

## 🚀 Instalación

```bash
# Instalar dependencias
pip install Pillow

# Opcional: para drag & drop
pip install tkinterdnd2
```

## ▶️ Ejecutar

Para ejecutar la aplicación, asegúrate de estar en el directorio raíz del proyecto y usa el siguiente comando:

```bash
python -m src.main
```

## ✨ Características Nuevas

### 🖼️ Layouts Adaptativos
- **2 imágenes**: Lado a lado, más grandes
- **3 imágenes**: 2 arriba, 1 abajo centrada
- **4 imágenes**: Formato cuadrado 2x2

### 🎨 Formas de Imágenes
- ⬜ Cuadradas
- ⬛ Redondeadas (esquinas suaves)
- ⭕ Circulares

### ✍️ Estilos de Título
- **Simple**: Texto con sombra básica
- **Contorno**: Borde negro grueso
- **Sombra Suave**: Sombra difuminada elegante
- **Impacto**: Contorno + sombra (máximo impacto visual)

### 🔤 Fuentes Disponibles
- Arial Bold (por defecto)
- Impact
- Comic Sans Bold
- Times New Roman Bold

### 📍 Logo Mejorado
- Ahora se coloca en el **centro** de la imagen
- Más pequeño y discreto (20% del ancho)
- Sombra sutil para destacar

## 🎯 Mejoras Implementadas

### ✅ Problemas Solucionados
- ✔️ Título ahora se renderiza correctamente
- ✔️ `textsize` reemplazado por `textbbox` (compatible con Pillow moderno)
- ✔️ Import de `simpledialog` agregado
- ✔️ Mejor manejo de errores
- ✔️ Nombres de archivo únicos para el procesamiento por lotes (usando marcas de tiempo para evitar sobrescritura).

### ✅ Mejoras Visuales
- ✔️ Imágenes sin círculo forzado (formas personalizables)
- ✔️ Layouts inteligentes según cantidad de imágenes
- ✔️ Logo centrado y más pequeño
- ✔️ Título con múltiples efectos profesionales

### ✅ Código Organizado
- ✔️ Separación en módulos lógicos
- ✔️ Configuración centralizada
- ✔️ Fácil de mantener y extender

## 🎮 Uso

1. **Añadir imágenes** (2-4) usando los botones o drag & drop
2. **Personalizar**:
   - Título con texto libre
   - Elegir fuente y estilo
   - Seleccionar forma de imágenes
   - Cargar fondo (opcional)
   - Cargar logo (opcional)
3. **Añadir emojis** debajo de cada imagen (opcional)
4. **Guardar** plantilla en alta resolución (1080x1080)

## 🔧 Personalización Avanzada

### Modificar Layouts
Edita `config.py` → `IMAGE_LAYOUTS` para cambiar posiciones y tamaños

### Añadir Fuentes
Edita `config.py` → `FONT_PATHS` con rutas a tus fuentes

### Crear Nuevos Estilos
Edita `config.py` → `TITLE_STYLES` para agregar efectos personalizados

### Cambiar Colores
Edita `config.py` → variables de color

## 🐛 Troubleshooting

### Error: "textsize not found"
- Asegúrate de usar la versión actualizada de los archivos
- Verifica que Pillow esté actualizado: `pip install --upgrade Pillow`

### Las fuentes no cargan
- El sistema usa fuentes por defecto si no encuentra las especificadas
- Puedes agregar rutas personalizadas en `config.py`

### Drag & Drop no funciona
- Instala: `pip install tkinterdnd2`
- En Linux puede requerir dependencias adicionales

## 📝 Notas

- Resolución final: **1080x1080** (ideal para redes sociales)
- Formatos soportados: PNG, JPG, JPEG, WEBP, BMP
- Las imágenes se redimensionan y centran automáticamente
- El logo siempre se coloca en el centro para no tapar las imágenes

## 🎨 Ejemplo de Uso

```python
# Para usar el compositor directamente en código:
from composer import compose_template
from PIL import Image

imgs = [
    Image.open("img1.jpg"),
    Image.open("img2.jpg"),
    Image.open("img3.jpg")
]

result = compose_template(
    final_size=(1080, 1080),
    fondo_img=Image.open("fondo.jpg"),
    slots_imgs=imgs,
    emojis_imgs_or_texts=["❤️", "🔥", "😂"],
    title_text="¡VOTA AHORA!",
    logo_img=Image.open("logo.png"),
    font_family="impact",
    title_style="impacto",
    image_shape="rounded"
)

result.save("resultado.png")
```

## 👨‍💻 Desarrollo

Para extender la aplicación:
1. Nuevas formas → `utils.py` → `apply_shape_to_image()`
2. Nuevos layouts → `config.py` → `IMAGE_LAYOUTS`
3. Nuevos efectos de texto → `utils.py` → `draw_text_with_style()`
4. Nueva GUI → `main.py` → clase `TemplateGeneratorApp`

---

**¡Disfruta creando plantillas increíbles!** 🎉