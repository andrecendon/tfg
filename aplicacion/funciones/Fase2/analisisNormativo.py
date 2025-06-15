from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Food, Prototype, DatabaseSession
from aplicacion.chatbot.chatbot import ModeloIA, Normativa
import time
from flask_login import login_required



Session = DatabaseSession()

analisisNormativo_bp = Blueprint("analisisNormativo", __name__, template_folder="templates", url_prefix="/funciones/Fase2/analisisNormativo")

@analisisNormativo_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
        if not project.foods:
            return redirect(url_for("analisisNormativo.inicio"))
        alimentos = ", ".join([food.food_description for food in project.foods])
    prompt = "Realizar una búsqueda y tabla resumen de los requisitos normativos en País [España] para un alimento []. La tabla debe contener: requisitos de ingredientes y aditivos , requisitos de rotulado y etiquetado, requisitos de composición, requisitos microbiológicos, requisitos fisicoquímicos, requisitos para exportación, nombre de la norma, link. El alimento tiene los siguientes ingredientes: " + alimentos 
     
    return render_template("funciones/Fase2/analisisNormativo.html", prompt=prompt, project=project)


@analisisNormativo_bp.route('/enviar', methods=["POST", "GET"])
@login_required
def analisisNormativoEnv():
    reponse = None
    time = 0
    prompt = request.form["prompt"]
    config={
                'response_mime_type': 'application/json',
                'response_schema': list[Normativa],}
        

    response, tiempo = ModeloIA(prompt, config=config)
    respuesta: list[Normativa] = response.parsed

    for normativa in respuesta:
        print(f"Normativa: {normativa.nombre_norma}, Link: {normativa.link}")

    return render_template("funciones/Fase2/analisisNormativo.html", normativas=respuesta, time=tiempo)