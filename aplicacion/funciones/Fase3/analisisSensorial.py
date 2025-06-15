
from flask import Blueprint, request, redirect, url_for, render_template, session
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Test_Sensorial_Inicial, Test_Sensorial, Test_Hedonico, Test_Aceptacion
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import json
import os

# Crear el Blueprint
analisisSensorial_bp = Blueprint("analisisSensorial", __name__, template_folder="templates")


Session = DatabaseSession()


def promedios(project):
    tests =Session.query(Test_Sensorial_Inicial).filter(Project.id==project.id).all()
    promedios = {}
    num_muestras = {}

    #Recorrer los tests, si se encuentra en la lista calcular el promedio 
    for test in tests:
        if test.type == "inicial":
            if test.muestra not in promedios:
                promedios[test.muestra] = test.posicion
                num_muestras[test.muestra] = 1
            else:
                promedios[test.muestra] += test.posicion
                num_muestras[test.muestra] += 1
    print("Promedios:", promedios)
    print("Número de muestras:", num_muestras)
    # Calcular el promedio final
    promedios_finales = {}
    for muestra, total in promedios.items():
        if num_muestras[muestra] > 0:
            promedios_finales[muestra] = total / num_muestras[muestra]
        else:
            promedios_finales[muestra] = 0
    
    if promedios_finales:
        return promedios_finales
    
    return None


@analisisSensorial_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    
    tests = Session.query(Test_Sensorial_Inicial).filter(Project.id==project.id).all()
    
    
       
    if tests:
        promedios_finales = promedios(project)
    else: 
        promedios_finales = {}

    print("Tests sensoriales iniciales del proyecto:", tests)

    return render_template("funciones/Fase3/analisisSensorial.html", project=project, tests = tests, numero_muestras=len(promedios_finales), promedios=promedios_finales) 

#### PANTALLA principal ####



@analisisSensorial_bp.route('/iniciar', methods=["POST", "GET"])
@login_required
def iniciar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    tests = Session.query(Test_Sensorial_Inicial).filter(Project.id==project.id).all()
    if not tests:
        atributo = request.form.get("atributo", "Atributo")
        test = Test_Sensorial_Inicial(
            project_id=project.id,
            nombre_evaluador = "Nombre",
            atributo=atributo,
            muestra = "1",
            posicion = 1,
            comentarios = " ",
        )
        
        Session.add(test)
        Session.commit()
        
    else:
        atributo = request.form.get("atributo", tests[0].atributo)
        for test in tests:
            if test.atributo != atributo:
                test.atributo = atributo
                Session.commit()
    
    return redirect(url_for('analisisSensorial.inicio'))



@analisisSensorial_bp.route('/actualizar', methods=["POST", "GET"])
@login_required
def act():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")

        print(request.form)
        if 'eliminar' in request.form:
            print("eliminar")
            id = request.form.get("eliminar")
            test = Session.query(Test_Sensorial_Inicial).filter(Test_Sensorial_Inicial.id == id).first()
            if test:
                Session.delete(test)
                Session.commit()
            else:   
                print("No se encontró el test con ID:", id)
        
        if 'añadir' in request.form:
            atributo = request.form.get("atributo", "")
            if atributo:
                        test = Test_Sensorial_Inicial(
                            project_id=project.id,
                            project=project,
                            atributo = atributo,
                            nombre_evaluador = "Nombre", 
                            muestra = "1",
                            posicion = 1,
                            comentarios = "Comentarios",
                        )
                        Session.add(test)
                        Session.commit()
                
        if 'guardar' in request.form:

            i=0
            print("Guardar tests")
            print("Datos recibidos:", request.form)
            while f'{i}[test_id]' in request.form:
                test_id = request.form.get(f"{i}[test_id]")
                test = Session.query(Test_Sensorial_Inicial).filter(Test_Sensorial_Inicial.id == int(test_id)).first()
                if not test:
                    print(f"No se encontró el test con ID: {test_id}")
                    i += 1
                    continue
                if request.form.get(f"{test_id}[comentarios]"): test.comentarios = request.form.get(f"{test_id}[comentarios]")
                if request.form.get(f"{test_id}[muestra]"): test.muestra = request.form.get(f"{test_id}[muestra]")
                if request.form.get(f"{test_id}[posicion]"): test.posicion = request.form.get(f"{test_id}[posicion]")
                if request.form.get(f"{test_id}[evaluador]"): test.nombre_evaluador = request.form.get(f"{test_id}[evaluador]")

                Session.commit()
                print(f"Test actualizado: {test_id} - {test.comentarios}, {test.muestra}, {test.posicion}, {test.nombre_evaluador}")

                #recuperamos el resto de valores
                i += 1
           

            # Guardar todos en la base de datos
           
    
    return redirect(url_for('analisisSensorial.inicio'))
    




