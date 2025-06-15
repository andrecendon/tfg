
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, SimulacionProduccion, EtapaProduccion
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA, simulacionProduccion_IA
import json
from pydantic import TypeAdapter

# Crear el Blueprint
simulacionProduccion_bp = Blueprint("simulacionProduccion", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@simulacionProduccion_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
        if project.simulacion_produccion is None:
            project.simulacion_produccion = SimulacionProduccion(project=project)
            Session.add(project.simulacion_produccion)
            Session.commit()
    
    ingredientes = ""
    for f in project.foods:
        ingredientes += f"{f.food_description}/ "

    prompt_flujo = "Realizar un diagrama de flujo para la producción de un alimento tipo [  ], el cual tiene como ingredientes: " + ingredientes 
    prompt_tabla = "A partir de este diagrama de flujo realiza una tabla que contenga : Cada etapa del proceso ; posibles equipos requeridos , proveedor en el país [ ] link de la empresa, costo estimado."
    prompt_imagen = "A partir del diagrama de flujo y de la tabla realizar una imagen de la línea de producción de [ ] teniendo en cuenta [ ]. "

    print("Etapas", project.simulacion_produccion)
    if project.simulacion_produccion.etapas:
        for etapa in project.simulacion_produccion.etapas:
            print("Etapa: ", etapa.numero_etapa, etapa.nombre, etapa.descripcion)
    return render_template("funciones/Fase3/simulacionProduccion.html", project=project, prompt_tabla=prompt_tabla, prompt_imagen=prompt_imagen)


@simulacionProduccion_bp.route('añadirEtapa/', methods=["POST", "GET"])
@login_required
def etapa():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")

    numero_etapa = request.form.get("numero_etapa")
    nombre_etapa = request.form.get("nombre_etapa")
    descripcion_etapa = request.form.get("descripcion_etapa")
    print("Datos recibidos: ", numero_etapa, nombre_etapa, descripcion_etapa)

    if nombre_etapa and descripcion_etapa and numero_etapa:
        
            if project.simulacion_produccion is None:
                project.simulacion_produccion = SimulacionProduccion(project=project)
                Session.add(project.simulacion_produccion)
                Session.commit()
            if project.simulacion_produccion.etapas is None:
                for etapa in project.simulacion_produccion.etapas:
                    if etapa.numero_etapa == numero_etapa:
                        print("Ya existe una etapa con este número: ", numero_etapa)
                        return redirect(url_for('simulacionProduccion.inicio'))
            etapa = EtapaProduccion(numero_etapa=numero_etapa, nombre=nombre_etapa, descripcion=descripcion_etapa, simulacion = project.simulacion_produccion)
            Session.add(etapa)
            Session.commit()
            

    return redirect(url_for('simulacionProduccion.inicio'))


@simulacionProduccion_bp.route('eliminarEtapa/', methods=["POST", "GET"])
@login_required
def eliminar():
    
    if 'etapa_id' in request.form:
        etapa_id = request.form.get('etapa_id')
        etapa = Session.query(EtapaProduccion).filter(EtapaProduccion.id == etapa_id).first()
        if etapa:
            Session.delete(etapa)
            Session.commit()
            print("Etapa eliminada: ", etapa_id)
        else:
            print("No se encontró la etapa con ID: ", etapa_id)

    return redirect(url_for('simulacionProduccion.inicio'))

@simulacionProduccion_bp.route('/generarTablaIA', methods=["POST", "GET"])
@login_required
def chat():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
        if project.simulacion_produccion is None:
            project.simulacion_produccion = SimulacionProduccion(project=project)
            Session.add(project.simulacion_produccion)
            Session.commit()
        
    
    
    #Generamos prompt para la tabla: 
    prompt_tabla = "Genera una tabla que contenga las siguientes columnas: Etapa del proceso, Posibles equipos requeridos, Proveedor en España, Link de la empresa (que funcione), Costo estimado. A partir de las siguientes etapas: \n\n"
    for etapa in project.simulacion_produccion.etapas:
        prompt_tabla += f"Etapa {etapa.numero_etapa}: {etapa.nombre} - {etapa.descripcion}\n"

    config = {
            'response_mime_type': 'application/json',
            'response_schema': list[simulacionProduccion_IA],
    }

    response_tabla, tiempo = ModeloIA(prompt_tabla, config=config)

    json_obj = json.loads(response_tabla.text)

    adapter = TypeAdapter(list[simulacionProduccion_IA])
    lista_objetos = adapter.validate_python(json_obj)

    for item in lista_objetos:
        print(f"Etapa: {item.etapa}, Equipos: {item.equipo}, Proveedor: {item.proveedor}, Link: {item.enlace}, Costo: {item.costo}")
        #Recuperamos la etaa que tiene el mismo numero de etapa que el objeto
        etapa = Session.query(EtapaProduccion).filter(EtapaProduccion.numero_etapa == item.numero_etapa, EtapaProduccion.simulacion == project.simulacion_produccion).first()
        if etapa:
            etapa.equipos_requeridos = item.equipo
            etapa.proveedor = item.proveedor
            etapa.web_proveedor = item.enlace
            etapa.costo_estimado = item.costo
            Session.commit()
         

    
    return redirect("/funciones/Fase3/simulacionProduccion")


@simulacionProduccion_bp.route('/actualizar', methods=["POST", "GET"])
@login_required
def act():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    
    #Hay que actualizar todos las etapas.
    try:
        
        
        
        # Procesar las etapas recibidas y ver que tienen distintos números
        numeros = []
        i=0
        while f"etapas[{i}][id]" in request.form:
            
            id = request.form.get(f'etapas[{i}][id]')
            numero = int(request.form.get(f'etapas[{i}][numero]'))
            nombre = request.form.get(f'etapas[{i}][nombre]')
            descripcion = request.form.get(f'etapas[{i}][descripcion]')
            etapa = Session.query(EtapaProduccion).filter(EtapaProduccion.id == id, EtapaProduccion.simulacion == project.simulacion_produccion).first()
            if numero not in numeros:
                numeros.append(numero)
                if etapa:
                    etapa.numero_etapa = numero
                    etapa.nombre = nombre
                    etapa.descripcion = descripcion
                    print(f"Actualizando etapa: {etapa.numero_etapa} - {etapa.nombre} - {etapa.descripcion}")
                    numeros.append(numero)
            else: 
                i=-1
            
           
            i += 1

        if i>0:
            Session.commit()
        else:
            print("Hay números repetidos en las etapas.")
        
        
        return redirect(url_for('simulacionProduccion.inicio'))
    
    except:

        return redirect(url_for('simulacion_produccion', project_id=project_id))