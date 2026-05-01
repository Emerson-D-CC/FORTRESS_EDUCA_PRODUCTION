# FUNCIONES DE FLASK
from flask import Blueprint
from app.utils.decorators.admin_decorators import login_required, mfa_required
from app.utils.decorators.tickets_decorators import role_required
from app.controllers.tickets_controller import TicketsController

tickets_bp = Blueprint("ticket_ad", __name__, url_prefix="/fortress_ad_ticket")
controller = TicketsController()


# TICKET PANEL
@tickets_bp.route("/ticket_panel/<string:id_ticket>", methods=["GET"])
@login_required
@role_required
@mfa_required
def ticket_panel_detail(id_ticket):
    return controller.ticket_panel_detail(id_ticket)

    # SIDERBAR
@tickets_bp.route("/ticket_panel/<string:id_ticket>/estado", methods=["POST"])
@login_required
@role_required
@mfa_required
def ticket_update_estado(id_ticket):
    return controller.ticket_update_estado(id_ticket)

    # TAB COMENTARIOS
@tickets_bp.route("/ticket_panel/<string:id_ticket>/comentario", methods=["POST"])
@login_required
@role_required
@mfa_required
def ticket_add_comentario(id_ticket):
    return controller.ticket_add_comentario(id_ticket)

    # TAB ASIGNAR CUPO
@tickets_bp.route("/ticket_panel/<string:id_ticket>/cupo/filtro", methods=["GET", "POST"])
@login_required
@role_required
@mfa_required
def ticket_filtrar_cupo(id_ticket):
    return controller.ticket_filtrar_cupo(id_ticket)

@tickets_bp.route("/ticket_panel/<string:id_ticket>/cupo", methods=["GET", "POST"])
@login_required
@role_required
@mfa_required
def ticket_asignar_cupo(id_ticket):
    return controller.ticket_asignar_cupo(id_ticket)

    # TAB DOCUMENTOS
@tickets_bp.route("/ticket_panel/<string:id_ticket>/documento", methods=["POST"])
@login_required
@role_required
@mfa_required
def ticket_upload_doc(id_ticket):
    return controller.ticket_upload_doc(id_ticket)

@tickets_bp.route("/ticket_panel/<string:id_ticket>/documento/<int:id_doc>/descargar", methods=["GET"])
@login_required
@role_required
@mfa_required
def ticket_download_doc(id_ticket, id_doc):
    return controller.ticket_download_doc(id_ticket, id_doc)

    # TAB COMFIRMAR ASIGNACIÓN
@tickets_bp.route("/ticket_panel/<string:id_ticket>/cupo/autorizar", methods=["GET", "POST"])
@login_required
@role_required
@mfa_required
def ticket_autorizar_cupo(id_ticket):
    return controller.ticket_autorizar_cupo(id_ticket)

@tickets_bp.route("/ticket_panel/<string:id_ticket>/cupo/cancelar", methods=["POST"])
@login_required
@role_required
@mfa_required
def ticket_cancelar_cupo(id_ticket):
    return controller.ticket_cancelar_cupo(id_ticket)