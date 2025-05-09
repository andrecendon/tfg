from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Food, Prototype, DatabaseSession
from chatbot.chatbot import ModeloIA, Suplemento
import time
from flask_login import login_required



Session = DatabaseSession()

#####  ESTUDIO DE MERCADO #####

estudioMercado_bp = Blueprint("estudioMercado", __name__, template_folder="templates", url_prefix="/funciones/Fase1/estudioMercado")

@estudioMercado_bp.route('/', methods=["POST", "GET"])
@login_required
def mercado():
    return render_template("funciones/Fase1/estudioMercado.html")


@estudioMercado_bp.route('/enviar', methods=["POST", "GET"])
@login_required
def estudioMercadoEnv():
    reponse = None
    time = 0
    if request.form["caracteristicas"] and request.form["alimentos"]:
        alimentos = request.form["alimentos"]
        caracteristicas = request.form["caracteristicas"]

        prompt = (f"Realizar una búsqueda y tabla resumen de un alimento con la siguiente descripción:  {alimentos}, "
                  f"y con características como {caracteristicas}. "
                  "Primera columna nombre del alimento, Segunda características, "
                  "tercera columna marcas, cuarta lugar de comercialización, "
                  "quinta columna precio, sexta columna link.")
     
       
        config={
                'response_mime_type': 'application/json',
                'response_schema': list[Suplemento],}
        

        response, tiempo = ModeloIA(prompt, config=config)
        respuesta: list[Suplemento] = response.parsed

    return render_template("funciones/Fase1/estudioMercado.html", suplementos=respuesta, time=tiempo)