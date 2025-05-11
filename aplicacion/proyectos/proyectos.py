
from flask import Blueprint, request, redirect, url_for, render_template, session # type: ignore
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Session
from flask_login import login_required


# Crear el Blueprint
proyectos_bp = Blueprint("proyectos", __name__, template_folder="aplicacion/templates")

#No funciona sessiones compartidas o crear una funcion que haga todo o nada


#Index
@proyectos_bp.route('/', methods=["POST", "GET"])
@login_required
def proyectos():
    
    #Recuperamos de la session el usuario
    if 'username' in session:
        usuario_final = Session.query(User).filter(User.name == session['username']).first()
    else: 
        print("No hay session")
    
    return render_template("proyectos/proyectos.html", user=usuario_final)





@proyectos_bp.route('/crearProyecto', methods=["POST", "GET"])
@login_required
def crearProyecto():
    if request.form:
        if not all([request.form.get("nombre"), request.form.get("director")]):
            return render_template("proyectos/crearProyecto.html", error="Rellena todos los campos obligatorios")
        user_id = session['username']
        user = Session.query(User).filter(User.name == user_id).first()
        if  request.form.get("idea_inicial"):
            pro = Project(name=request.form["nombre"], user=user, responsable=request.form["director"] ,idea_inicial=request.form["idea_inicial"])
        else:
            pro = Project(name=request.form["nombre"], user=user, responsable=request.form["director"])
        Session.add(pro)
        Session.commit()
        return redirect('/proyectos')
    else: 
        return render_template("proyectos/crearProyecto.html", error="Rellena todos los campos obligatorios")