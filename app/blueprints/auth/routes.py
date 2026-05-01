# FUNCIONES DE FLASK
from flask import Blueprint, render_template, redirect, url_for
# FUNCIONES DE FLASK
from flask_wtf.csrf import CSRFError

from app.controllers.auth_controller import AuthController

# Declarar el Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
controller = AuthController()

# LOGIN
@auth_bp.route("/login-usuarios", methods=["GET", "POST"])
def login_user():
    return controller.login()

@auth_bp.route("/login-administradores", methods=["GET", "POST"])
def login_admin():
    return controller.login_ad()

@auth_bp.route("/login-tecnios", methods=["GET", "POST"])
def login_technical():
    return controller.login_tec()

# LOGOUT
@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    return controller.logout()

@auth_bp.route("/logout-administrador", methods=["GET", "POST"])
def logout_ad():
    return controller.logout_ad()

@auth_bp.route("/logout-tecnico", methods=["GET", "POST"])
def logout_tec():
    return controller.logout_tec()

# MFA
    # VERIFICAR MFA
@auth_bp.route("/verificar-mfa", methods=["GET", "POST"])
def verify_mfa():
    return controller.verify_mfa()

    # CONFIGURAR MFA
@auth_bp.route("/configurar-mfa", methods=["GET"])
def config_mfa():
    return controller.config_mfa()

@auth_bp.route("/configurar-mfa/confirmar", methods=["POST"])
def verify_config_mfa():
    return controller.verify_config_mfa()

# RECUPERACIÓN DE CONTRASEÑA
@auth_bp.route("/recuperar/enviar-codigo", methods=["GET", "POST"])
def recover_password_code():
    return controller.recover_password_code()

@auth_bp.route("/recuperar/verificar-codigo", methods=["GET", "POST"])
def recover_password_verify():
    return controller.recover_password_verify()

@auth_bp.route("/recuperar/nueva-contraseña", methods=["GET", "POST"])
def recover_password_new():
    return controller.recover_password_new()

# REGISTRO DE USUARIO
@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    return controller.register()

# MANEJO DE ERROR SI EL TOKEN ES INVALIDO
@auth_bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    return redirect(url_for('auth.login_user'))