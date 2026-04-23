from flask import Blueprint
from app.utils.decorators.admin_decorators import admin_required, login_required
from app.controllers.admin import AdminController

admin_bp = Blueprint("admin", __name__, url_prefix="/fortress_administrativo")
controller = AdminController()

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    return controller.dashboard()

# CASES
@admin_bp.route("/cases")
@login_required
@admin_required
def cases():
    return controller.cases()

# TICKET PANEL
@admin_bp.route("/ticket_panel/<string:id_ticket>", methods=["GET"])
@login_required
@admin_required
def ticket_panel_detail(id_ticket):
    return controller.ticket_panel_detail(id_ticket)

    # SIDERBAR
@admin_bp.route("/ticket_panel/<string:id_ticket>/estado", methods=["POST"])
@login_required
@admin_required
def ticket_update_estado(id_ticket):
    return controller.ticket_update_estado(id_ticket)

    # TAB COMENTARIOS
@admin_bp.route("/ticket_panel/<string:id_ticket>/comentario", methods=["POST"])
@login_required
@admin_required
def ticket_add_comentario(id_ticket):
    return controller.ticket_add_comentario(id_ticket)

    # TAB ASIGNAR CUPO
@admin_bp.route("/ticket_panel/<string:id_ticket>/cupo/filtro", methods=["POST"])
@login_required
@admin_required
def ticket_filtrar_cupo(id_ticket):
    return controller.ticket_filtrar_cupo(id_ticket)

@admin_bp.route("/ticket_panel/<string:id_ticket>/cupo", methods=["POST"])
@login_required
@admin_required
def ticket_asignar_cupo(id_ticket):
    return controller.ticket_asignar_cupo(id_ticket)

    # TAB DOCUMENTOS
@admin_bp.route("/ticket_panel/<string:id_ticket>/documento", methods=["POST"])
@login_required
@admin_required
def ticket_upload_doc(id_ticket):
    return controller.ticket_upload_doc(id_ticket)

@admin_bp.route("/ticket_panel/<string:id_ticket>/documento/<int:id_doc>/descargar", methods=["GET"])
@login_required
@admin_required
def ticket_download_doc(id_ticket, id_doc):
    return controller.ticket_download_doc(id_ticket, id_doc)

    # TAB COMFIRMAR ASIGNACIÓN
@admin_bp.route("/ticket_panel/<string:id_ticket>/cupo/autorizar", methods=["POST"])
@login_required
@admin_required
def ticket_autorizar_cupo(id_ticket):
    return controller.ticket_autorizar_cupo(id_ticket)

@admin_bp.route("/ticket_panel/<string:id_ticket>/cupo/cancelar", methods=["POST"])
@login_required
@admin_required
def ticket_cancelar_cupo(id_ticket):
    return controller.ticket_cancelar_cupo(id_ticket)

# ACCOUNTS
@admin_bp.route("/cuentas")
@login_required
@admin_required
def accounts():
    return controller.accounts()

    # ACCOUNTS USER
@admin_bp.route("/cuentas/usuarios")
@login_required
@admin_required
def accounts_user():
    return controller.accounts_user()

@admin_bp.route("/cuentas/usuarios/<int:id_usuario>/estado", methods=["POST"])
@login_required
@admin_required
def accounts_user_toggle_estado(id_usuario):
    return controller.toggle_estado_usuario(id_usuario)

@admin_bp.route("/cuentas/usuarios/estudiante/<int:id_estudiante>/estado", methods=["POST"])
@login_required
@admin_required
def accounts_estudiante_toggle_estado(id_estudiante):
    return controller.toggle_estado_estudiante(id_estudiante)

    # ACCOUNTS FUNC
@admin_bp.route("/cuentas/funcionarios")
@login_required
@admin_required
def accounts_func():
    return controller.accounts_func()

@admin_bp.route("/cuentas/funcionarios/<int:id_usuario>/estado", methods=["POST"])
@login_required
@admin_required
def accounts_func_toggle_estado(id_usuario):
    return controller.toggle_estado_tecnico(id_usuario)


# HISTORY
@admin_bp.route("/history")
@login_required
@admin_required
def history():
    return controller.history()

@admin_bp.route("/history/export")
@login_required
@admin_required
def history_export():
    return controller.history_export()

# COLEGIOS
@admin_bp.route("/colegios")
@login_required
@admin_required
def school_status():
    return controller.school_status()


@admin_bp.route("/colegios/agregar", methods=["POST"])
@login_required
@admin_required
def school_agregar():
    return controller.school_agregar()


@admin_bp.route("/colegios/<int:id_colegio>")
@login_required
@admin_required
def school_config(id_colegio):
    return controller.school_config(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/datos", methods=["POST"])
@login_required
@admin_required
def school_config_datos(id_colegio):
    return controller.school_config_datos(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/jornadas", methods=["POST"])
@login_required
@admin_required
def school_config_jornadas(id_colegio):
    return controller.school_config_jornadas(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/cupos", methods=["POST"])
@login_required
@admin_required
def school_config_cupos(id_colegio):
    return controller.school_config_cupos(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/estado", methods=["POST"])
@login_required
@admin_required
def school_config_estado(id_colegio):
    return controller.school_config_estado(id_colegio)

# SETTINGS
@admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    return controller.settings()

    # AFECTACIONES
@admin_bp.route("/settings/afectacion/crear", methods=["POST"])
@login_required
@admin_required
def settings_afectacion_crear():
    return controller.settings_afectacion_crear()

@admin_bp.route("/settings/afectacion/<int:id_afectacion>/editar", methods=["POST"])
@login_required
@admin_required
def settings_afectacion_editar(id_afectacion):
    return controller.settings_afectacion_editar(id_afectacion)

@admin_bp.route("/settings/afectacion/<int:id_afectacion>/estado", methods=["POST"])
@login_required
@admin_required
def settings_afectacion_estado(id_afectacion):
    return controller.settings_afectacion_estado(id_afectacion)

    # GRUPOS PREFERENCIALES
@admin_bp.route("/settings/grupo/crear", methods=["POST"])
@login_required
@admin_required
def settings_grupo_crear():
    return controller.settings_grupo_crear()

@admin_bp.route("/settings/grupo/<int:id_grupo>/editar", methods=["POST"])
@login_required
@admin_required
def settings_grupo_editar(id_grupo):
    return controller.settings_grupo_editar(id_grupo)

@admin_bp.route("/settings/grupo/<int:id_grupo>/estado", methods=["POST"])
@login_required
@admin_required
def settings_grupo_estado(id_grupo):
    return controller.settings_grupo_estado(id_grupo)

    # ESTRATOS
@admin_bp.route("/settings/estrato/crear", methods=["POST"])
@login_required
@admin_required
def settings_estrato_crear():
    return controller.settings_estrato_crear()

@admin_bp.route("/settings/estrato/<int:id_estrato>/editar", methods=["POST"])
@login_required
@admin_required
def settings_estrato_editar(id_estrato):
    return controller.settings_estrato_editar(id_estrato)

@admin_bp.route("/settings/estrato/<int:id_estrato>/estado", methods=["POST"])
@login_required
@admin_required
def settings_estrato_estado(id_estrato):
    return controller.settings_estrato_estado(id_estrato)