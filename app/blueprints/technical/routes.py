# FUNCIONES DE FLASK
from flask import Blueprint
# UTILIDADES
from app.utils.decorators.technical_decorator import technical_required, login_required, mfa_required
# CONTROLADOR
from app.controllers.technical_controller import TechnicalController

technical_bp = Blueprint("technical", __name__, url_prefix="/fortress_tecnicos")
controller = TechnicalController()

@technical_bp.route("/dashboard")
@login_required
@technical_required
@mfa_required
def dashboard():
    return controller.dashboard()   

# CASES
@technical_bp.route("/cases")
@login_required
@technical_required
@mfa_required
def cases():
    return controller.cases()

# HISTORY
@technical_bp.route("/history")
@login_required
@technical_required
@mfa_required
def history():
    return controller.history()

@technical_bp.route("/history/export")
@login_required
@technical_required
@mfa_required
def history_export():
    return controller.history_export()

# SECURITY
@technical_bp.route("/centro_seguridad", methods=["GET", "POST"])
@login_required
@technical_required
@mfa_required
def security():
    return controller.security()

    # CAMBIAR CONTRASEÑA
@technical_bp.route("/centro_seguridad/contraseña", methods=["POST"])
@login_required
@technical_required
@mfa_required
def security_change_password():
    return controller.security_change_password()

    # SESIÓN CONTROLADOR
@technical_bp.route("/centro_seguridad/sesiones/<string:jti_sesion>/cerrar", methods=["POST"])
@login_required
@technical_required
@mfa_required
def security_cerrar_sesion(jti_sesion):
    return controller.security_session_one(jti_sesion)

@technical_bp.route("/centro_seguridad/sesiones/cerrar-todas", methods=["POST"])
@login_required
@technical_required
@mfa_required
def security_cerrar_sesiones():
    return controller.security_session_all()