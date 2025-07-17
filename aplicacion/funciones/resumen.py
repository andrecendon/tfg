
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Food, Prototype, Session
from aplicacion.chatbot.chatbot import ModeloIA, Suplemento
import time
import base64
from io import BytesIO
import pathlib
import textwrap

from IPython.display import display
from IPython.display import Markdown

from flask_login import login_required, current_user

resumen_bp = Blueprint("resumen", __name__, template_folder="aplicacion/templates", url_prefix="/resumen")
# Crear el Blueprint




#Le hacen POST desde html
@resumen_bp.route('/', methods=["POST", "GET"])
@login_required
def a():
    projectID = request.args.get('id')
    if(projectID): 
        session['project_id'] = projectID
    project = Session.query(Project).filter(Project.id == session['project_id']).first()

    favorite_prototype = None

    for proto in project.prototypes:
        if proto.is_favourite:
            favorite_prototype = proto
            break
    
    conclusionesIA, tiempo = ModeloIA(prompt="Quiero que me saques unas conclusiones de este proyecto, teniendo en cuenta los prototipos y los alimentos que contiene. No me digas nada más, solo las conclusiones. Devuelve un formato de texto plano ya que no se va a estructurar ni dar estilo. El proyecto es el siguiente: "+ project.resumen())
    return render_template("funciones/resumen.html", project = project, favorite_prototype= favorite_prototype, conclusiones_IA = conclusionesIA)

