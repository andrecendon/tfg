
from flask import Blueprint, request, redirect, url_for, render_template, session
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Empaque
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from sqlalchemy.orm.attributes import flag_modified
import json
import os

# Crear el Blueprint
validacionEmpaque_bp = Blueprint("validacionEmpaque", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@validacionEmpaque_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
        
        empaque = Session.query(Empaque).filter(Empaque.project_id == project.id, Empaque.is_favourite==True).first()
        if not empaque:
            return redirect("/funciones/Fase2/empaque/")
        if empaque.chequeo is None or len(empaque.chequeo) == 0: 
            print("Creando nuevo")
            empaque.chequeo = [
                { "texto": "¿El envase final cumple con la normativa de contacto alimentario aplicable (UE, FDA, Mercosur)?", "check": False },
                { "texto": "¿La etiqueta incluye toda la información obligatoria: nombre, ingredientes, alérgenos, origen, lote, fecha de vencimiento?", "check": False },
                { "texto": "¿El etiquetado nutricional cumple con el formato legal requerido?", "check": False },
                { "texto": "¿El producto cuenta con los sellos regulatorios obligatorios (Nutri-Score, semáforo, orgánico, etc.) si aplica?", "check": False },
                { "texto": "¿El envase primario protege eficazmente el producto durante toda su vida útil?", "check": False },
                { "texto": "¿El sistema de cierre/apertura del envase ha sido validado por pruebas de usuario?", "check": False },
                { "texto": "¿El envase presenta buena resistencia al transporte y manipulación comercial?", "check": False },
                { "texto": "¿El material del envase permite reciclado o está alineado con requisitos de sostenibilidad ambiental?", "check": False },
                { "texto": "¿La etiqueta está correctamente adherida y es resistente a condiciones de transporte y refrigeración (si aplica)?", "check": False },
                { "texto": "¿La identidad visual está clara y cumple con las guías de marca (logo, colores, tipografía)?", "check": False },
                { "texto": "¿El envase y etiqueta permiten una lectura clara del contenido por parte del consumidor?", "check": False },
                { "texto": "¿El empaque secundario (cajas, bandejas, etc.) está diseñado para transporte seguro y eficiente?", "check": False },
                { "texto": "¿Se ha probado la estiba o disposición del producto para distribución mayorista?", "check": False },
                { "texto": "¿Las unidades de venta y distribución están claramente diferenciadas (unitario vs. caja)?", "check": False },
                { "texto": "¿Existen pruebas logísticas que aseguren que el producto llegará en buen estado al punto de venta?", "check": False },
                { "texto": "¿Se ha verificado que el producto cumple con toda la normativa local de comercialización?", "check": False },
                { "texto": "¿Se cuenta con ficha técnica del producto y del envase para distribución?", "check": False },
                { "texto": "¿Se ha definido el sistema de trazabilidad (códigos de lote, QR, etc.) para seguimiento en el mercado?", "check": False }
            ]

            Session.commit()


    print("HH ", empaque.chequeo)
    
    return render_template("funciones/Fase4/validacionEmpaque.html", project=project, empaque = empaque)



@validacionEmpaque_bp.route('/guardar', methods=["POST", "GET"])
@login_required
def guardar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    if request.method == "POST":

        i = 0
        for index, (key, value) in enumerate(request.form.items()):
                if key.startswith('pregunta_'):
                    form_number = key.split('_')[1]
                    for emp in project.empaques:
                        if emp.is_favourite:
                            empaque = emp
                            break
                   
                    if empaque:
                         #metemos en lista de booleanos todos los valores de las preguntas y lo guardamos en la base de datos
                         if value == 'si':
                            empaque.chequeo[i]['check'] = True
                            flag_modified(empaque, "chequeo")
                         elif value == 'no':
                            empaque.chequeo[i]['check'] = False
                            flag_modified(empaque, "chequeo")

                         i = i+1

    
          
    Session.commit()     
    if request.form.get('action') == 'save':
        return redirect('/funciones/Fase4/validacionEmpaque/')
        
    elif request.form.get('action') == 'back':
        return redirect('/funciones/')
              
    return redirect('/funciones/Fase4/validacionEmpaque/')
