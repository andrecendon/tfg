
from flask import Blueprint, request, redirect, url_for, render_template, session
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, ParametrosSustentables
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
chequeo_bp = Blueprint("chequeo", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@chequeo_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if project.parametros_sustentables is None: 
            # Si no existe, creamos una nueva instancia
            chequeo = ParametrosSustentables(project=project)
        if project.parametros_sustentables.chequeo is None: 
            print("Creando nuevo")
            project.parametros_sustentables.chequeo = [
                                { "texto": "¿Usamos agua de forma eficiente y controlada en la producción?", "check": False },
                                { "texto": "¿Tenemos prácticas activas para conservar el suelo o prevenir erosión?", "check": False },
                                { "texto": "¿Realizamos separación y gestión de residuos orgánicos e inorgánicos?", "check": False },
                                { "texto": "¿Hacemos compostaje o tratamiento de residuos sólidos?", "check": False },
                                { "texto": "¿Contamos con algún sistema de tratamiento de aguas residuales?", "check": False },
                                { "texto": "¿Registramos o medimos el consumo energético en el proceso?", "check": False },
                                { "texto": "¿Implementamos estrategias para reducir el consumo de energía?", "check": False },
                                { "texto": "¿Utilizamos materiales de empaque reciclables o biodegradables?", "check": False },
                                { "texto": "¿Protegemos o integramos fuentes de biodiversidad en el entorno de la planta?", "check": False },
                                { "texto": "¿Hemos evaluado nuestra huella hídrica o de carbono?", "check": False },
                                { "texto": "¿Registramos los costos de producción con regularidad?", "check": False },
                                { "texto": "¿Diversificamos nuestros productos o fuentes de ingreso?", "check": False },
                                { "texto": "¿Tenemos planificada una estrategia de mejora continua o inversión?", "check": False },
                                { "texto": "¿Realizamos control de inventarios y mermas productivas?", "check": False },
                                { "texto": "¿Conocemos el margen de ganancia de cada producto?", "check": False },
                                { "texto": "¿Hemos evaluado la rentabilidad económica de nuestro sistema productivo?", "check": False },
                                { "texto": "¿Ofrecemos algún valor agregado (procesamiento, diseño, presentación)?", "check": False },
                                { "texto": "¿Realizamos alianzas o compras con proveedores locales?", "check": False },
                                { "texto": "¿Contamos con una política clara de precios justos?", "check": False },
                                { "texto": "¿Tenemos indicadores financieros mínimos definidos (flujo, retorno)?", "check": False },
                                { "texto": "¿La empresa ofrece condiciones laborales seguras y dignas?", "check": False },
                                { "texto": "¿Incluimos a mujeres, jóvenes o adultos mayores en el equipo?", "check": False },
                                { "texto": "¿El equipo participa en decisiones operativas importantes?", "check": False },
                                { "texto": "¿Hemos capacitado a nuestro personal en sostenibilidad o buenas prácticas?", "check": False },
                                { "texto": "¿Hemos consultado o recibido retroalimentación de nuestros consumidores?", "check": False },
                                { "texto": "¿Producimos alimentos accesibles y relevantes para la comunidad donde operamos?", "check": False },
                                { "texto": "¿Contribuimos con alimentos saludables o culturalmente aceptados?", "check": False },
                                { "texto": "¿Hemos creado materiales educativos o de sensibilización ambiental?", "check": False },
                                { "texto": "¿Participamos en ferias, redes o actividades comunitarias?", "check": False },
                                { "texto": "¿Hemos mejorado prácticas tras la observación directa de nuestros usuarios finales?", "check": False }
                                ]
            

            Session.commit()

    print("HH ", project.parametros_sustentables.chequeo)
    
    return render_template("funciones/Fase4/chequeo.html", project=project)



@chequeo_bp.route('/guardar', methods=["POST", "GET"])
@login_required
def guardar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    if request.method == "POST":

        i = 0
        for index, (key, value) in enumerate(request.form.items()):
                if key.startswith('pregunta_'):
                    form_number = key.split('_')[1]
                    chequeo = project.parametros_sustentables
                    if chequeo:
                         #metemos en lista de booleanos todos los valores de las preguntas y lo guardamos en la base de datos
                         if value == 'si':
                            project.parametros_sustentables.chequeo[i]['check'] = True
                            flag_modified(project.parametros_sustentables, "chequeo")
                         elif value == 'no':
                            project.parametros_sustentables.chequeo[i]['check'] = False
                            flag_modified(project.parametros_sustentables, "chequeo")

                         i = i+1

    
          
    Session.commit()     
    if request.form.get('action') == 'save':
        return redirect('/funciones/Fase4/chequeo/')
        
    elif request.form.get('action') == 'back':
        return redirect('/funciones/')
              
    return redirect('/funciones/Fase4/chequeo/')
