from ollama import chat
from ollama import ChatResponse
import time
import requests
from flask import Blueprint, request, redirect, url_for, render_template
import requests
import time
import ollama  # Usa ollama directamente
from modelo.models import Prototype, Session, Project
from PIL import Image
from io import BytesIO
import base64
from google.genai import types
import json 
from google import genai
from flask import jsonify, session
import json
import time
import base64


from IPython.display import display
from IPython.display import Markdown


from aplicacion.chatbot.chatbot import ModeloIA



# Crear el Blueprint
agente_bp = Blueprint("agente", __name__, template_folder="aplicacion/templates")


@agente_bp.route('/', methods=["POST", "GET"])
def index():
    #Gestiona peticiones del usuario y envía respuesta del chat

    
   
    
    return render_template("chatbot/agente.html")


@agente_bp.route('/enviar', methods=['POST'])
def enviar():
    # Obtener el historial como JSON
    historial_json = request.form.get('historial', '{}')
    print("Historial recibido:", historial_json)
    try:
        mensajes = json.loads(historial_json)
    except json.JSONDecodeError:
        mensajes = {}
    
    # Obtener el nuevo prompt
    nuevo_prompt = request.form.get('prompt', '')
    
    respuesta_texto = ""
    if nuevo_prompt:
        # Construir contexto
        if 'project_id' in session:
                project = Session.query(Project).filter(Project.id == session['project_id']).first()
                if project:
                    resumen = project.resumen()

        contexto = "Contexto del proyecto: " + resumen + "\n\n"
        contexto += "\n".join(
            f"Usuario: {value}" if key.startswith('user') else f"Asistente: {value}"
            for key, value in mensajes.items()
        )
        
        # Generar respuesta
        try:
            respuesta, _ = ModeloIA(prompt=f"{contexto}\n\nUsuario: {nuevo_prompt}")
           
            respuesta_texto = respuesta
            print("Respuesta generada:", respuesta_texto)
            # Añadir nuevos mensajes al historial
            nuevo_idx = len(mensajes) // 2 + 1
            mensajes[f'user{nuevo_idx}'] = nuevo_prompt
            mensajes[f'chatbot{nuevo_idx}'] = respuesta
            
        except Exception as e:
            print(f"Error: {str(e)}")
            respuesta_texto = "Lo siento, hubo un error procesando tu solicitud."
    
    # Devolver JSON con la respuesta y el historial actualizado
    return jsonify({
        'respuesta': respuesta_texto,
        'historial': mensajes
    })

