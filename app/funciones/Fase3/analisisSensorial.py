
from flask import Blueprint, request, redirect, url_for, render_template, session
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Test_Sensorial_Inicial, Test_Sensorial, Test_Hedonico, Test_Aceptacion
from collections import defaultdict
from flask_login import login_required
from chatbot.chatbot import ModeloIA
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import json
import os

# Crear el Blueprint
analisisSensorial_bp = Blueprint("analisisSensorial", __name__, template_folder="templates")


Session = DatabaseSession()


def generar_grafico(): 
    # Obtener los datos de la base de datos
    if 'project_id' in session:
        tests = Session.query(Test_Sensorial_Inicial).filter(Test_Sensorial_Inicial.project_id == session.get('project_id')).all()
        
        datos_muestras = defaultdict(list)
    
        for test in tests:
            # Asumiendo que test.muestras es un diccionario {muestra: posición}
            for muestra, posicion in test.muestras.items():
                datos_muestras[muestra].append(posicion)
        
        # Calcular promedios y conteos
        resultados = []
        for muestra, posiciones in datos_muestras.items():
            resultados.append({
                'Muestra': muestra,
                'Posición Promedio': sum(posiciones) / len(posiciones),
                'Número de Evaluaciones': len(posiciones)
            })
        
        # Crear DataFrame y ordenar (menor posición = mejor)
        df = pd.DataFrame(resultados)
        df = df.sort_values('Posición Promedio', ascending=True)
        
        # Configurar el gráfico
        plt.figure(figsize=(12, 6))
        bars = plt.bar(df['Muestra'], df['Posición Promedio'], color='skyblue')
        
        # Añadir etiquetas y valores
        plt.title('Resultados Sensoriales - Promedio de Posiciones\n(Menor valor = mejor posición)')
        plt.xlabel('Muestras')
        plt.ylabel('Posición Promedio')
        plt.xticks(rotation=45)
        
        # Añadir los valores encima de las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
    
        # Añadir línea de referencia
        plt.axhline(y=1, color='red', linestyle='--', alpha=0.3)
        
        # Añadir leyenda informativa
        plt.text(0.02, 0.95, f'Total evaluadores: {len(tests)}', 
                transform=plt.gca().transAxes)
        
        # Ajustar layout y guardar
        plt.tight_layout()
            
        # Guardar el gráfico en un archivo
        ruta_base = os.path.abspath(os.path.join(os.getcwd(), '..'))  # sube dos carpetas
        ruta_destino = os.path.join(ruta_base, "app", "static", "graficos")  # carpeta de la imagen

        # Crear carpetas si no existen
        os.makedirs(ruta_destino, exist_ok=True)
        grafico_path = os.path.join(ruta_destino, "analisisSensorial.png")

        plt.savefig(grafico_path)
        print(f"Gráfico guardado en: {grafico_path}")
        return grafico_path
    return None



#### PANTALLA principal ####
@analisisSensorial_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    
    for p in project.prototypes:
        p.actualizar_peso()
    tests = []
    for p in project.tests_sensoriales:
        if p.type=="inicial":
            tests.append(p)
    #grafico = generar_grafico()
    return render_template("funciones/Fase3/analisisSensorial.html", project=project, tests = tests)


@analisisSensorial_bp.route('/formulario', methods=["POST", "GET"])
@login_required
def form():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
   
    
    return render_template("funciones/Fase3/formulario.html", project=project, test=None)



@analisisSensorial_bp.route('/editar', methods=["POST", "GET"])
@login_required
def editar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()

        if 'editar' in request.form:
            id = request.form.get("test_id")
            test = Session.query(Test_Sensorial_Inicial).filter(Test_Sensorial_Inicial.id == id).first()
            
            if test:
                evaluador = test.nombre_evaluador
                fecha = test.fecha
                atributo = test.atributo
                muestras_json = test.muestras
                comentarios = test.comentarios
                
                return render_template("funciones/Fase3/formulario.html", project=project, test=test)
    
    
    return render_template("funciones/Fase3/formulario.html", project=project)

@analisisSensorial_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()

        print(request.form)
        if 'eliminar' in request.form:
            print("eliminar")
            id = request.form.get("test_id")
            test = Session.query(Test_Sensorial_Inicial).filter(Test_Sensorial_Inicial.id == id).first()
            if test:
                Session.delete(test)
                Session.commit()
            else:   
                print("No se encontró el test con ID:", id)
            
    return redirect("/funciones/Fase3/analisisSensorial")


@analisisSensorial_bp.route('/guardarBasico', methods=['POST'])
@login_required
def guardar_ordenamiento():
    evaluador = request.form['evaluador']
    try:
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
    except ValueError:
            print("Error al convertir la fecha")
            fecha = None
    atributo = request.form['atributo']
    comentarios = request.form.get('comentarios')

    muestras_json = {}
    i = 0
    
    while True:
        codigo = request.form.get(f'muestra_{i}')
        orden = request.form.get(f'orden_{i}')
        
        # Si no hay código, terminar el bucle
        if not codigo:
            break
            
        # Solo agregar si ambos campos existen
        if codigo and orden:
            muestras_json[codigo] =int(orden)
        
        i += 1
    

    print({
        "evaluador": evaluador,
        "atributo": atributo,
        "muestras": muestras_json,
        "comentarios": comentarios
    })

    test = Test_Sensorial_Inicial(
        project_id=session.get('project_id'),
        nombre_evaluador=evaluador,
        atributo=atributo,
        fecha=fecha,
        muestras=muestras_json,
        comentarios=comentarios
    )
    Session.add(test)
    Session.commit()

    return redirect ("/funciones/Fase3/analisisSensorial")


