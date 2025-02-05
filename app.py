from flask import Flask, render_template, request, send_file
import os
from cronica import generar_placa

app = Flask(__name__)

# Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Obtener el texto del formulario
        texto = request.form.get("texto")

        # Generar la placa
        output_file = "static/placa_generada.png"
        generar_placa(texto, fondo_path="static/fondo_placa.png", output_file=output_file)

        # Mostrar la imagen generada
        return render_template("index.html", imagen_generada=output_file)

    # Si es una solicitud GET, mostrar el formulario
    return render_template("index.html")

# Ruta para descargar la imagen
@app.route("/descargar")
def descargar():
    return send_file("static/placa_generada.png", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)