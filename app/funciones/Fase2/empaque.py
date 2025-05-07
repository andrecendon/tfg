
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, Empaque
from collections import defaultdict
from chatbot.chatbot import ModeloImagenIA, ModeloIA, Empaque_IA, Modelo_Hugging
from flask_login import login_required
import os
from PIL import Image
from chatbot.chatbot import ModeloIA
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

        #Hacemos que para todos los Empaque_IA se le guarde la url de su imagen: img="imagenesIA/"+f"{project.name}/"+ f"{emp.Nombre}"+ ".png"

        for emp in empaques: 
             emp.Imagen="imagenesIA/"+f"{project.name}/"+ f"{emp.Nombre}"+ ".png"
             print("NOMBRE EMPAUQETADO", emp.Imagen)
        
       


        tiempo_total += tiempo

    
        #Imagen - hacemos una llamada por cada uno de los empaques
        
        if request.form.get("name") is not None: 
            nombre_imagen= request.form.get("name")
        else:
            nombre_imagen = "empaque.png"
        ruta_base = os.path.abspath(os.path.join(os.getcwd(), '..'))  # sube una carpeta: "carpeta abuela"
        ruta_destino = os.path.join(ruta_base, "app", "static", "imagenesIA", project.name)  # carpeta de la imagen
        

        # Crear carpetas si no existen
        os.makedirs(ruta_destino, exist_ok=True)
        alimentos = ""
        for f in project.foods:
            alimentos += f"{f.food_description}, "
        lista_imagenes = []
        for emp in empaques: 
            ruta_completa = os.path.join(ruta_destino, f"{emp.Nombre}.png")
            directory = "imagenesIA/"+f"{project.name}/"+ f"{emp.Nombre}"+ ".png"
            lista_imagenes.append(directory)
            prompt_emp = "Genera una imagen realista de un prototipo de envoltorio, de este tipo:  "+ emp.Nombre + ", con estas características" + emp.Características + "del alimento que tiene estos ingredientes" + alimentos 
            imagen, tiempo = ModeloImagenIA(prompt = prompt_emp, img_directory=ruta_completa)

            #im = Modelo_Hugging(prompt="Astronaut riding a horse") #Se agota muy rapido los ctos de la API
            tiempo_total += tiempo
        
        

    print(lista_imagenes)
        
    return render_template("funciones/Fase2/prototipoEmpaque.html", empaques_IA=empaques, proyecto=project, prompt= prompt, imagenes=lista_imagenes, project=project, tiempo=tiempo_total)

@empaque_bp.route('/añadir', methods=["POST", "GET"])
@login_required
def añadir():
    #Recibe un Empaque_IA y crea un Empaque normal en el proyecto.
    
    try:
        if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return redirect("/funciones/Fase2/empaque")
       
        if request.form.get('nombre') is not None:

            
            nuevo_empaque = Empaque(
            nombre=request.form.get('nombre'),
            caracteristicas=request.form.get('caracteristicas', ''), 
            precio=float(request.form.get('precio', 0)) if request.form.get('precio') else 0.0,
            proveedor=request.form.get('proveedor', ''),
            web=request.form.get('web', ''),
            imagen=request.form.get('imagen', ''), 
            notas=request.form.get('notas', ''),
            project_id=project.id
            )

            print(nuevo_empaque)
        
            Session.add(nuevo_empaque)
            Session.commit()
            

        
        return redirect("/funciones/Fase2/empaque")

    except Exception as e:
        print("Operación de creación de empaque abortada")
        Session.rollback()
        return redirect("/funciones/Fase2/empaque")



@empaque_bp.route('/editar', methods=["POST", "GET"])
@login_required
def editar():
    if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
    
    #Recibe la imagen del prompt y permite editarla con un prompt


    
    return redirect("/funciones/Fase2/empaque")



@empaque_bp.route('/eliminar', methods=["POST", "GET"])
@login_required
def eliminar():
    #Recibe un Empaque_IA y crea un Empaque normal en el proyecto.
    
    try:
        if 'project_id' in session:
            project_id = session.get('project_id')
            project = Session.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return redirect("/funciones/Fase2/empaque")
        actualizar = request.form.get("actualizar")
        eliminar = request.form.get("eliminar")
        notas = request.form.get("notas")
        id = request.form.get("id")
        if id and eliminar:
            empaque = Session.query(Empaque).filter(Empaque.id==id).first()
            Session.delete(empaque)
            Session.commit()
        if actualizar and notas and id:
            emp = Session.query(Empaque).filter(Empaque.id==int(id)).first()
            if emp:
                emp.notas =notas 
                Session.commit()
            print("notas actualizada")
            

        
        return redirect("/funciones/Fase2/empaque")

    except Exception as e:
        print("Operación de eliminar empaque abortada")
        Session.rollback()
        return redirect("/funciones/Fase2/empaque")