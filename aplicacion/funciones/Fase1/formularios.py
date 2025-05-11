from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import  Project, Session, DatabaseSession, Food

from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA


Session = DatabaseSession()

formularios_bp = Blueprint("formularios", __name__, template_folder="aplicacion/templates")




@formularios_bp.route('/IdeaInicial', methods=["POST", "GET"])
@login_required
def idea():
    if 'project_id' in session:
        project_id = session.get('project_id')
        p = Session.query(Project).filter(Project.id == project_id).first()
    return render_template("funciones/Fase1/IdeaInicial.html", project=p)


@formularios_bp.route('/IdeaInicial/guardar', methods=["POST", "GET"])
@login_required
def IdeaInicialguardar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    if request.form and project:
        if request.form["claves_iniciales"] != "":
            project.claves_iniciales = request.form["claves_iniciales"]
        if request.form["requisitos_iniciales"] != "":
            project.requisitos_iniciales = request.form["requisitos_iniciales"]
        if request.form["idea_inicial"] != "":
            project.idea_inicial = request.form["idea_inicial"]
        Session.commit()

        #Ahora vamos a llamar a la IA para que devuelva alimentos de acuerdo a la idea inicial
    foods_description = Session.query(Food).all()
    foods_list = [
            {"id": food.id, "food_description": food.food_description} 
            for food in foods_description
        ]
    print("MODELO IA para alimentos")
    respuesta_ia = ModeloIA(
            prompt=f"Filtra esta lista de alimentos manteniendo solo los que cumplan con: '{project.idea_inicial}'. Devuélvelos en el mismo formato. Los alimentos son los siguientes, en caso de que haya varios tipos selecciona solo uno, ej: flour potato, flour semolina, selecciona el más adecaudo para la receta, y en caso de duas selecciona menos ingredientes: {foods_list}",
            model="gemini-1.5-flash"
        )
    print(respuesta_ia)

    return render_template("funciones/funciones.html", project=project)







@formularios_bp.route('/empatizar', methods=["POST", "GET"])
@login_required
def empatizar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    return render_template("funciones/Fase1/empatizar.html", project=project)

@formularios_bp.route('/empatizar/guardar', methods=["POST", "GET"])
@login_required
def Empatizarguardar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    if request.form:
        if request.form["empatizar1"] != "":
            project.empatizar1 = request.form["empatizar1"]
            
        if request.form["empatizar2"] != "":
            project.empatizar2 = request.form["empatizar2"]
          
        Session.commit()

    return render_template("funciones/funciones.html", project=project)