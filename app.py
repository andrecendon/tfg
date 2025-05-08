from flask import Flask, render_template, session, redirect

from datetime import timedelta
import json
import atexit

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")
app.secret_key = 'your_secret_key'

# Base de datos
@app.route("/")
def home():
    return render_template("app/templates/login/login.html")

if __name__ == '__main__':
    app.run()
