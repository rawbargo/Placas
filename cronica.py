from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import requests

# URL de la fuente Oswald en Google Fonts
GOOGLE_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald-Regular.ttf"
FONT_PATH = "static/Oswald-Regular.ttf"

def descargar_fuente():
    """Descarga la fuente si no existe en la carpeta 'static/'."""
    if not os.path.exists(FONT_PATH):
        try:
            print("🔽 Descargando la fuente Oswald desde Google Fonts...")
            response = requests.get(GOOGLE_FONT_URL)
            response.raise_for_status()
            
            # Guardar la fuente en la carpeta 'static/'
            os.makedirs("static", exist_ok=True)
            with open(FONT_PATH, "wb") as f:
                f.write(response.content)
            print("✅ Fuente descargada correctamente.")
        except requests.RequestException as e:
            print(f"⚠️ Error al descargar la fuente: {e}. Se usará una fuente del sistema.")
            return None  # Si falla, se usará una fuente alternativa del sistema
    return FONT_PATH

def generar_placa(texto, fondo_path="static/fondo_placa.png", output_file="static/placa_cronica.png"):
    # Cargar la imagen de fondo
    try:
        imagen = Image.open(fondo_path)
    except FileNotFoundError:
        print(f"⚠️ No se encontró la imagen de fondo: {fondo_path}")
        return

    # Configuración de la imagen
    ancho, alto = imagen.size
    color_texto = (255, 255, 255)  # Blanco
    color_sombra = (0, 0, 0)  # Negro para la sombra

    # Crear objeto para dibujar
    dibujar = ImageDraw.Draw(imagen)

    # Descarga la fuente si es necesario
    fuente_path = descargar_fuente()
    tamano_fuente = 80
    espaciado_lineas = 20

    # Ajustar el texto a varias líneas
    max_ancho = ancho - 100  # Margen de 50px a cada lado
    lineas = textwrap.wrap(texto, width=20)

    def calcular_tamano_texto(fuente):
        bbox_total = [dibujar.textbbox((0, 0), linea, font=fuente) for linea in lineas]
        text_alto_total = sum([bbox[3] - bbox[1] for bbox in bbox_total]) + (len(lineas) - 1) * espaciado_lineas
        text_ancho_max = max([bbox[2] - bbox[0] for bbox in bbox_total])
        return text_ancho_max, text_alto_total

    while True:
        try:
            if fuente_path:
                fuente = ImageFont.truetype(fuente_path, tamano_fuente)
            else:
                fuente = ImageFont.truetype("arial.ttf", tamano_fuente)  # Fuente del sistema si falla
        except IOError:
            print("⚠️ No se pudo cargar la fuente personalizada. Usando fuente predeterminada.")
            fuente = ImageFont.load_default()

        text_ancho_max, text_alto_total = calcular_tamano_texto(fuente)

        if text_ancho_max <= max_ancho and text_alto_total <= alto - 100:
            break

        tamano_fuente -= 5
        espaciado_lineas -= 2
        if tamano_fuente < 20:
            print("⚠️ El texto es demasiado largo para la imagen.")
            return

    # Dibujar texto
    y_actual = (alto - text_alto_total) // 2
    for linea in lineas:
        bbox = dibujar.textbbox((0, 0), linea, font=fuente)
        text_ancho = bbox[2] - bbox[0]
        x = (ancho - text_ancho) // 2
        dibujar.text((x + 2, y_actual + 2), linea, fill=color_sombra, font=fuente)
        dibujar.text((x, y_actual), linea, fill=color_texto, font=fuente)
        y_actual += bbox[3] - bbox[1] + espaciado_lineas

    # Guardar la imagen
    imagen.save(output_file)
    print(f"✅ Imagen guardada en {output_file}")

