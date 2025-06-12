
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Food, Prototype, Session, EvaluacionAvance, Fase
from aplicacion.chatbot.chatbot import ModeloIA, Suplemento



from IPython.display import display
from IPython.display import Markdown

from flask_login import login_required, current_user

funciones_bp = Blueprint("funciones", __name__, template_folder="aplicacion/templates", url_prefix="/funciones")
# Crear el Blueprint




@funciones_bp.route('/', methods=["POST", "GET"])
@login_required
def a():
    print(session)
    
    projectID = request.form.get('id')
    print("Proyecto ", projectID)
    if(projectID): 
        session['project_id'] = projectID
        project = Session.query(Project).filter(Project.id == session['project_id']).first()
        print("abriendo ", project)
        
    else:
        if 'project_id' in session:
            project = Session.query(Project).filter(Project.id == session['project_id']).first()

            
        
    if len(project.evaluaciones_avances)==0:
                todas_las_fases = Session.query(Fase).all()
                # Crear una evaluación nueva
                ev = EvaluacionAvance(
                    avance=False,
                    numero_fases=len(todas_las_fases),
                    fases=todas_las_fases,  # Asigna todas las fases directamente
                    project_id=projectID 
                )
                # Añadir y guardar
                Session.add(ev)
                Session.commit()
                print("Evaluación creada: ", ev)
    else:
         
        ev = project.evaluaciones_avances[0]
        print("Evaluación recuperadaa: ", ev)
    
    

    return render_template("funciones/funciones.html", project=project, evaluacion_avance=ev)
    

@funciones_bp.route('/accion', methods=["POST", "GET"])
@login_required
def accion():
    projectID = request.args.get('id')
    if projectID: 
        session['project_id'] = projectID
        project = Session.query(Project).filter(Project.id == projectID).first()
        
    return render_template("funciones/funciones.html", project=project)
















