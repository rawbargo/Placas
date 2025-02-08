import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

# URL de la fuente en Google Fonts (archivo TTF directo)
FONT_URL = "https://github.com/rawbargo/Placas/raw/refs/heads/main/static/estamesma.ttf"

# Generar la placa con la fuente en línea
def generar_placa(texto, fondo_path="static/fondo_placa.png", output_file="static/placa_cronica.png"):
    # Descargar la fuente en memoria (sin guardarla)
    try:
        response = requests.get(FONT_URL)
        response.raise_for_status()  # Verifica si hubo un error en la descarga
        fuente_ttf = io.BytesIO(response.content)  # Convierte la respuesta en un archivo en memoria
    except requests.RequestException as e:
        print(f"⚠️ Error al obtener la fuente: {e}")
        return

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

    # Tamaño de fuente inicial
    tamano_fuente = 80
    margen = 50  # Margen mínimo en los bordes
    espaciado_lineas = 20  # Espaciado inicial entre líneas

    # Ajustar el texto a varias líneas si es muy largo
    max_ancho = ancho - 2 * margen  # Margen a los lados
    lineas = textwrap.wrap(texto, width=20)  # Ajusta según la cantidad de palabras por línea

    # Función para calcular el tamaño del texto
    def calcular_tamano_texto(fuente):
        bbox_total = [dibujar.textbbox((0, 0), linea, font=fuente) for linea in lineas]
        text_alto_total = sum([bbox[3] - bbox[1] for bbox in bbox_total]) + (len(lineas) - 1) * espaciado_lineas
        text_ancho_max = max([bbox[2] - bbox[0] for bbox in bbox_total])
        return text_ancho_max, text_alto_total

    # Ajustar el tamaño de la fuente si el texto es demasiado grande
    while True:
        try:
            fuente = ImageFont.truetype(fuente_ttf, tamano_fuente)
        except IOError:
            print("⚠️ No se pudo cargar la fuente en línea.")
            return

        text_ancho_max, text_alto_total = calcular_tamano_texto(fuente)

        # Si el texto cabe en la imagen, salir del bucle
        if text_ancho_max <= max_ancho and text_alto_total <= alto - 2 * margen:
            break

        # Reducir el tamaño de la fuente y el espaciado entre líneas
        tamano_fuente -= 5
        espaciado_lineas -= 2

        # Tamaño mínimo de fuente
        if tamano_fuente < 20:
            print("⚠️ El texto es demasiado largo para la imagen.")
            return

    # Dibujar cada línea centrada con sombra
    y_actual = (alto - text_alto_total) // 2
    for i, linea in enumerate(lineas):
        bbox = dibujar.textbbox((0, 0), linea, font=fuente)
        text_ancho = bbox[2] - bbox[0]
        x = (ancho - text_ancho) // 2

        # Dibujar sombra (desplazada ligeramente)
        dibujar.text((x + 2, y_actual + 2), linea, fill=color_sombra, font=fuente)

        # Dibujar texto principal
        dibujar.text((x, y_actual), linea, fill=color_texto, font=fuente)

        # Ajustar posición para la siguiente línea
        y_actual += bbox[3] - bbox[1] + espaciado_lineas

    # Guardar la imagen
    imagen.save(output_file)
    print(f"✅ Imagen guardada en {output_file}")
