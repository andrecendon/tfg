
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Costos
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
import json


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



@calculoGastos_bp.route('/validacionCostos', methods=["POST", "GET"])
@login_required
def validacionCostos():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    if project.costos is None: 
        c = Costos(project = project)
        Session.add(c)
        Session.commit()
        print(c)
    else:
        project.costos.asignar_ingredientes()

    print(project.costos)
    return render_template("funciones/Fase3/validacionCostos.html", project=project)


@calculoGastos_bp.route('/validacionCostos/actualizar', methods=["POST", "GET"])
@login_required
def actualizar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    
    try:
       
        
        print("Datos recibidos:", request.form)
        
        # Procesar ingredientes
        ingredientes = {}
        for key, value in request.form.items():
            if key.startswith('ingredientes['):
                parts = key.split('[')
                nombre = parts[1].split(']')[0]
                campo = parts[2].split(']')[0]
                
                if nombre not in ingredientes:
                    ingredientes[nombre] = {}
                
                ingredientes[nombre][campo] = value
        print("Ingredientes procesados:", ingredientes)
        # Procesar empaque
        empaque = {}
        for key, value in request.form.items():
            if key.startswith('empaque['):
                parts = key.split('[')
                nombre = parts[1].split(']')[0]
                campo = parts[2].split(']')[0]
                
                if nombre not in empaque:
                    empaque[nombre] = {}
                
                # Convertir a float los campos numéricos
                if campo in ['cantidad', 'costo']:
                    try:
                        empaque[nombre][campo] = float(value)
                    except ValueError:
                        empaque[nombre][campo] = 0.0
                else:
                    empaque[nombre][campo] = value
        
        # Procesar mano de obra
        mano_obra = {
            'descripcion': request.form.get('operario[descripcion]'),
            'cantidad': float(request.form.get('operario[cantidad]', 0)),
            'costo': float(request.form.get('operario[costo]', 0))
        }
        
        # Procesar costos indirectos
        electricidad = {
            'descripcion': request.form.get('electricidad[descripcion]'),
            'cantidad': float(request.form.get('electricidad[cantidad]', 0)),
            'costo': float(request.form.get('electricidad[costo]', 0))
        }
        
        agua = {
            'descripcion': request.form.get('agua[descripcion]'),
            'cantidad': float(request.form.get('agua[cantidad]', 0)),
            'costo': float(request.form.get('agua[costo]', 0))
        }
        
        depreciacion_equipos = {
            'descripcion': request.form.get('depreciacion_equipos[descripcion]'),
            'cantidad': float(request.form.get('depreciacion_equipos[cantidad]', 0)),
            'costo': float(request.form.get('depreciacion_equipos[costo]', 0))
        }
        
        # Procesar otros costos
        transporte = {
            'descripcion': request.form.get('transporte[descripcion]'),
            'cantidad': float(request.form.get('transporte[cantidad]', 0)),
            'costo': float(request.form.get('transporte[costo]', 0))
        }
        
        mermas = {
            'descripcion': request.form.get('mermas[descripcion]'),
            'cantidad': float(request.form.get('mermas[cantidad]', 0)),
            'costo': float(request.form.get('mermas[costo]', 0))
        }
        
        adicionales = {
            'descripcion': request.form.get('adicionales[descripcion]'),
            'cantidad': float(request.form.get('adicionales[cantidad]', 0)),
            'costo': float(request.form.get('adicionales[costo]', 0))
        }
        
        # Actualizar el objeto de costos
        project.costos.ingredientes = ingredientes
        project.costos.empaque = empaque
        project.costos.mano_obra = mano_obra
        project.costos.electricidad = electricidad
        project.costos.agua = agua
        project.costos.depreciacion_equipos = depreciacion_equipos
        project.costos.transporte = transporte
        project.costos.mermas = mermas
        project.costos.adicionales = adicionales

        Session.commit()
        print("Costos actualizados:", project.costos)

        if 'action' in request.form and request.form['action'] == 'back':
            return redirect('/funciones')
        

    except Exception as e:
         return redirect('/funciones')

    
    return redirect(url_for('calculoGastos.validacionCostos', project_id=project.id))