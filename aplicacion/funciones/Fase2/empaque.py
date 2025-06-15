
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Empaque
from collections import defaultdict
from aplicacion.chatbot.chatbot import ModeloImagenIA, ModeloIA, Empaque_IA
from flask_login import login_required
import os
from PIL import Image
from werkzeug.utils import secure_filename
from aplicacion.chatbot.chatbot import ModeloIA
# Crear el Blueprint

empaque_bp = Blueprint("empaque", __name__, template_folder="templates")


Session = DatabaseSession()


@empaque_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
    
    
    
    alimentos = ""
    for f in project.foods:
        alimentos += f"{f.food_description}, "
    
    prompt= "Realizar una tabla con 4 " +\
             "propuestas de posibles empaques que cuiden los nutrientes que sea sustentable que sea de bajo costo, que se comercialice en la unión europea incluir , "+\
             "la tabla debe tener nombre del empaque, características, precio , nombre de proveedor , web o contactos. Los ingredientes del producto son  " + alimentos

     #Se añadió algo a notas de un protototipo
    
    
            


    if project.empaques: 
        empaques = project.empaques
        return render_template("funciones/Fase2/prototipoEmpaque.html",proyecto=project ,prompt=prompt, empaques=empaques)
    
    return render_template("funciones/Fase2/prototipoEmpaque.html",proyecto=project ,prompt=prompt)




@empaque_bp.route('/favorito', methods=["POST", "GET"])
@login_required
def favorito():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
        if 'empaque_id' in request.form:
            empaque_id = request.form.get('empaque_id')
            empaque = Session.query(Empaque).filter(Empaque.id == empaque_id, Project.id==project.id).first()
            
            if empaque.is_favourite is False:
                empaque.is_favourite = True
                for emp in project.empaques:
                    if emp.id != empaque.id:
                        emp.is_favourite = False
            else: 
                empaque.is_favourite = False
            Session.commit()
            print(f"[DEBUG] Estado de favorito actualizado para el empaque: {empaque.nombre}, is_favourite: {empaque.is_favourite}")
    return redirect(url_for('empaque.inicio')) 

@empaque_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
        if 'empaque_id' in request.form:
            empaque_id = request.form.get('empaque_id')
            empaque = Session.query(Empaque).filter(Empaque.id == empaque_id, Project.id==project.id).first()
            #Eliminamos las imagenes del empaque si existe
            if empaque.imagen1 or empaque.imagen2 or empaque.imagen3:
                ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'empaques', project.name)
                old_image_path1 = os.path.join(ruta, empaque.imagen1) if empaque.imagen1 else None
                old_image_path2 = os.path.join(ruta, empaque.imagen2) if empaque.imagen2 else None
                old_image_path3 = os.path.join(ruta, empaque.imagen3) if empaque.imagen3 else None
                
                for image_path in [old_image_path1, old_image_path2, old_image_path3]:
                    if image_path and os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"[DEBUG] Imagen eliminada: {image_path}")
                
            
            Session.delete(empaque)
            Session.commit()
            print(f"[DEBUG] Empaque eliminado: {empaque.nombre}")
        

    return redirect(url_for('empaque.inicio')) 


@empaque_bp.route('/guardar', methods=["POST", "GET"])
@login_required
def guardar():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")

    if 'empaque_id' in request.form: 
        empaque_id = request.form.get('empaque_id')
        empaque = Session.query(Empaque).filter(Empaque.id == empaque_id, Empaque.project_id == project.id).first()
        
        if empaque:
            empaque.nombre = request.form.get('nombre', '')
            empaque.caracteristicas = request.form.get('caracteristicas', '')
            empaque.proveedor = request.form.get('proveedor', '')
            empaque.web = request.form.get('web', '')
            empaque.precio = float(request.form.get('precio', 0)) if request.form.get('precio') else 0.0
            
            Session.commit()
            print(f"[DEBUG] Empaque actualizado: {empaque.nombre}")
        else:
            print("[ERROR] No se encontró el empaque con el ID proporcionado.")
    return redirect(url_for('empaque.inicio'))

@empaque_bp.route('/crearPrototipo', methods=["POST", "GET"])
@login_required
def crear():
    if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
    
    #Recuperamos la información y creamos nuevo prototipo de empaque
    if 'proveedor' and 'precio' and 'nombre' and 'caracteristicas' and 'web' in request.form:
        nuevo_empaque = Empaque(
            nombre=request.form.get('nombre'),
            caracteristicas=request.form.get('caracteristicas', ''), 
            precio=float(request.form.get('precio', 0)) if request.form.get('precio') else 0.0,
            proveedor=request.form.get('proveedor', ''),
            web=request.form.get('web', ''),
            project_id=project.id
        )

        Session.add(nuevo_empaque)
        Session.commit()
    
    print("Nuevo empaque creado:", nuevo_empaque)

    return redirect("/funciones/Fase2/empaque")


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@empaque_bp.route('/subirImagen', methods=["POST", "GET"])
@login_required
def imagen():
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")

    if 'nueva_imagen' not in request.files:
        return "No se envió ningún archivo", 400
    
    file = request.files['nueva_imagen']
    categoria = request.form.get('categoria')
    print(f"[DEBUG] Archivo recibido: {file}")
    if file.filename == '':
        return "Nombre de archivo vacío", 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'empaques', project.name)
        
        os.makedirs(ruta, exist_ok=True)
        file.save(os.path.join(ruta, filename))
        print(f"[DEBUG] Archivo guardado en: {os.path.join(ruta, filename)}")
        emp_id = request.form.get('empaque_id')
        for emp in project.empaques:
            if emp.id == int(emp_id):
                #Eliminamos la imagen anterior si existe
                if emp.imagen1:
                    old_image_path = os.path.join(ruta, emp.imagen1)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                        print(f"[DEBUG] Imagen anterior eliminada: {old_image_path}")

                emp.imagen1 = filename
                Session.commit()
                print(f"[DEBUG] Imagen guardada para el empaque {emp.nombre}: {filename}")
                break
        return redirect(url_for('empaque.inicio'))
    else:
        return "Extensión de archivo no permitida", 400

  



@empaque_bp.route('/generar', methods=["POST", "GET"])
@login_required
def generarEmpaque():
    tiempo_total=0
    
    if request.method == "POST":
        prompt = request.form.get("prompt")
       
        if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
        
       
        #Texto 
        config={
                    'response_mime_type': 'application/json',
                    'response_schema': list[Empaque_IA],}
        


        empaques, tiempo = ModeloIA(prompt, config=config)
        empaques: list[Empaque_IA] = empaques.parsed


        for emp in empaques: 
             print(f"[DEBUG] Empaque generado: {emp.Nombre}, Precio: {emp.Precio}, Proveedor: {emp.Proveedor}, Web: {emp.Web}, Características: {emp.Caracteristicas}")
        
        tiempo_total += tiempo

       
        
    return render_template("funciones/Fase2/prototipoEmpaque.html", empaques_IA=empaques, proyecto=project, prompt= prompt,  project=project, tiempo=tiempo_total)

@empaque_bp.route('/guardarEmpaqueIA', methods=["POST", "GET"])
@login_required
def añadir():
    #Recibe un Empaque_IA y crea un Empaque normal en el proyecto.
    
   
        if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
        
        print(request.form)
       
        if request.form.get('nombre') is not None:

            
            nuevo_empaque = Empaque(
            nombre=request.form.get('nombre'),
            caracteristicas=request.form.get('caracteristicas', ''), 
            precio=float(request.form.get('precio', 0)) if request.form.get('precio') else 0.0,
            proveedor=request.form.get('proveedor', ''),
            web=request.form.get('web', ''),
            project_id=project.id
            )

            print(nuevo_empaque)
        
            Session.add(nuevo_empaque)
            Session.commit()
            

        
        return redirect("/funciones/Fase2/empaque")

    



@empaque_bp.route('/editar', methods=["POST", "GET"])
@login_required
def editar():
    if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
    
    

    
    return redirect("/funciones/Fase2/empaque")



