from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Food, Prototype, DatabaseSession
from chatbot.chatbot import ModeloIA, MatrizSustentable
import time
from flask_login import login_required



Session = DatabaseSession()

#####  ESTUDIO DE MERCADO #####

matrizSustentable_bp = Blueprint("matrizSustentable", __name__, template_folder="templates", url_prefix="/funciones/Fase1/matrizSustentable")

@matrizSustentable_bp.route('/', methods=["POST", "GET"])
@login_required
def mercado():
    if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
    alimentos=""
    for f in project.foods:
        alimentos += f"{f.food_description}, "

    prompt = (f"Realizar una búsqueda de cada uno de los ingredientes {alimentos} para construir un tabla resumen con : nombre del alimento, nivel de sustentabilidad, análisis ciclo de vida, cadena de suministro, huella de carbono, impacto ambiental.")

    return render_template("funciones/Fase1/matrizSustentable.html", prompt=prompt)


@matrizSustentable_bp.route('/enviar', methods=["POST", "GET"])
@login_required
def matrizSustentableEnv():
    reponse = None
    time = 0
    if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
    if request.method == "POST":
        prompt = request.form.get("prompt")
             
       
    config={
                'response_mime_type': 'application/json',
                'response_schema': list[MatrizSustentable],}
        

    response, tiempo = ModeloIA(prompt, config=config)
    respuesta: list[MatrizSustentable] = response.parsed

    return render_template("funciones/Fase1/matrizSustentable.html", prompt=prompt,  alimentos=respuesta, time=tiempo)