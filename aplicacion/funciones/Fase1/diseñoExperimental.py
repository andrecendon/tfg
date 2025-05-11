
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food, Prototype, Project, User, FoodPrototype, Session
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
from sqlalchemy.orm import scoped_session
# Crear el Blueprint
diseñoExperimental_bp = Blueprint("diseñoExperimental", __name__, template_folder="aplicacion/templates")




#Lo que va a hacer es crear 10(si son muchos alimentos) prototipos, con sus cantidades que los crea y luego redirige a prototipado
@diseñoExperimental_bp.route('/generarIA', methods=["POST", "GET"])
@login_required
def IA():

    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()

    config={
                'response_mime_type': 'application/json',
                "response_schema": {
                    "type": "array", 
                    "items": {
                        "type": "object",
                        "properties": {
                            "food_id": {"type": "integer"},
                            "cantidad": {"type": "number"},
                        },
                    },
                },
                }
    prompt = request.form.get('prompt')  # Esto busca en los datos del formulario POST    if prompt:
    alimentos="" 
    for food in project.foods:
        alimentos += f"{food.food_description}, food_id: {food.id}, "
    prompt += f"Los alimentos son {alimentos}. El food_id tiene que ser el mismo que la comida, solo tienes que añadirle la cantidad. "
    response, tiempo = ModeloIA(prompt, config=config)
    
    numero_alimentos = len(project.foods)
    j=0
    prototipos = []
    for i in range(0, len(response.parsed), numero_alimentos):
        grupo = response.parsed[i:i+numero_alimentos]
        
        # Crear un nuevo prototipo para cada grupo
        p = Prototype(project=project)
        Session.add(p)
        
        # Asignar cantidades a este prototipo
        for alimento in grupo:
            p.asignar_cantidad(food_id=alimento["food_id"], cantidad=alimento["cantidad"])
        
        prototipos.append(p)
        print(p)
         
    return redirect("/funciones/Fase1/prototipado") 



#### PANTALLA principal ####
@diseñoExperimental_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    #Tiene que acceder a la base de datos de prototipo
    

    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    n = len(project.prototypes)
    # Obtener lista de ingredientes con comillas
    ingredientes = ', '.join([f'"{food.food_description}, id: {food.id}"' for food in project.foods])

    # Crear el prompt
    prompt = (f"Realiza un diseño experimental con 10 posibles recetas, sumando en cada una 100gr en total, para hacer un alimento "
            f"que cubra las [necesidades nutricionales] y para [público objetivo].") 
       
    return render_template("funciones/Fase1/diseñoExperimental.html", proyecto=project, numero_prototipos=n, project = project, prompt= prompt)


def asignar_comidas(project, session):
    
    for proto in project.prototypes: 
        for f in project.foods:
                
                food_prototype = session.query(FoodPrototype).filter_by(food_id=f.id, prototype_id=proto.id).first()
               
                if not food_prototype:
                    food_prototype = FoodPrototype(food_id=f.id, prototype_id=proto.id, cantidad=0, food_description=f.food_description)
                    proto.foods.append(f)
                    session.add(food_prototype)
                    session.commit()
    session.commit()
    





@diseñoExperimental_bp.route('/guardar_gramos', methods=["POST", "GET"])
@login_required
def añadirComida():
    
    if request.method == "POST":
        datos = {}  # Diccionario para almacenar los datos
        
        if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
            
            
    
    p = request.form.get("prototipo")  # Identifica qué prototipo se está guardando
    gramos_por_alimento = {}

    # Obtiene la cantidad inicial de FoodPrototype
    prototipo = Prototype(project=project)
   

    Session.add(prototipo)
    Session.commit()  
    

    prototipo.asignar_foods_a_prototipo(Session)  # Asigna alimentos solo si no existen duplicados


    # Ahora sí, aseguramos que el prototipo pertenece al proyecto
    if not Session.object_session(prototipo):
        Session.add(prototipo)  # Evitamos que se pierda la relación con el proyecto

    project.prototypes.append(prototipo) 
    Session.commit()  # Guardamos nuevamente tras establecer la relación

    


    valores = []
    

    for key, value in request.form.items():
            if key.startswith(f"grams_{p}_"):
                valores.append(value) 
                

    j=0
    
    for f in project.foods:
        prototipo.asignar_cantidad(food_id=f.id, cantidad=valores[j])
        j+=1
         
    Session.add(prototipo)
    Session.commit()
          

    
        
    return redirect("/funciones/Fase1/diseñoExperimental")


