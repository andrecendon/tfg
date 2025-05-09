from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import  Project, Session, DatabaseSession

from flask_login import login_required



Session = DatabaseSession()

formularios_bp = Blueprint("formularios", __name__, template_folder="templates")




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