
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import Food,  Prototype, Project, User, Session
from flask_login import login_required
from chatbot.chatbot import ModeloIA
# Crear el Blueprint
composicionQuimica_bp = Blueprint("composicionQuimica", __name__, template_folder="templates")




####  Quitar alimento de tabla ####
@composicionQuimica_bp.route('/quitarAlimento', methods=["POST", "GET"])
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



@composicionQuimica_bp.route('/bucarAlimento', methods=["POST", "GET"])
@login_required
def buscarAlimento():
    termino = request.args.get('alimento', '')
    if termino:
        resultados = Food.buscar_alimentos(termino)

    return render_template("funciones/Fase1/composicionQuimica/añadirAlimento.html", resultados=resultados, termino=termino)

####  Añadir alimento de tabla ####
@composicionQuimica_bp.route('/añadirAlimento', methods=["POST", "GET"])
@login_required
def elementoAñadido():
    
    alimento = request.args.get('alimento', '')
    
    if alimento:
        resultados = Food.buscar_alimentos(alimento)

    else:  
        resultados = []
    return render_template("funciones/Fase1/añadirAlimento.html", resultados=resultados, termino=alimento)




#### PANTALLA principal ####
@composicionQuimica_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    #Tiene que acceder a la base de datos de prototipo
   

    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    if request.form.get('food_id'):
        food_id = request.form.get('food_id')
        food = Session.query(Food).filter(Food.id == food_id).first()
        project.añadirAlimento(food, Session)
    if project:
            foods = project.foods
            totales = {
                'protein': round(sum(food.protein for food in foods), 3),
                'carbs': round(sum(food.carbohydrates for food in foods), 3),
                'fat': round(sum(food.total_fat for food in foods), 3),
                'sugars': round(sum(food.sugars for food in foods), 3),
                'fiber': round(sum(food.fiber for food in foods), 3),
                'sodium': round(sum(food.sodium for food in foods), 3),
                'calcium': round(sum(food.calcium for food in foods), 3),
                'cholesterol': round(sum(food.cholesterol for food in foods), 3),
                'energy': round(sum(food.energy_kcal for food in foods), 3),
                'water': round(sum(food.water for food in foods), 3),
                'potassium': round(sum(food.potassium for food in foods), 3)
            }

    if 'username' in session:
        username = session['username']
        user = Session.query(User).filter(User.name == username).first()

    
    Session.commit()

    return render_template("funciones/Fase1/composicionQuimica.html", foods=foods, usuario=user, proyecto=project, totales = totales)



@composicionQuimica_bp.route('/añadirComida', methods=["POST", "GET"])
@login_required
def añadirComida():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    food_id = request.form.get('food_id')
    try:
        project.añadirAlimento(food_id, Session)
    except:
        print("Ya está incluido ese alimento")
    Session.commit()
   
    return redirect("/funciones/Fase1/composicionQuimica/")