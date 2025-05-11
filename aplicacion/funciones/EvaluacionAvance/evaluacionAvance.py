
from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, Session, EvaluacionAvance
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
# Crear el Blueprint
evaluacionAvance_bp = Blueprint("evaluacionAvance", __name__, template_folder="aplicacion/templates")


#### PANTALLA principal ####
@evaluacionAvance_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
   if 'evaluacion_id' in session and 'project_id' in session:
       evaluacion_id = session.get('evaluacion_id')
       avance = Session.query(EvaluacionAvance).filter(EvaluacionAvance.id == evaluacion_id).first()
       
   else:
      #Creamos una nueva evaluacion
      avance = EvaluacionAvance(project_id = session.get('project_id'))
      Session.add(avance)
      Session.commit()
      session['evaluacion_id'] = avance.id
  
   return render_template("funciones/evaluacionAvance/evaluacionAvance.html", fases = avance.fases)
