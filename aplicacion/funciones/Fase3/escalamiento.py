
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, EquipoProduccion, SimulacionProduccion
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
# Crear el Blueprint
escalamiento_bp = Blueprint("escalamiento", __name__, template_folder="templates")


Session = DatabaseSession()


#### PANTALLA principal ####
@escalamiento_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    #Tiene que acceder a la base de datos de prototipo
    
    
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project.simulacion_produccion:
            project.simulacion_produccion = SimulacionProduccion(project=project)
            Session.add(project.simulacion_produccion)
            Session.commit()
    #verificar que cantidad es un float

    equipos_planta = []
    equipos_nuevos = []
    for equipo in project.simulacion_produccion.equipos_produccion:
        if equipo.esta_en_planta:
            equipos_planta.append(equipo)
        else:
            equipos_nuevos.append(equipo)

    print("Equipos en planta: ", equipos_planta)
    print("Equipos nuevos: ", equipos_nuevos)

    
    
    return render_template("funciones/Fase3/escalamiento.html", project=project, equipos_planta=equipos_planta, equipos_nuevos=equipos_nuevos)




#### PANTALLA principal ####
@escalamiento_bp.route('/añadir', methods=["POST", "GET"])
@login_required
def añadir():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project.simulacion_produccion:
            project.simulacion_produccion = SimulacionProduccion(project=project)
            Session.add(project.simulacion_produccion)
            Session.commit()
    
    try:
            # Obtener datos del formulario
            nombre = request.form['nombre_equipo']
            
            
            costo = float(request.form['costo'])
            
            observaciones = request.form.get('observaciones', ' ')  # Campo opcional
            
            print("Datos recibidos: ", request.form)
            print("Nombre: ", nombre, "Costo: ", costo, "Observaciones: ", observaciones)
           
            
            if float(costo) <= 0:
                
                return redirect('/funciones')
            
            # Crear nuevo equipo
            equipo = EquipoProduccion(
                simulacion=project.simulacion_produccion,
                nombre=nombre,
                costo=costo,
                observaciones=observaciones
            )
            print("Equipo creado: ", equipo.nombre, equipo.costo, equipo.observaciones)
            if 'viejo' in request.form:
                equipo.esta_en_planta = True
                ubicacion = request.form['ubicacion']
                requisitos = request.form['requisitos_uso']
                if ubicacion: equipo.ubicacion = ubicacion
                if requisitos:equipo.requisitos_uso = requisitos
                
            if 'nuevo' in request.form:
                equipo.esta_en_planta = False
                especificaciones = request.form['especificaciones']
                requisitos = request.form['requisitos_instalacion']
                dimensiones = request.form['dimensiones']
                if especificaciones: equipo.especificaciones = especificaciones
                if dimensiones: equipo.dimensiones = dimensiones
                if requisitos: equipo.requisitos_instalacion = requisitos

            Session.add(equipo)
            Session.commit()
    #Excep
    except Exception as e:
        print("Error al añadir el equipo de producción")
    

    return redirect("/funciones/Fase3/escalamiento")

#### PANTALLA principal ####
@escalamiento_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    #Tiene que acceder a la base de datos de prototipo
    
    if 'eliminar' in request.form:
        equipo_id = request.form.get('eliminar')
        equipo = Session.query(EquipoProduccion).filter(EquipoProduccion.id == equipo_id).first()
        if equipo:
            Session.delete(equipo)
            Session.commit()
            print("Equipo eliminado: ", equipo.nombre)
        else:
            print("Equipo no encontrado")
        
    return redirect("/funciones/Fase3/escalamiento")