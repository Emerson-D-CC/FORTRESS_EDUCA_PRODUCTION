# FUNCIONES DE FLASK
from flask import Blueprint

from app.utils.decorators.aplication_decorators import acudiente_required, login_required, student_required
from app.controllers.aplication_controller import AplicationController


# Declara el Blueprint para Aplication
aplication_bp = Blueprint("aplication", __name__, url_prefix="/sistema_cupos")
controller = AplicationController()

# PANEL PRINCIPAL
@aplication_bp.route("/inicio", methods=["GET"])
@login_required
@acudiente_required
def dashboard():
    return controller.dashboard()

# NUEVA SOLICITUD (TICKET)
@aplication_bp.route("/solicitud_ticket/nuevo", methods=["GET", "POST"])
@login_required
@acudiente_required
@student_required
def ticket_request():
    return controller.ticket_request()

# SEGUIMIENTO DE SOLICITUDES DE CUPO (TICKETS)
@aplication_bp.route("/mis_solicitudes", methods=["GET"])
@login_required
@acudiente_required
def ticket_status():
    return controller.ticket_status()

@aplication_bp.route("/mis_solicitudes/<string:id_ticket>", methods=["GET", "POST"])
@login_required
@acudiente_required
def ticket_detail(id_ticket):
    return controller.ticket_detail(id_ticket)

@aplication_bp.route("/mis_solicitudes/<string:id_ticket>/descargar/<int:id_doc>", methods=["GET"])
@login_required
@acudiente_required
def ticket_download_doc(id_ticket, id_doc):
    return controller.ticket_detail_download_doc(id_ticket, id_doc)

@aplication_bp.route("/mis-solicitudes/<string:id_ticket>/comentario", methods=["POST"])
@login_required
def ticket_add_coment(id_ticket):
    return controller.ticket_detail_coment(id_ticket)

# REGISTRO ESTUDIANTE 
@aplication_bp.route("/aplication_registro_estudiante", methods=["GET", "POST"])
@login_required
@acudiente_required
def register_student():
    return controller.register_student()

# PERFIL USUARIO
@aplication_bp.route("/perfil", methods=["GET", "POST"])
@login_required
@acudiente_required
def profile():
    return controller.profile_user()

# SEGURIDAD
@aplication_bp.route("/centro_seguridad", methods=["GET", "POST"])
@login_required
@acudiente_required
def security():
    return controller.security()

    # CAMBIAR CONTRASEÑA
@aplication_bp.route("/centro_seguridad/contraseña", methods=["POST"])
@login_required
@acudiente_required
def security_hange_password():
    return controller.security_change_password()

    # MFA CONFIGURACION
@aplication_bp.route("/centro_seguridad/mfa/iniciar", methods=["POST"])
@login_required
@acudiente_required
def security_mfa_start():
    return controller.security_mfa()

@aplication_bp.route("/centro_seguridad/mfa/confirmar", methods=["POST"])
@login_required
@acudiente_required
def security_mfa_confir():
    return controller.security_mfa_confirm()

@aplication_bp.route("/centro_seguridad/mfa/desactivar", methods=["POST"])
@login_required
@acudiente_required
def security_mfa_disable():
    return controller.security_mfa_disable()

    # SESIÓN CONTROLADOR
@aplication_bp.route("/centro_seguridad/sesiones/<string:jti_sesion>/cerrar", methods=["POST"])
@login_required
@acudiente_required
def security_cerrar_sesion(jti_sesion):
    return controller.security_session_one(jti_sesion)

@aplication_bp.route("/centro_seguridad/sesiones/cerrar-todas", methods=["POST"])
@login_required
@acudiente_required
def security_cerrar_sesiones():
    return controller.security_session_all()

# AJUSTES
@aplication_bp.route("/configuración", methods=["GET"])
@login_required
@acudiente_required
def settings():
    return controller.settings()

    # PREFERENCIA NOTIFICACIONES
@aplication_bp.route("/configuración/notif-email", methods=["POST"])
@login_required
@acudiente_required
def settings_notif_email():
    return controller.settings_notif_email()

@aplication_bp.route("/configuración/notif-navegador", methods=["POST"])
@login_required
@acudiente_required
def settings_notif_browser():
    return controller.settings_notif_browser()

    # ELIMINAR CUENTA
@aplication_bp.route("/configuración/eliminar-cuenta", methods=["POST"])
@login_required
@acudiente_required
def settings_delete_account():
    return controller.settings_delete_account()