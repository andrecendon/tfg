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
from google.genai import types
import json 


from google import genai

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

    
    mensajes = {}
    

    return render_template("chatbot/agente.html", mensajes = mensajes)

@agente_bp.route('/enviar', methods=["POST", "GET"])
def enviar():
    if request.method == 'POST':
        # Obtener el historial de mensajes

        mensajes = request.form.get('mensajes', '{}')
        print("Rq ", request.form)
        try:
            mensajes = eval(mensajes)  # Convertir string a dict (cuidado en producción)
        except:
            mensajes = {}
        
        # Obtener el nuevo prompt
        nuevo_prompt = request.form.get('prompt', '')
        if not nuevo_prompt:
            return render_template("chatbot/agente.html", mensajes=mensajes)
        
        # Construir el contexto para Gemini
        contexto = "Historial de conversación:\n"
        for key, value in mensajes.items():
            tipo = "Usuario" if key.startswith('user') else "Asistente"
            contexto += f"{tipo}: {value}\n"
        
        # Generar respuesta
        try:
            respuesta, tiempo = ModeloIA(prompt = contexto + "\nNuevo mensaje: " + nuevo_prompt)
            print("rePuesta: ", respuesta)

            # Añadir el nuevo mensaje del usuario y la respuesta del chatbot al diccionario
            # Buscar el siguiente índice disponible
            user_idx = max([int(k.replace('user', '')) for k in mensajes.keys() if k.startswith('user')] + [0]) + 1
            chatbot_idx = max([int(k.replace('chatbot', '')) for k in mensajes.keys() if k.startswith('chatbot')] + [0]) + 1

            mensajes[f'user{user_idx}'] = nuevo_prompt
            mensajes[f'chatbot{chatbot_idx}'] = respuesta

            print("MENsajes ", mensajes)
            
            
        except Exception as e:
            print(f"Error con Gemini: {str(e)}")
            respuesta = "Lo siento, hubo un error procesando tu solicitud."
            mensajes[f'chatbot{chatbot_idx}'] = respuesta
        
        print("mensajes ", mensajes)
        return render_template("chatbot/agente.html", mensajes=mensajes)
    
    # GET request - mostrar chat vacío
    return render_template("chatbot/agente.html", mensajes={})

