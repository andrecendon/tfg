
from flask import Blueprint, request, redirect, url_for, render_template, session # type: ignore
from sqlalchemy.orm import sessionmaker
from modelo.models import User,  Project, Session
from flask_login import login_required
import os

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
        return redirect('/login')
    
    print("Usuario final: ", usuario_final.projects)
    
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
    


def eliminar_carpetas(proyecto):
   
    if proyecto:
                empaque = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'empaques', proyecto.name)
                ficheros = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'ficheros', proyecto.name)
                
                
                
                if ficheros and os.path.exists(ficheros):
                        os.remove(ficheros)
                        print(f"[DEBUG] Carpeta eliminada: {ficheros}")
                if empaque and os.path.exists(empaque):
                        os.remove(empaque)
                        print(f"[DEBUG] Carpeta eliminada: {empaque}")
                

@proyectos_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    
    #Recuperamos de la session el usuario
    if 'username' in session:
        usuario_final = Session.query(User).filter(User.name == session['username']).first()
    else: 
        return redirect('/login')
    
    if request.form:
        project_id = request.form.get("eliminar")
        print("ID del proyecto a eliminar:", project_id)
        if project_id:
            project = Session.query(Project).filter(Project.id == project_id).first()
            if project:
                #Eliminarmos primero todas las carpetas que depende de este proyecto
                proto = project.prototypes
                Session.delete(project)
                Session.commit()

                if proto:
                     print("Eliminando prototipos asociados al proyecto")
                else:
                     print("Joder")
                print("Proyecto eliminado correctamente")
                return redirect('/proyectos')
        
        
            
    
    return render_template("proyectos/proyectos.html", user=usuario_final)


def cambiar_nombre_carpetas(proyecto, nuevo_nombre):
    print(f"[DEBUG] Cambiando nombre de carpetas para el proyecto: {proyecto.name} a {nuevo_nombre}")
    if proyecto:
        empaque = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'aplicacion', 'static', 'empaques', proyecto.name)
        ficheros = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'aplicacion', 'static', 'ficheros', proyecto.name)
        
        nuevo_empaque = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'aplicacion', 'static', 'empaques', nuevo_nombre)
        nuevo_ficheros = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'aplicacion', 'static', 'ficheros', nuevo_nombre)
        
        if os.path.exists(empaque):
            os.rename(empaque, nuevo_empaque)
            print(f"[DEBUG] Carpeta renombrada de {empaque} a {nuevo_empaque}")
        if os.path.exists(ficheros):
            os.rename(ficheros, nuevo_ficheros)
            print(f"[DEBUG] Carpeta renombrada de {ficheros} a {nuevo_ficheros}")
        #Si no existe la carpeta, se crea una nueva con el nuevo nombre
        else:
            os.makedirs(nuevo_empaque, exist_ok=True)
            os.makedirs(nuevo_ficheros, exist_ok=True)
            print(f"[DEBUG] Carpeta creada: {nuevo_empaque} y {nuevo_ficheros}")
        return True

@proyectos_bp.route('/actualizar', methods=["POST", "GET"])
@login_required
def actu():
    
    if not 'editar' in request.form:
        
            nombre = request.form.get("nombre")
            director = request.form.get("director")
            idea_inicial = request.form.get("idea_inicial")

            id = request.form.get("id")
            
            project = Session.query(Project).filter(Project.id ==id).first()

            cambio = cambiar_nombre_carpetas(project, nombre)
            if project and cambio:
                #Si cambia el nombre debemos cambiar el nombre de las carpetas
                print("Proyecto a actualizar:", project)
                project.name = nombre
                project.responsable = director
                if idea_inicial:
                    project.idea_inicial = idea_inicial
                else:
                    project.idea_inicial = None
                
                Session.commit()
                return redirect('/proyectos')
            

    id_editar = request.form.get("editar")
    print("ID del proyecto a editar:", id_editar)
    if id_editar:
        project = Session.query(Project).filter(Project.id == int(id_editar)).first()
        print(project)
        if project:
               return render_template("proyectos/editarProyecto.html",  project = project)
        
    return redirect('/proyectos')
            
    
    