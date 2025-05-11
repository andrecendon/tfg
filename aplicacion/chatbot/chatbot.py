from ollama import chat
from ollama import ChatResponse
import time
import requests
from flask import Blueprint, request, redirect, url_for, render_template
import requests
import time
import ollama  # Usa ollama directamente
from modelo.models import Prototype
from PIL import Image
from io import BytesIO
import base64



import google.generativeai as genai
import time
import base64
from io import BytesIO
import pathlib
import textwrap

from IPython.display import display
from IPython.display import Markdown



def to_markdown(text):
            text = text.replace("•", "  *")
            return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))

#### STRUCTS QUE PUEDE USAR ####

from pydantic import BaseModel
class Suplemento(BaseModel):
            Nombre: str
            Características: str
            Marca: str
            Lugar_de_Comercialización: str
            Precio_Aproximado: str
            Link: str

class Empaque_IA(BaseModel):
     Nombre: str
     Características: str
     Precio:  float
     Proveedor: str
     Web: str 
     Imagen: str

class MatrizSustentable(BaseModel):
     Ingrediente: str
     NivelSostenibilidad: str
     CicloVida: str
     CadenaSuministro: str
     HuellaCarbono: str
     ImpactoAmbiental: str

class Normativa(BaseModel):
     nombre: str
     nombre_requisito: str
     requisito_especifico: str
     link: str

class simulacionProduccion_IA(BaseModel):
     etapa: str
     equipo: str
     proveedor: str
     enlace: str
     costo: str

     
     
def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))





# Crear el Blueprint
chatbot_bp = Blueprint("chatbot", __name__, template_folder="aplicacion/templates")

#ya se ejecuta cuando /chatbot por el blueprint
@chatbot_bp.route('/', methods=["POST", "GET"])
def index():
    return render_template("chatbot/chatbot.html")



def ModeloIA(prompt, model=None, config=None, api_key=None):
    # Configura tu API Key
    
    if model is None:
        model = "gemini-1.5-flash"
    if api_key is None:
        api_key = "AIzaSyD4nvMaH39V07jGRL_vuJxUnbhjNInUHCI"

    genai.configure(api_key=api_key)
    
    # Crea el modelo generativo
    model = genai.GenerativeModel(model)  # Usa el nombre del modelo directamente
    
    # Registra el tiempo de inicio
    start_time = time.time()
    
    # Genera la respuesta
    response = model.generate_content(prompt, config=config)

   
    # Registra el tiempo de fin
    end_time = time.time()

    # Calcula el tiempo transcurrido
    elapsed_time = end_time - start_time
    print(f"Tiempo transcurrido: {elapsed_time:.4f} segundos")

    if(config):
        return(response, elapsed_time)
    else:
        respuesta = response.text
    # Mostrar el resultado de la API
    
    return (respuesta, elapsed_time)




### Recibe prompts y los ejecuta devuelve respuesta y tiempo, tiene todos los casos de chat de 
@chatbot_bp.route('/chat', methods=["POST", "GET"])
def chat():
   
    if request.form["prompt"]:
        prompr = request.form["prompt"]
        
    return render_template("chatbot/chatbot.html")




#Devuelve una imagen de la Biblioteca PIL
def ModeloImagenIA(prompt, model=None, config=None, api_key=None, img_directory=None):
    
    if model is None:
        model = "gemini-2.0-flash-exp-image-generation"
    if api_key is None:
        api_key = "AIzaSyD4nvMaH39V07jGRL_vuJxUnbhjNInUHCI"
    if config is None: 
        config = types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )

        try:
            client = genai.Client(api_key=api_key)
            # Registra el tiempo de inicio
            start_time = time.time()

            response = client.models.generate_content(
                model=model,
                contents= prompt,
                config=config,
            )

            # Registra el tiempo de fin
            end_time = time.time()

            # Calcula el tiempo transcurrido
            elapsed_time = end_time - start_time
            print(f"Tiempo transcurrido: {elapsed_time:.4f} segundos")

            if response.candidates:
                parts = response.candidates[0].content.parts
                

                for part in parts:
                    if part.text is not None:
                        print(part.text)
                    elif part.inline_data is not None:
                        print("Imagen generada.")
                        image = Image.open(BytesIO(part.inline_data.data))
                        if img_directory is None:
                            return image, elapsed_time
                        else:
                            image.save(img_directory)
                            return image, elapsed_time

            print("No se generaron partes en la respuesta.")
            return None, elapsed_time

        except Exception as e:
            print(f"Error: {e}")
            return None, 0
    


