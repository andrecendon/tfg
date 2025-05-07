
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from chatbot.chatbot import ModeloIA


# Crear el Blueprint
calculoGastos_bp = Blueprint("calculoGastos", __name__, template_folder="templates")


Session = DatabaseSession()


#### PANTALLA principal ####
@calculoGastos_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    #Tiene que acceder a la base de datos de prototipo
    
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
  
    #Hacemos una matriz para meter los precios de los ingredientes

    matriz = []
    alimentos = project.foods
    prototipos = project.prototypes
    
    # Inicializar matriz con ceros
    matriz = [[0.0 for _ in prototipos] for _ in alimentos]

    totales = []

    for p in project.prototypes:
        total = 0.0
        for f in p.food_prototypes:
            total += f.cantidad * f.food.precio /100
        totales.append(total)

    print(totales)
    
    #Recorremos los alimentos y luego los prototipos
    
    
    
    return render_template("funciones/Fase3/calculoGastos.html", proyecto=project, project = project, totales = totales)
