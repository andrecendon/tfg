
from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, Session, EvaluacionAvance, Fase, DatabaseSession
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
# Crear el Blueprint
evaluacionAvance_bp = Blueprint("evaluacionAvance", __name__, template_folder="aplicacion/templates")


Session = DatabaseSession()


#Numero de fases de cada evaluacion
FASE1 = 8
FASE2 = 12
FASE3 = 21
FASE4 = 27
#### PANTALLA principal de la primera evaluacion ###
@evaluacionAvance_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
   if 'evaluacion_id' in session and 'project_id' in session:
       evaluacion_id = session.get('evaluacion_id')
       avance = Session.query(EvaluacionAvance).filter(EvaluacionAvance.project_id == session.get('project_id') ).first()
       
   elif avance is None:
      
      todas_las_fases = Session.query(Fase).all()
                # Crear una evaluación nueva
      avance = EvaluacionAvance(
                    avance=False,
                    numero_fases=len(todas_las_fases),
                    fases=todas_las_fases,  # Asigna todas las fases directamente
                    project_id=session.get('project_id')
                )
      
      Session.add(avance)
      Session.commit()
      session['evaluacion_id'] = avance.id
   
   print( avance.id ," AVANCES ", avance.avance, avance.avance2, avance.avance3)
   print(avance)

   return render_template("funciones/EvaluacionAvance/evaluacionAvance.html", evaluacionAvance = avance , numero_fases=FASE1)


## Se puede recibir a traves de la flecha back, tiene que probarse pero 
@evaluacionAvance_bp.route('/guardar', methods=["POST", "GET"])
def save_evaluation():
   if 'evaluacion_id' in session:
       
          
       evaluacion_id = session.get('evaluacion_id')
       print("evaluacion_id: ", evaluacion_id)
       evaluacion = Session.query(EvaluacionAvance).filter(EvaluacionAvance.project_id == session.get('project_id')).first()
       comentario = request.form.get("comentarios", "")
       print(request.form)
       print("Evaluando ", evaluacion)
       if comentario and evaluacion:
            evaluacion.comentarios = comentario
       else:
           evaluacion.comentarios = None 
       
       if 'cualidades' in request.form:
            evaluacion.cualidades = request.form.get("cualidades", "")
       if 'debilidades' in request.form:
            evaluacion.debilidades = request.form.get("debilidades", "")
       if 'mejoras' in request.form:
            evaluacion.mejoras = request.form.get("mejoras", "")
       Session.commit()
       print("Evaluación actualizada: ", evaluacion.comentarios, evaluacion.cualidades, evaluacion.debilidades, evaluacion.mejoras)
      
       if 'avanceFase1' in request.form:
            evaluacion.avance = True
            Session.commit()
       elif 'numero_fases' in request.form and request.form['numero_fases'] == str(FASE1):
            evaluacion.avance = False
       
       
       #Actualizamos valores de los estados
       if evaluacion.fases:
         for v in evaluacion.fases:
            estado = request.form.get(f"estado_{v.id}")
            if estado: 
               v.estado = estado
               Session.commit()

      
             
          
   

   #Criterios finalización: 
   if  'numero_fases' in request.form and request.form['numero_fases'] == str(FASE4): 
        evaluacion.conclusiones = request.form.get("conclusiones", "")
        if 'finalizacion' in request.form:
             evaluacion.finalizacion = True
        else:
             evaluacion.finalizacion = False

   #Manejamos los avances y redirecciones
   if 'action' in request.form:
       action = request.form['action']
       print("Action: ", action)
       if action.startswith('save'):
         fase_num = action.split('_')[1]
         fase_num = int(fase_num)
         print("Fase num: ", fase_num)
         if fase_num>FASE1:
                  if fase_num==FASE2:
                     if 'avance2' in request.form:
                        evaluacion.avance2= True
                     else:
                           evaluacion.avance2 = False
                  if fase_num==FASE3:
                        if 'avance3' in request.form:
                              evaluacion.avance3 = True
                        else:
                              evaluacion.avance3 = False
         

         Session.commit()
       print( evaluacion.id, "Valores de avance: ", evaluacion.avance, evaluacion.avance2, evaluacion.avance3)
       if action.startswith('save'):
            if fase_num==FASE2:
               return redirect("/funciones/evaluacionAvance/Fase2")
            elif fase_num==FASE3:
                  return redirect("/funciones/evaluacionAvance/Fase3")
            elif fase_num==FASE4:
                 return redirect("/funciones/evaluacionAvance/Fase4")
            else:
                return redirect("/funciones/evaluacionAvance/")
            
       elif action == 'back':
           return redirect("/funciones/")
   return redirect("/funciones/")
      


#Ev Fase 2
@evaluacionAvance_bp.route('/Fase2', methods=["POST", "GET"])
@login_required
def fase2():
   
   if 'project_id' in session:
       project = Session.query(Project).filter(Project.id == session.get('project_id')).first()
       avance = Session.query(EvaluacionAvance).filter(EvaluacionAvance.project_id == project.id ).first()
       
   print( avance.id ," AVANCES ", avance.avance, avance.avance2, avance.avance3)
   print(avance)
  
   return render_template("funciones/EvaluacionAvance/evaluacionAvance2.html", evaluacionAvance = avance, numero_fases=FASE2, fase1=FASE1, fase2 = FASE2, fase3=FASE3, fase4=FASE4) 




#Ev Fase 3
@evaluacionAvance_bp.route('/Fase3', methods=["POST", "GET"])
@login_required
def fase3():
   if  'project_id' in session:
       project = Session.query(Project).filter(Project.id == session.get('project_id')).first()
       avance = Session.query(EvaluacionAvance).filter(EvaluacionAvance.project_id == project.id ).first()
       print(avance.fases)
       
  
   return render_template("funciones/EvaluacionAvance/evaluacionAvance2.html", evaluacionAvance = avance , numero_fases=FASE3, fase1=FASE1, fase2 = FASE2, fase3=FASE3, fase4=FASE4)

#Ev Fase 4
@evaluacionAvance_bp.route('/Fase4', methods=["POST", "GET"])
@login_required
def fase4():
   if  'project_id' in session:
       project = Session.query(Project).filter(Project.id == session.get('project_id')).first()
       avance = Session.query(EvaluacionAvance).filter(Project.id == project.id ).first()
       print(avance.fases)
       
  
   return render_template("funciones/EvaluacionAvance/evaluacionAvance2.html", evaluacionAvance = avance , numero_fases=FASE4, fase1=FASE1, fase2 = FASE2, fase3=FASE3, fase4=FASE4)