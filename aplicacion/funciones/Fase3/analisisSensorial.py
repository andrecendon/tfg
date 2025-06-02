
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
    numero_muestras = tests[0].numero_muestras if tests else 4
    promedios = {}

    # Convertir tests a formato serializable y calcular promedios
    for test in tests:
        resultados = test.resultados if isinstance(test.resultados, dict) else json.loads(test.resultados)
        for muestra, posicion in resultados.items():
            if muestra not in promedios:
                promedios[muestra] = []
            promedios[muestra].append(float(posicion))

        # Calcular promedios finales
        promedios_finales = {
            muestra: sum(valores)/len(valores) if valores else 0
            for muestra, valores in promedios.items()
        }
    
        return promedios_finales
    
    return None

#### PANTALLA principal ####
@analisisSensorial_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    
    tests = []
    numero = None
    atributo = None
    for p in project.tests_sensoriales:
        if p.type=="inicial":
            tests.append(p)
            numero = p.numero_muestras
            atributo = p.atributo
        # Si no hay tests y viene informado la cantidad de muestras, se crea un test por defecto
    
    promedios_finales = promedios(project)

    return render_template("funciones/Fase3/analisisSensorial.html", project=project, tests = tests, numero_muestras=numero, atributo= atributo, promedios=promedios_finales) 


@analisisSensorial_bp.route('/iniciar', methods=["POST", "GET"])
@login_required
def iniciar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    
    tests = []
    print("Tests sensoriales del proyecto:")
    numero = None
    atributo = None
    for p in project.tests_sensoriales:
        if p.type=="inicial":
            tests.append(p)
            p.numero_muestras = 4
            numero = p.numero_muestras
            atributo = p.atributo
        
    if not tests:
        numero = int(request.form.get('numero_muestras'))
        atributo = request.form.get('atributo')

        print("Número de muestras:", numero, "Atributo:", atributo)
        if numero:
            try:
                numero_muestras = int(numero)
                print("Número de muestras:", numero_muestras)
                resultados = {}
                if numero_muestras > 0:
                    for i in range(1, numero_muestras + 1):
                        resultados[i] = 1
                    test = Test_Sensorial_Inicial(
                        project_id=project.id,
                        atributo=atributo,
                        numero_muestras=int(numero_muestras),
                        resultados=resultados,
                        
                    )
                    Session.add(test)
                    Session.commit()
                    tests.append(test)
            except ValueError:
                print("Número de muestras no válido, se usará el valor por defecto de 4.")

    
    promedios_finales = promedios(project)

    return render_template("funciones/Fase3/analisisSensorial.html", project=project, tests = tests, numero_muestras=4, promedios=promedios_finales, atributo=atributo)



    






#Funcion que elimina, guarda y añade tests
@analisisSensorial_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()

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
            
            test = Session.query(Test_Sensorial_Inicial).filter(Project.id==project.id).first()
            if test:
                try:
                    
                    if int(test.numero_muestras) > 0:
                        test = Test_Sensorial_Inicial(
                            project_id=project.id,
                            atributo=test.atributo,
                            numero_muestras=int(test.numero_muestras),
                            resultados=test.resultados
                        )
                        Session.add(test)
                        Session.commit()
                except ValueError:
                    print("Número de muestras no válido, se usará el valor por defecto de 4.")
        #Actualizamos la lista de tests
        if 'guardar' in request.form:

            tests_final = []
            i = 0
            while f'tests[{i}][nombre_evaluador]' in request.form:
                nombre = request.form.get(f'tests[{i}][nombre_evaluador]')
                comentarios = request.form.get(f'tests[{i}][comentarios]', '')
                id = request.form.get(f'tests[{i}][id]', None)
                print("Nombre:", nombre, "Comentarios:", comentarios, "ID:", id)
                if id:
                    test = Session.query(Test_Sensorial_Inicial).filter(Test_Sensorial_Inicial.id == id).first()
                    print("Test recuperado:", test)
                    if not test:
                        print("No se encontró el test con ID:", id)
                        continue
                
                    print("Recuperando datos del test:", nombre, comentarios)
                    # Recolectamos muestras y posiciones en un dict
                    resultados = {}
                    print(request.form)
                    j = 1
                    print(f"Recuperando muestras para el test {i}")
                    print(request.form.get('tests[0][muestra1_codigo]'))
                    while request.form.get(f'tests[{i}][muestra{j}_codigo]'):
                        print(f"Recuperando muestra {j} para el test {i}")
                        muestra = request.form.get(f'tests[{i}][muestra{j}_codigo]')
                        posicion = request.form.get(f'tests[{i}][posicion{j}]')
                        print(f"Muestra {j}: {muestra}, Posición: {posicion}")
                        if muestra and posicion:
                            resultados[muestra] = int(posicion)
                        j += 1
                    test.nombre_evaluador = nombre
                    test.comentarios = comentarios
                    test.resultados = resultados
                    Session.commit()
                    print("Test actualizado:", test)
                
                
                i += 1

            # Guardar todos en la base de datos
           
    
    return redirect("/funciones/Fase3/analisisSensorial")




