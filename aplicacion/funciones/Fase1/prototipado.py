
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from chatbot.chatbot import ModeloIA
# Crear el Blueprint
prototipado_bp = Blueprint("prototipado", __name__, template_folder="templates")


Session = DatabaseSession()

####  Quitar alimento de tabla ####
@prototipado_bp.route('/quitarAlimento', methods=["POST", "GET"])
@login_required
def quitarAlimento():
    
    food_id = request.args.get('food_id', '')
    food = Session.query(Food).filter(Food.id == food_id).first()
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    else: 
        print("No hay proyecto")
    if food_id and project:
        project.quitarAlimento(food, Session)
        Session.commit()
    else: 
        print("No hay alimento")
        
    
    return redirect("/funciones/Fase1/composicionQuimica/")



@prototipado_bp.route('/bucarAlimento', methods=["POST", "GET"])
@login_required
def buscarAlimento():
    termino = request.args.get('alimento', '')
    if termino:
        resultados = Food.buscar_alimentos(termino)

    return render_template("funciones/Fase1/composicionQuimica/añadirAlimento.html", resultados=resultados, termino=termino)


####  Añadir alimento de tabla ####
@prototipado_bp.route('/añadirAlimento', methods=["POST", "GET"])
@login_required
def elementoAñadido():
    
    alimento = request.args.get('alimento', '')
    
    if alimento:
        resultados = Food.buscar_alimentos(alimento)

    else:  
        resultados = []
    return render_template("funciones/Fase1/añadirAlimento.html", resultados=resultados, termino=alimento)


@prototipado_bp.route('/eliminar', methods=["POST"])
@login_required
def elim():
    
    prototipo_id = request.form.get('eliminado', '')  # Obtener el ID del formulario

    if not prototipo_id:
        return "Error: No se proporcionó un ID válido.", 400
    
    try:
        prototipo_id = int(prototipo_id)  # Convertir a entero
       

        # Buscar el prototipo por ID
        prototipo = Session.query(Prototype).filter_by(id=prototipo_id).first()
        Session.add(prototipo)
        print("Prototipo", prototipo)
        if prototipo:
            Session.delete(prototipo)  # Eliminar el prototipo
            #Session.commit()  # Guardar cambios
            print(f"Prototipo {prototipo_id} eliminado correctamente.")
        else:
            print(f"No se encontró el prototipo con ID {prototipo_id}")

    except ValueError:
        return "Error: ID no válido.", 400
    
    
    return redirect("/funciones/Fase1/prototipado/")
        
        
        
#Funciónn que se le pase food_id, protype id y recupere la cantidad
def cantidades(food_id,prototype_id):
    
    food_proto = Session.query(FoodPrototype).filter(FoodPrototype.prototype_id == prototype_id, FoodPrototype.food_id == food_id).first()
    if food_proto:
        return food_proto.cantidad
    return 0  


#### PANTALLA principal ####
@prototipado_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    #Tiene que acceder a la base de datos de prototipo
    
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    n = len(project.prototypes)
    #Recuperamos todos los FoodPrototype de este prototipo para pasrle al html 


    #El diccionario tiene como valores el id del alimento y el id del prototipo y como resultado la cantidad. 
    
    
    return render_template("funciones/Fase1/prototipado.html", proyecto=project, numero_prototipos=n, project = project)


def asignar_comidas(project):
    Session = DatabaseSession()
    for proto in project.prototypes: 
        for f in project.foods:
                
                food_prototype = Session.query(FoodPrototype).filter_by(food_id=f.id, prototype_id=proto.id).first()
                if not food_prototype:
                    food_prototype = FoodPrototype(food_id=f.id, prototype_id=proto.id, cantidad=0, food_description=f.food_description)
                    proto.foods.append(f)
                    Session.add(food_prototype)
    Session.commit()
    


@prototipado_bp.route('/guardar_gramos', methods=["POST", "GET"])
@login_required
def añadirComida(): 

    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    accion = request.form.get('accion')

    if accion.startswith('eliminar_'):
        # Eliminar prototipo
        prototipo_id = accion.split('_')[1]
        prototipo = Session.query(Prototype).filter(Prototype.id==prototipo_id).first()
        print(f"Eliminando prototipo {prototipo_id}", len(project.prototypes))
        Session.delete(prototipo)
        Session.commit()
        # Lógica para eliminar el prototipo
        print(f"Eliminando prototipo {prototipo_id}", len(project.prototypes))
        
    elif accion.startswith('actualizar_'):
        # Actualizar prototipo
        prototipo_id = accion.split('_')[1]
        # Recoger todos los datos del formulario
        prototipo = Session.query(Prototype).filter(Prototype.id==prototipo_id).first()
        
        #Actualizar el nombre del prototipo
        prototipo.name = request.form.get('prototipo_name_'+prototipo_id)
        #Falta que actualice el nombre bien
        for key, value in request.form.items():
            if key.startswith(f'grams_{prototipo_id}_'):
                food_id = key.split('_')[2]
                grams = value
                prototipo.asignar_cantidad(food_id=food_id, cantidad=grams)
        Session.commit()
        
    elif accion == 'crear':
        # Crear nuevo prototipo
        prototipo = Prototype(project=project, name=request.form.get('nombre_prototipo'))
        Session.add(prototipo)
        # Procesar los gramos para cada alimento en el nuevo prototipo
        for key, value in request.form.items():
            if key.startswith('nuevo_grams_'):
                food_id = key.split('_')[2]
                grams = value
                print(f"Nuevo prototipo - alimento {food_id}: {grams}g")
               
                prototipo.asignar_cantidad(food_id=food_id, cantidad=grams)

                


    

        
    return redirect("/funciones/Fase1/prototipado/")