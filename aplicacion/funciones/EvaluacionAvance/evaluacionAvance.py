
from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, Session, EvaluacionAvance, Fase, DatabaseSession
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
# Crear el Blueprint
evaluacionAvance_bp = Blueprint("evaluacionAvance", __name__, template_folder="aplicacion/templates")


Session = DatabaseSession()

#### PANTALLA principal de la primera evaluacion ###
@evaluacionAvance_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
   if 'evaluacion_id' in session and 'project_id' in session:
       evaluacion_id = session.get('evaluacion_id')
       avance = Session.query(EvaluacionAvance).filter(EvaluacionAvance.id == 1).first()
       print(avance.fases)
       
   else:
      #Creamos una nueva evaluacion
      avance = EvaluacionAvance(project_id = session.get('project_id'))
      Session.add(avance)
      Session.commit()
      session['evaluacion_id'] = avance.id
  
   return render_template("funciones/EvaluacionAvance/evaluacionAvance.html", evaluacionAvance = avance , numero_fases=8)


## Se puede recibir a traves de la flecha back, tiene que probarse pero 
@evaluacionAvance_bp.route('/guardar', methods=["POST", "GET"])
def save_evaluation():
   if 'evaluacion_id' in session:
       
          
       evaluacion_id = session.get('evaluacion_id')
       print("evaluacion_id: ", evaluacion_id)
       evaluacion = Session.query(EvaluacionAvance).filter(EvaluacionAvance.id == 1).first()
       comentario = request.form.get("comentarios", "")

       print("Evaluando ", evaluacion)
       if comentario and evaluacion:
            evaluacion.comentarios = comentario
       else:
           evaluacion.comentarios = None 
       if 'avance' in request.form:
            avance = request.form["avance"]
            if avance == 'true':
               evaluacion.avance = True
       else:
            evaluacion.avance = False

       if evaluacion.fases:
         for v in evaluacion.fases:
            estado = request.form.get(f"estado_{v.id}")
            if estado: 
               v.estado = estado
             
          
   Session.commit()

   if 'action' in request.form:
       action = request.form['action']
       print("Action: ", action)
       if action.startswith('save'):
            fase_num = action.split('_')[1]
            fase_num = int(fase_num)
            print("Fase num: ", fase_num)
            if fase_num>8:
                return redirect("/funciones/evaluacionAvance/Fase2")
            else:
               return redirect("/funciones/evaluacionAvance/")
               return redirect("/funciones/")
       elif action == 'back':
           return redirect("/funciones/")
   return redirect("/funciones/")
      


#Ev Fase 2
@evaluacionAvance_bp.route('/Fase2', methods=["POST", "GET"])
@login_required
def fase2():
   if 'project_id' in session:
       evaluacion_id = session.get('evaluacion_id')
       avance = Session.query(EvaluacionAvance).filter(EvaluacionAvance.id == 1).first()
       print(avance.fases)
       
   else:
      #Creamos una nueva evaluacion
      avance = EvaluacionAvance(project_id = session.get('project_id'))
      Session.add(avance)
      Session.commit()
      session['evaluacion_id'] = avance.id
  
   return render_template("funciones/EvaluacionAvance/evaluacionAvance2.html", evaluacionAvance = avance, numero_fases=22) 




#Ev Fase 3
@evaluacionAvance_bp.route('/Fase3', methods=["POST", "GET"])
@login_required
def fase3():
   if  'project_id' in session:
       evaluacion_id = session.get('evaluacion_id')
       avance = Session.query(EvaluacionAvance).filter(EvaluacionAvance.id == 1).first()
       print(avance.fases)
       
   else:
      #Creamos una nueva evaluacion
      avance = EvaluacionAvance(project_id = session.get('project_id'))
      Session.add(avance)
      Session.commit()
      session['evaluacion_id'] = avance.id
  
   return render_template("funciones/EvaluacionAvance/evaluacionAvance2.html", evaluacionAvance = avance , numero_fases=30)
