# html_routes.py
from flask import Blueprint, render_template

# Cria um blueprint para as rotas HTML
html_bp = Blueprint('html_bp', __name__, template_folder='../pages')

@html_bp.route("/")
def home():
    return render_template("index.html")

@html_bp.route("/conexoes")
def conexoes():
    return render_template("conexoes.html")

@html_bp.route("/dispositivos")
def dispositivos():
    return render_template("dispositivos.html")

@html_bp.route("/dispositivo")
def dispositivo():
    return render_template("dispositivo.html")

@html_bp.route("/graficos")
def graficos():
    return render_template("graficos.html")

@html_bp.route("/json")
def json():
    return render_template("teste.html")