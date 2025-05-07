
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from chatbot.chatbot import ModeloIA
# Crear el Blueprint
preciosIngredientes_bp = Blueprint("preciosIngredientes", __name__, template_folder="templates")


Session = DatabaseSession()


#### PANTALLA principal ####
@preciosIngredientes_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    #Tiene que acceder a la base de datos de prototipo
    
    
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    #verificar que cantidad es un float

    for f in project.prototypes:
        for pr in f.food_prototypes:
            pr.cantidad = float(pr.cantidad)
        f.peso_inicial = float(f.peso_inicial)
    
    
    
    return render_template("funciones/Fase3/preciosIngredientes.html", proyecto=project)




#### PANTALLA principal ####
@preciosIngredientes_bp.route('/actualizar', methods=["POST", "GET"])
@login_required
def actualizar():
    #Tiene que acceder a la base de datos de prototipo
    
    

    try:
        if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
        
        food_id = request.form.get('actualizar')


        if food_id:
            precio = float(request.form.get(f'precio_{food_id}'))
            if precio > 0: 
                food = Session.query(Food).filter(Food.id == food_id).first()
                food.setPrecio(float(precio))
                Session.commit()
                
    except Exception as e:
        print(f"Error actualizando el producto: {e}")
    
    return redirect("/funciones/Fase3/preciosIngredientes")