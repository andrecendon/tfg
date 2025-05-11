
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
from google import genai
from google.genai import types
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

    #Generamos resumen
    comidas=""
    for p in project.foods:
       comidas+= "\t"+ p.food_description + "\n"
    resumen=""
    if project.name: 
        resumen+="Nombre: "+ project.name
     
    if project.description: 
        resumen+= "\n Decripción: " + project.description+ "\n Ingredientes: \n"+comidas

    if project.prototypes:

        for pro in project.prototypes:
            if pro.is_favourite==True: 
                if pro.name: 
                    resumen+="\n Prototipo Favorito: " + pro.name
                for i in pro.food_prototypes:
                    resumen+= "\t"+ i.food_description + "cantidad: "+ str(i.cantidad) + "\n"
    
    for p in project.prototypes:
        if p.is_favourite == True:
            return render_template("funciones/resumen.html", project = project, favorite_prototype=p)
            
    return render_template("funciones/resumen.html", project = project)

