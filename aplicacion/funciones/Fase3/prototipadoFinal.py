
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA

# Crear el Blueprint
prototipoFinal_bp = Blueprint("prototipoFinal", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@prototipoFinal_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    
    for p in project.prototypes:
        p.actualizar_peso()
    
    return render_template("funciones/Fase3/prototipoFinal.html", proyecto=project)




@prototipoFinal_bp.route('/guardar', methods=["POST", "GET"])
@login_required
def guardar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    
    print(request.form)

    if 'observaciones' in request.form and 'prototipo_id' in request.form:
        proto = Session.query(Prototype).filter(Prototype.id == request.form.get("prototipo_id"), Prototype.project_id==project.id).first()
        print("Prototipo encontrado:", proto)
        if proto:
            proto.comentarios = request.form.get("observaciones", "")
            Session.commit()
            print(proto.comentarios)
        
    
    return redirect("/funciones/Fase3/prototipoFinal/")