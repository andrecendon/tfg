
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
import re

# Crear el Blueprint
analisisSensorial2_bp = Blueprint("analisisSensorial2", __name__, template_folder="templates")


Session = DatabaseSession()




def promedios(project):
    tests =Session.query(Test_Hedonico).filter(Project.id==project.id).all()
    promedios = {}
    num_muestras = {}

    #Recorrer los tests, si se encuentra en la lista calcular el promedio 
    for test in tests:
        if test.type == "hedonico":
            if test.muestra not in promedios:
                promedios[test.muestra] = test.puntuacion
                num_muestras[test.muestra] = 1
            else:
                promedios[test.muestra] += test.puntuacion
                num_muestras[test.muestra] += 1
    
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

#### PANTALLA principal #### Tests Hedonico
@analisisSensorial2_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    
    tests = Session.query(Test_Hedonico).filter(Project.id==project.id).all()
    
    if not tests:
        t = Test_Hedonico(
            project_id=project.id,
            nombre_evaluador = "Andre",
            atributo="Hedonico",
            muestra = "1",
            puntuacion =1, 
            )
        tests = [t]
        Session.add(t)
        Session.commit()
       
    
    promedios_finales = promedios(project)

    print("Tests sensoriales del proyecto:", tests)

    return render_template("funciones/Fase4/analisisSensorial2.html", project=project, tests = tests, numero_muestras=len(promedios_finales), promedios=promedios_finales) 




#Funcion que elimina, guarda y añade tests
@analisisSensorial2_bp.route('/actualizar', methods=["POST", "GET"])
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
            test = Session.query(Test_Hedonico).filter(Test_Hedonico.id == id).first()
            if test:
                Session.delete(test)
                Session.commit()
            else:   
                print("No se encontró el test con ID:", id)
        
        if 'añadir' in request.form:

                        test = Test_Hedonico(
                            project_id=project.id,
                            project=project,
                            nombre_evaluador = "Nombre", 
                            muestra = "1",
                            puntuacion = 1,
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
                test = Session.query(Test_Hedonico).filter(Test_Hedonico.id == int(test_id)).first()
                if not test:
                    print(f"No se encontró el test con ID: {test_id}")
                    i += 1
                    continue
                if request.form.get(f"{test_id}[comentarios]"): test.comentarios = request.form.get(f"{test_id}[comentarios]")
                if request.form.get(f"{test_id}[muestra]"): test.muestra = request.form.get(f"{test_id}[muestra]")
                if request.form.get(f"{test_id}[puntuacion]"): test.puntuacion = request.form.get(f"{test_id}[puntuacion]")
                if request.form.get(f"{test_id}[evaluador]"): test.nombre_evaluador = request.form.get(f"{test_id}[evaluador]")

                Session.commit()
                print(f"Test actualizado: {test_id} - {test.comentarios}, {test.muestra}, {test.puntuacion}, {test.nombre_evaluador}")

                #recuperamos el resto de valores
                i += 1
           

            # Guardar todos en la base de datos
           
    
    return redirect(url_for('analisisSensorial2.inicio'))


#Tercer analisis sensorial
@analisisSensorial2_bp.route('/aceptacion', methods=["POST", "GET"])
@login_required
def aceptacion():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    tests = Session.query(Test_Aceptacion).filter(Project.id==project.id).all()
    if not tests:
        t = Test_Aceptacion(
            project_id=project.id,
            nombre_evaluador = "1",
            agrado = "3",
            aceptacion = "3",
            compra = "2",
            apariencia = "3",
            textura = "3",
            )
        tests = [t]
        Session.add(t)
        Session.commit()
    

    return render_template("funciones/Fase4/analisisSensorialAceptacion.html", project=project, tests = tests) 



#Funcion que elimina, guarda y añade tests de Aceptacion
@analisisSensorial2_bp.route('/aceptacion/actualizar', methods=["POST", "GET"])
@login_required
def eliminar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")

        print(request.form)
        if 'eliminar' in request.form:
            print("eliminar")
            id = request.form.get("eliminar")
            test = Session.query(Test_Aceptacion).filter(Test_Aceptacion.id == id).first()
            if test:
                Session.delete(test)
                Session.commit()
            else:   
                print("No se encontró el test con ID:", id)
        
        if 'añadir' in request.form:

                        t = Test_Aceptacion(
                        project_id=project.id,
                        nombre_evaluador = "1",
                        agrado = "3",
                        sabor = "3",
                        compra = "2",
                        apariencia = "3",
                        textura = "3",
                        )
                        Session.add(t)
                        Session.commit()
                
        if 'guardar' in request.form:

            i=0
            print("Guardar tests")
            print("Datos recibidos:", request.form)
            while f'{i}[test_id]' in request.form:
                test_id = request.form.get(f"{i}[test_id]")
                test = Session.query(Test_Aceptacion).filter(Test_Aceptacion.id == int(test_id)).first()
                if not test:
                    print(f"No se encontró el test con ID: {test_id}")
                    i += 1
                    continue
                if request.form.get(f"{test_id}[comentarios]"): test.comentarios = request.form.get(f"{test_id}[comentarios]")
                if request.form.get(f"{test_id}[apariencia]"): test.apariencia = request.form.get(f"{test_id}[apariencia]")
                if request.form.get(f"{test_id}[agrado]"): test.agrado = request.form.get(f"{test_id}[agrado]")
                if request.form.get(f"{test_id}[evaluador]"): test.nombre_evaluador = request.form.get(f"{test_id}[evaluador]")
                if request.form.get(f"{test_id}[compra]"): test.compra = request.form.get(f"{test_id}[compra]")
                if request.form.get(f"{test_id}[sabor]"): test.sabor = request.form.get(f"{test_id}[sabor]")
                if request.form.get(f"{test_id}[textura]"): test.textura = request.form.get(f"{test_id}[textura]")

                Session.commit()
                print(f"Test actualizado: {test_id} - {test.comentarios}, {test.apariencia}, {test.agrado}, {test.nombre_evaluador}")

                #recuperamos el resto de valores
                i += 1
           

            # Guardar todos en la base de datos
           
    
    return redirect(url_for('analisisSensorial2.aceptacion'))









