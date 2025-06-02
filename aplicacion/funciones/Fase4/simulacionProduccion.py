
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, SimulacionProduccion
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA, simulacionProduccion_IA
import json

# Crear el Blueprint
simulacionProduccion_bp = Blueprint("simulacionProduccion", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@simulacionProduccion_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    ingredientes = ""
    for f in project.foods:
        ingredientes += f"{f.food_description}/ "

    prompt_flujo = "Realizar un diagrama de flujo para la producción de un alimento tipo [  ], el cual tiene como ingredientes: " + ingredientes 
    prompt_tabla = "A partir del diagrama de flujo realiza una tabla que contenga : Cada etapa del proceso ; posibles equipos requeridos , proveedor en el país [ ] link de la empresa, costo estimado."
    prompt_imagen = "A partir del diagrama de flujo y de la tabla realizar una imagen de la línea de producción de [ ] teniendo en cuenta [ ]. "

    return render_template("funciones/Fase3/simulacionProduccion.html", project=project, prompt_flujo=prompt_flujo, prompt_tabla=prompt_tabla, prompt_imagen=prompt_imagen)


@simulacionProduccion_bp.route('/chatbot', methods=["POST", "GET"])
@login_required
def chat():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if project.simulacion_produccion is None:
            project.simulacion_produccion = SimulacionProduccion()
            Session.commit()
        
    
    
    #Recibimos los diferentes prompts para el chatbot
    prompt_flujo = request.form.get("prompt_flujo")
    prompt_tabla = request.form.get("prompt_tabla")
    prompt_imagen = request.form.get("prompt_imagen")

    #Pipeline para el chatbot
    try: 
        response_tabla = None
        reponse_flujo = None
        response_imagen = None
        if 'flujo' in request.form:
            # 1. Generar el diagrama de flujo
            prompt = f"{prompt_flujo}\n\nPor favor genera un diagrama de flujo en formato Mermaid JS con este formato:\n Graph: \n    A[Inicio] --> B[Paso 1]\n    B --> C[Paso 2]```" + prompt_flujo
            reponse_flujo, tiempo= ModeloIA(prompt)
            print("Respuesta flujo: ", reponse_flujo)
            project.simulacion_produccion.diagrama_flujo = reponse_flujo
            Session.commit()
            
        
        if 'tabla' in request.form:
            config={
                        'response_mime_type': 'application/json',
                        'response_schema': list[simulacionProduccion_IA],}
                

            response_tabla, tiempo = ModeloIA(prompt_tabla, config=config)
           
            try:
                json_obj = json.loads(response_tabla.text)
                project.simulacion_produccion.tabla = json_obj
                Session.commit()
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")

            
            
           

        # 3. Generar la imagen
        #imagen = ModeloIA(prompt_imagen, project.foods, project_id, "imagen")

        
        return render_template("funciones/Fase3/simulacionProduccion.html", project=project, prompt_flujo=prompt_flujo, prompt_tabla=prompt_tabla, prompt_imagen=prompt_imagen, response_flujo=reponse_flujo)
    except Exception as e:
        print("Error en el chatbot: ", e)
        return redirect("/funciones/Fase3/simulacionProduccion")