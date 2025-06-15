
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Costos, ValoresNutricionales
from collections import defaultdict
from flask_login import login_required

from aplicacion.chatbot.chatbot import ModeloIA
import json


# Crear el Blueprint
validacionNutricional_bp = Blueprint("validacionNutricional", __name__, template_folder="templates")


Session = DatabaseSession()


#### PANTALLA principal ####
@validacionNutricional_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
   
    #try:
        print("Validacion nutricional inicio")
        #Recuperamos el favorito 
        if 'prototype_id' in session or 'project_id' in session:
            prototype_id = session.get('prototype_id')
            prototype = Session.query(Prototype).filter(Prototype.id == prototype_id).first()
            if prototype is None:
                if 'project_id' in session:
                    project_id = session.get('project_id')
                    project = Session.query(Project).filter(Project.id == project_id).first()
                    if project is None:
                        return redirect('/funciones')
                    else:
                        for p in project.prototypes:
                            if p.is_favourite:
                                prototype = p
                                session['prototype_id'] = prototype.id
                                print("Prototype favorito recuperado: ", prototype)
                                break

            print("Prototype recuperado: ", prototype)
            if not prototype:
                return redirect('/funciones/Fase2/prototipoMedio/')
            
            if prototype.valores_nutricionales is None: 
                valores_nutricionales = ValoresNutricionales(prototype=prototype)

                print("Valores creados ", valores_nutricionales)
                Session.add(valores_nutricionales)
            
                Session.commit()
           
            prototype.valores_nutricionales.calcular_valores_nutricionales()
            
        
        return render_template("funciones/Fase3/validacionNutricional.html", prototipo=prototype, prompt="¿Que valoración de NutriScore le darías a este prototipo? ¿Que cambiarías para mejorar su valor nutricional?")
    
@validacionNutricional_bp.route('/consulta', methods=["POST", "GET"])
@login_required
def consultaIA():
   
    
        if 'prototype_id' in session:
            prototype_id = session.get('prototype_id')
            prototype = Session.query(Prototype).filter(Prototype.id == prototype_id).first()
            print("Prototype recuperado: ", prototype)
        
        if 'prompt' in request.form:
            prompt = request.form.get('prompt', '')
            print("Prompt recibido:", prompt)
            
            food_descriptions = ""
            for f in prototype.food_prototypes:
                food_descriptions += f"{f.food_description} ({f.cantidad}g), "
            
            proto = f"Prototype(name={prototype.name}, version={ prototype.version}, food_prototypes={food_descriptions})" 

            valores_nutricionales = (
                f". ValoresNutricionales(energia_kcal={prototype.valores_nutricionales.energia_kcal}, proteinas={prototype.valores_nutricionales.proteinas}, grasas_totales={prototype.valores_nutricionales.grasas_totales}, grasas_saturadas={prototype.valores_nutricionales.grasas_saturadas}, carbohidratos={prototype.valores_nutricionales.carbohidratos}, fibra={prototype.valores_nutricionales.fibra}, azucares={prototype.valores_nutricionales.azucares}, sodio={prototype.valores_nutricionales.sodio}, sal={prototype.valores_nutricionales.sal})"
            )
            p = prompt + ". Que la salida tenga el siguiente formato -> Valor NutriScore: A /n Comentarios: Breves comentarios. El prototipo es el siguiente: " + proto + valores_nutricionales
            print("Prompt para IA:", p)
            # Crear una instancia del modelo IA
            respuesta, tiempo = ModeloIA(prompt=p)

         
            
            
            
            print("Respuesta del modelo IA:", respuesta)
            
            # Guardar la respuesta en el prototipo
            if prototype.valores_nutricionales is None: 
                valores_nutricionales = ValoresNutricionales(prototype=prototype)
                Session.add(valores_nutricionales)
                Session.commit()
            else:
                prototype.valores_nutricionales.respuesta_ia = respuesta
                Session.commit()
        
        return render_template("funciones/Fase3/validacionNutricional.html", prototipo=prototype, prompt=prompt, respuestaIA=respuesta, tiempo=tiempo)



@validacionNutricional_bp.route('/validacionCostos', methods=["POST", "GET"])
@login_required
def validacionCostos():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    if project.costos is None: 
        c = Costos(project = project)
        Session.add(c)
        Session.commit()
        print(c)
    else:
        project.costos.asignar_ingredientes()

    print(project.costos)
    return render_template("funciones/Fase3/validacionCostos.html", project=project)


@validacionNutricional_bp.route('/validacionCostos/actualizar', methods=["POST", "GET"])
@login_required
def actualizar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    
    
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

    
    return redirect(url_for('validacionNutricional.validacionCostos', project_id=project.id))