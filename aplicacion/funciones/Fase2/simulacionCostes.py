
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
from flask import jsonify
# Crear el Blueprint
simulacionCostes_bp = Blueprint("simulacionCostes", __name__, template_folder="templates")


Session = DatabaseSession()


#### PANTALLA principal ####
@simulacionCostes_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    #Tiene que acceder a la base de datos de prototipo
    try:
        print(session)
        if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
        
        
        for p in project.prototypes:
            p.actualizar_peso()

        
        return render_template("funciones/Fase2/simulacionCostes.html", proyecto=project, project = project)
    except Exception as e:
        print("Error en la simulacion de costes: ", e)
        return redirect("/funciones")


# En tu archivo de Flask
@simulacionCostes_bp.route('/actualizar', methods=["POST", "GET"])
@login_required
def actualizar_peso_final():
    print("Actualizar peso final")
    data = request.get_json()
    prototipo_id = data.get('prototipo_id')
    peso_final = data.get('peso_final')

    # Aquí iría tu lógica de base de datos para actualizar el peso final
    # ejemplo ficticio:
    prototipo = Session.query(Prototype).get(prototipo_id)
    if prototipo:
        prototipo.peso_final = peso_final
        Session.commit()
        return jsonify({'success': True}), 200

    return jsonify({'success': False, 'error': 'Prototipo no encontrado'}), 404
