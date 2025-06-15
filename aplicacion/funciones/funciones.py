
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Food, Prototype, Session, EvaluacionAvance, Fase
from aplicacion.chatbot.chatbot import ModeloIA, Suplemento



from IPython.display import display
from IPython.display import Markdown

from flask_login import login_required, current_user

funciones_bp = Blueprint("funciones", __name__, template_folder="aplicacion/templates", url_prefix="/funciones")
# Crear el Blueprint


#Fases de la evaluacion
fases_data = {
    "1. Idea inicial de proyecto": "0",
    "2. Empatizar con los usuarios": "0",
    "3. Base de datos composición química de alimentos": "0",
    "4. Estudio de mercado": "0",
    "5. Ingredientes sustentables (matriz)": "0",
    "6. Ideación": "0",
    "7. Diseño experimental": "0",
    "8. Prototipo 1 - Baja complejidad": "0",

    "9. Prototipo de mediana complejidad": "0",
    "10. Simulación de costos": "0",
    "11. Análisis de viabilidad normativa": "0",
    "12. Prototipo empaque": "0",

    "13. Prototipado según diseño experimental": "0",
    "14. Simulación de producción": "0",
    "15. Actualización de precios de ingredientes": "0",
    "16. Simulación cálculo gastos de agua y energía": "0",
    "17. Análisis sensorial 1 - Inicial": "0",
    "18. Validación de composición nutricional": "0",
    "19. Escalamiento": "0",
    "20. Validación de costos producción": "0",
    "21. Prototipo de empaque alta fidelidad": "0",

    "22. Medición parámetros de sustentabilidad inicial": "0",
    "23. Estudio de vida útil": "0",
    "24. Análisis sensorial 2 - Hedónico": "0",
    "25. Validación de empaques": "0",
    "26. Medición parámetros de sustentabilidad final": "0",
    "27. Análisis sensorial 3 - Aceptación": "0",
    
}

    

@funciones_bp.route('/', methods=["POST", "GET"])
@login_required
def a():
    print("COOKIES :" ,session)
    try: 
        projectID = request.form.get('id')
        
        print("Proyecto ", projectID)
        if(projectID): 
            session['project_id'] = projectID
            project = Session.query(Project).filter(Project.id == session['project_id']).first()
            print("abriendo ", project)
            
        else:
            if 'project_id' in session:
                project = Session.query(Project).filter(Project.id == session['project_id']).first()

                
            
        if not project.evaluacion_avance:
                    todas_las_fases = []
                    for i, (nombre, estado) in enumerate(fases_data.items(), start=1):
                        fase = Fase(nombre=nombre, numero_paso=i, estado=0)
                        todas_las_fases.append(fase)
                        Session.add(fase)
                        Session.commit()
                    
                    ev = EvaluacionAvance(
                        avance=False,
                        avance2=False,
                        avance3=False,
                        finalizacion=False,
                        numero_fases=len(todas_las_fases),
                        fases=todas_las_fases,  # Asigna todas las fases directamente
                        project_id=project.id
                    )
                    # Añadir y guardar
                    Session.add(ev)
                    Session.commit()
                    print("Ev creada")
                    
                    print("Evaluación creada: ", ev)
        else:
            
            ev = project.evaluacion_avance
            print("Evaluación recuperadaa: ", ev)
        
        

        return render_template("funciones/funciones.html", project=project, evaluacion_avance=ev)
    except:
         return "Vuelve a iniciar sesión"
    

@funciones_bp.route('/accion', methods=["POST", "GET"])
@login_required
def accion():
    projectID = request.args.get('id')
    if projectID: 
        session['project_id'] = projectID
        project = Session.query(Project).filter(Project.id == projectID).first()
        
    return render_template("funciones/funciones.html", project=project)
















