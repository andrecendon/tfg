from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import  Project, Session, DatabaseSession, Food

from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA, Alimento_IA


Session = DatabaseSession()

formularios_bp = Blueprint("formularios", __name__, template_folder="aplicacion/templates")




@formularios_bp.route('/IdeaInicial', methods=["POST", "GET"])
@login_required
def idea():
    if 'project_id' in session:
        project_id = session.get('project_id')
        p = Session.query(Project).filter(Project.id == project_id).first()
    return render_template("funciones/Fase1/IdeaInicial.html", project=p)


@formularios_bp.route('/IdeaInicial/guardar', methods=["POST", "GET"])
@login_required
def IdeaInicialguardar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    if request.form and project:
        if request.form["claves_iniciales"] != "":
            project.claves_iniciales = request.form["claves_iniciales"]
        if request.form["requisitos_iniciales"] != "":
            project.requisitos_iniciales = request.form["requisitos_iniciales"]
        if request.form["idea_inicial"] != "":
            project.idea_inicial = request.form["idea_inicial"]
        Session.commit()

    return redirect(url_for('formularios.idea'))



@formularios_bp.route('/IdeaInicial/generarAlimentos', methods=["POST", "GET"])
@login_required
def generar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    if request.form and project:
        if request.form["claves_iniciales"] != "":
            project.claves_iniciales = request.form["claves_iniciales"]
        if request.form["requisitos_iniciales"] != "":
            project.requisitos_iniciales = request.form["requisitos_iniciales"]
        if request.form["idea_inicial"] != "":
            project.idea_inicial = request.form["idea_inicial"]
        Session.commit()

    foods_description = Session.query(Food).all()
    foods_list = [
            {"id": food.id, "nombre": food.food_description} 
            for food in foods_description
        ]
    
    config={
            'response_mime_type': 'application/json',
            'response_schema': list[Alimento_IA],}
        
    #Pedimos una receta inicial a la IA
    tiempo_total = 0
    receta, tiempo = ModeloIA("Dame una receta inicial para un producto alimenticio que cumpla con los siguientes requisitos: " + project.requisitos_iniciales + " y que tenga como idea inicial: " + project.idea_inicial)
    tiempo_total += tiempo

    prompt = f"Para la siguiente receta {receta} . Selecciona una cantidad máxima de 10 ingredientes y mejor ingredientes de menos que de mas, y que cada uno de ellos sea factible para la receta. Seleccionalos de esta lista devolviendo el id de cada ingrediente: {foods_list}. \n\n"
    alimentos_ia, tiempo = ModeloIA(prompt, config=config)
    alimentos_ia: list[Alimento_IA] = alimentos_ia.parsed
    tiempo_total += tiempo
    lista_alimentos = []
    
    for f in alimentos_ia:
        lista_alimentos.append(Session.query(Food).filter(Food.id == f.Id).first())

    
    return  render_template("funciones/Fase1/IdeaInicial.html", project=project,  lista_alimentos = lista_alimentos, tiempo = tiempo_total)


@formularios_bp.route('/IdeaInicial/guardarAlimentos', methods=["POST", "GET"])
@login_required
def guardarAlimentos():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    

    #Recuperamos los alimentos y los metemos en el proyecto. Luego dirigmos a la pantallal de ingredientes. 
    i=0
    while f"alimentos{i}" in request.form:
        food_id = request.form[f"alimentos{i}"]
        print("Alimento seleccionado:", food_id)
        if food_id != "":
            food = Session.query(Food).filter(Food.id == food_id).first()
            project.añadirAlimento(food_id, Session)

        i += 1
    Session.commit()

    
    return  redirect('/funciones/Fase1/composicionQuimica/')

@formularios_bp.route('/empatizar', methods=["POST", "GET"])
@login_required
def empatizar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    return render_template("funciones/Fase1/empatizar.html", project=project)

@formularios_bp.route('/empatizar/guardar', methods=["POST", "GET"])
@login_required
def Empatizarguardar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    if request.form:
        if request.form["empatizar1"] != "":
            project.empatizar1 = request.form["empatizar1"]
            
        if request.form["empatizar2"] != "":
            project.empatizar2 = request.form["empatizar2"]
          
        Session.commit()

    return render_template("funciones/funciones.html", project=project)


@formularios_bp.route('/ideacion', methods=["POST", "GET"])
@login_required
def ideacion():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    if request.form:
        if request.form["empatizar1"] != "":
            project.empatizar1 = request.form["empatizar1"]
            
        if request.form["empatizar2"] != "":
            project.empatizar2 = request.form["empatizar2"]
          
        Session.commit()

    return render_template("funciones/Fase1/ideacion.html", project=project)