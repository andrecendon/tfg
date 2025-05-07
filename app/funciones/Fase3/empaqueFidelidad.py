
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from chatbot.chatbot import ModeloIA

# Crear el Blueprint
empaqueFidelidad_bp = Blueprint("empaqueFidelidad", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@empaqueFidelidad_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    
   
    
    return render_template("funciones/Fase3/empaqueFidelidad.html", proyecto=project)

