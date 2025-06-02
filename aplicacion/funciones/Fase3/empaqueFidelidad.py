
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Empaque
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
import os
from werkzeug.utils import secure_filename
# Crear el Blueprint
empaqueFidelidad_bp = Blueprint("empaqueFidelidad", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@empaqueFidelidad_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    
    imagenes = []
    print("EMpaqueFidelidad: ", project.empaques)
    if len(project.empaques) == 0:
        emp = Empaque(project_id=project.id, is_favourite=True)
        Session.add(emp)
        Session.commit()
        print("EMPAQUE: ", emp.imagen1)
    for p in project.empaques:
        if p.is_favourite == True:
            if p.imagen1:
                imagenes.append(p.imagen1)
            if p.imagen2:
                imagenes.append(p.imagen2)
            if p.imagen3:
                imagenes.append(p.imagen3)
        
        
        Session.commit()
        
        break
    
    
    
    ruta = os.path.join( os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'empaques', project.name ) 
    os.makedirs(ruta, exist_ok=True)

    if os.path.exists(ruta) and os.path.isdir(ruta):
        print(ruta, "La carpeta fue creada correctamente.")
    else:
        print("La carpeta no se pudo crear.")
    
    print("Imagenes: ", imagenes)   
    
    return render_template("funciones/Fase3/empaqueFidelidad.html", proyecto=project, imagenes=imagenes)




@empaqueFidelidad_bp.route('/subirArchivos', methods=["POST", "GET"])
@login_required
def upload_files():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()

    if 'file' not in request.files:
        return "No se envió ningún archivo", 400
    
    file = request.files['file']
    
    print(f"[DEBUG] Archivo recibido: {file}")
    if file.filename == '':
        return "Nombre de archivo vacío", 400
    
    if file :
        
        p = Session.query(Empaque).filter(Empaque.project_id == project.id, Empaque.is_favourite == True).first()
        if p.imagen1 is None:
            p.imagen1 = file.filename
        elif p.imagen2 is None:
            p.imagen2 = file.filename
        elif p.imagen3 is None:
            p.imagen3 = file.filename
        else:
            return "El empaque ya tiene 3 imágenes", 400
        Session.commit()
            
        filename = secure_filename(file.filename)

        ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'empaques')
        save_path = os.path.join(ruta, project.name)
        os.makedirs(save_path, exist_ok=True)
        file.save(os.path.join(save_path, filename))
        print(f"[DEBUG] Archivo guardado en: {os.path.join(save_path, filename)}")
        return redirect(url_for('empaqueFidelidad.inicio'))
    else:
        return "Extensión de archivo no permitida", 400
    


@empaqueFidelidad_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
    print(f"\n[DEBUG] Proyecto actual: {project.name} (ID: {project_id})")
    if request.method == 'POST':
        fichero = request.form.get('eliminar')
        ruta = os.path.join( os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'empaques', project.name ) 
        file_path=os.path.join(ruta,fichero)
        print(f"[DEBUG] Intento de eliminar archivo: {file_path}")

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[DEBUG] Archivo eliminado: {file_path}")
                for emp in project.empaques:
                    if emp.imagen1 == fichero: 
                        emp.imagen1 = None
                    if emp.imagen2 == fichero: 
                        emp.imagen2 = None
                    if emp.imagen3 == fichero: 
                        emp.imagen3 = None
                Session.commit()
            except Exception as e:
                print(f"[ERROR] No se pudo eliminar el archivo: {str(e)}")
        else:
            print(f"[DEBUG] Archivo no encontrado: {file_path}")

    return redirect("/funciones/Fase3/empaqueFidelidad/")