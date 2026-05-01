# FUNCIONES DE FLASK
from flask import Blueprint, render_template, redirect, url_for
# FUNCIONES DE FLASK
from flask_wtf.csrf import CSRFError

home_bp = Blueprint("home", __name__, url_prefix="/home")

@home_bp.route('/')
def public_home():
    return render_template('home/home.html')

@home_bp.route("/politica_de_privacidad")
def privacy_policy():
    return render_template("home/privacy_policy.html")

@home_bp.route("/terminos_de_uso_y_compromisos")
def terms_of_use():
    return render_template("home/terms_of_use.html")