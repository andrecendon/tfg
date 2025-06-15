
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA
from werkzeug.utils import secure_filename
import os
# Crear el Blueprint
vidaUtil_bp = Blueprint("vidaUtil", __name__, template_folder="templates")


Session = DatabaseSession()
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_project_files(project_name):
    project_path = os.path.join(f'/aplicacion/static/ficheros/{project_name}')
    ruta = os.path.join( os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'ficheros' ) 
    os.makedirs(ruta, exist_ok=True)

    if os.path.exists(ruta) and os.path.isdir(ruta):
        print(ruta, "La carpeta fue creada correctamente.")
    else:
        print("La carpeta no se pudo crear.")

    files = {'microbiologico': [], 'fisicoquimico': [], 'sensoriales': [], 'vida útil': []}

    project_path = os.path.join(ruta, project_name)
    os.makedirs(project_path, exist_ok=True)
    if os.path.exists(project_path):
        for category in files.keys():
            category_path = os.path.join(project_path, category)
            # Recorremos las subcarpetas de los tipos
            os.makedirs(category_path, exist_ok=True)
            print("Categoria path ", category_path)
            for file in os.listdir(category_path):
                if file != '.gitkeep' and allowed_file(file):
                    files[category].append(file)

         
    
    return files




@vidaUtil_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    files = get_project_files(project.name)
    return render_template("funciones/Fase4/vidaUtil.html", files=files, project=project )



@vidaUtil_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
    print(f"\n[DEBUG] Proyecto actual: {project.name} (ID: {project_id})")
    if request.method == 'POST':
        fichero = request.form.get('eliminar')
        ruta = os.path.join( os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'ficheros' ) 
        file_path=os.path.join(ruta,fichero)
        print(f"[DEBUG] Intento de eliminar archivo: {file_path}")

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[DEBUG] Archivo eliminado: {file_path}")
            except Exception as e:
                print(f"[ERROR] No se pudo eliminar el archivo: {str(e)}")
        else:
            print(f"[DEBUG] Archivo no encontrado: {file_path}")
    return redirect("/funciones/Fase4/vidaUtil/")




@vidaUtil_bp.route('/subirArchivos', methods=["POST"])
@login_required
def upload_files():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")

    if 'file' not in request.files:
        return "No se envió ningún archivo", 400
    
    file = request.files['file']
    categoria = request.form.get('categoria')
    print(f"[DEBUG] Archivo recibido: {file}")
    if file.filename == '':
        return "Nombre de archivo vacío", 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'ficheros')
        save_path = os.path.join(ruta, project.name, categoria)
        os.makedirs(save_path, exist_ok=True)
        file.save(os.path.join(save_path, filename))
        print(f"[DEBUG] Archivo guardado en: {os.path.join(save_path, filename)}")
        return redirect(url_for('vidaUtil.inicio'))
    else:
        return "Extensión de archivo no permitida", 400