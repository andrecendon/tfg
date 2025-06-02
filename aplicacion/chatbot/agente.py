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


from google import genai

import time
import base64


from IPython.display import display
from IPython.display import Markdown


from aplicacion.chatbot.chatbot import ModeloIA



# Crear el Blueprint
agente_bp = Blueprint("agente", __name__, template_folder="aplicacion/templates")

#ya se ejecuta cuando /chatbot por el blueprint
@agente_bp.route('/', methods=["POST", "GET"])
def index():
    return render_template("chatbot/agente.html")

