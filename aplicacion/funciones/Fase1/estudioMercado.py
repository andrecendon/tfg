from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Food, Prototype, DatabaseSession
from aplicacion.chatbot.chatbot import ModeloIA, Suplemento
import time
from flask_login import login_required



Session = DatabaseSession()

#####  ESTUDIO DE MERCADO #####

estudioMercado_bp = Blueprint("estudioMercado", __name__, template_folder="aplicacion/templates", url_prefix="/funciones/Fase1/estudioMercado")

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

        prompt = (f"Genera una tabla para hacer un estudio de mercado acerca de un alimento descrito como: {alimentos} y con las características: {caracteristicas}. La tabla debe incluir las siguientes columnas: Nombre, Características, Marca, Lugar de Comercialización, Precio Aproximado y Link (un solo link a una pagina real). Cada fila de la tabla debe representar un alimento/suplemento del mercado individual.")
     
       
        config={
                'response_mime_type': 'application/json',
                'response_schema': list[Suplemento],}
        

        respuesta, tiempo = ModeloIA(prompt, config=config)
        respuesta: list[Suplemento] = respuesta.parsed

        print("Respuesta:", respuesta)
        
        #respuesta: list[Suplemento] = response.parsed

    return render_template("funciones/Fase1/estudioMercado.html", suplementos=respuesta, time=tiempo)