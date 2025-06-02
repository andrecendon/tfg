
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
# Crear el Blueprint
prototipoMedio_bp = Blueprint("prototipoMedio", __name__, template_folder="templates")


Session = DatabaseSession()






#### PANTALLA principal ####
@prototipoMedio_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    return render_template("funciones/Fase2/prototipoMedio.html", proyecto=project)



@prototipoMedio_bp.route('/favorito', methods=["POST", "GET"])
@login_required
def fav():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()

        if request.method == "POST" and 'favorito' in request.form:
            fav = request.form.get("favorito")
            prot = Session.query(Prototype).filter(Prototype.id == fav).first()
            print("Favorito cambiado a ")
            if prot:
                for p in project.prototypes:
                    if p.is_favourite == True:
                        p.is_favourite = False
                prot.is_favourite = True
                session['prototype_id'] = prot.id
                print("Favorito cambiado a True")
                Session.commit()
                return redirect(url_for("prototipoMedio.inicio"))
    
    return redirect('funciones/Fase2/prototipoMedio')