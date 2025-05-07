
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import User,  Project, Food, Prototype, Session
from chatbot.chatbot import ModeloIA, Suplemento
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
funciones_bp = Blueprint("funciones", __name__, template_folder="templates", url_prefix="/funciones")
# Crear el Blueprint




@funciones_bp.route('/', methods=["POST", "GET"])
@login_required
def a():
    print(session)
    projectID = request.args.get('id')
    if(projectID): 
        session['project_id'] = projectID
        project = Session.query(Project).filter(Project.id == session['project_id']).first()
        return render_template("funciones/funciones.html", project=project)
    else:
        if session['project_id']:
            project = Session.query(Project).filter(Project.id == session['project_id']).first()
            return render_template("funciones/funciones.html", project=project)
        return redirect("/proyectos")

@funciones_bp.route('/accion', methods=["POST", "GET"])
@login_required
def accion():
    projectID = request.args.get('id')
    if projectID: 
        session['project_id'] = projectID
        project = Session.query(Project).filter(Project.id == projectID).first()
        
    return render_template("funciones/funciones.html", project=project)
















