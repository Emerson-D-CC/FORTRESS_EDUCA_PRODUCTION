# FUNCIONES DE FLASK
from flask import Blueprint
from app.utils.decorators.admin_decorators import admin_required, login_required, mfa_required
from app.controllers.admin_controller import AdminController

admin_bp = Blueprint("admin", __name__, url_prefix="/fortress_administrativo")
controller = AdminController()

@admin_bp.route("/dashboard")
@login_required
@admin_required
@mfa_required
def dashboard():
    return controller.dashboard()

# CASES
@admin_bp.route("/cases")
@login_required
@admin_required
@mfa_required
def cases():
    return controller.cases()

@admin_bp.route("/cases/export")
#@login_required
#@admin_required
def cases_export():
    return controller.cases_export()

# ACCOUNTS
@admin_bp.route("/cuentas")
@login_required
@admin_required
@mfa_required
def accounts():
    return controller.accounts()

    # REPORTS
@admin_bp.route("/cuentas/exportar/acceso")
@login_required
@admin_required
@mfa_required
def accounts_exportar_acceso():
    return controller.accounts_exportar_acceso()

@admin_bp.route("/cuentas/exportar/acciones")
@login_required
@admin_required
@mfa_required
def accounts_exportar_acciones():
    return controller.accounts_exportar_acciones()

# ACCOUNTS NEW
@admin_bp.route("/cuentas/nueva-cuenta", methods=["GET", "POST"])
@login_required
@admin_required
@mfa_required
def accounts_new():
    return controller.accounts_new()

# ACCOUNTS USER
@admin_bp.route("/cuentas/usuarios")
@login_required
@admin_required
@mfa_required
def accounts_user():
    return controller.accounts_user()

@admin_bp.route("/cuentas/usuarios/<int:id_usuario>/estado", methods=["POST"])
@login_required
@admin_required
@mfa_required
def accounts_user_toggle_estado(id_usuario):
    return controller.toggle_estado_usuario(id_usuario)

@admin_bp.route("/cuentas/usuarios/estudiante/<int:id_estudiante>/estado", methods=["POST"])
@login_required
@admin_required
@mfa_required
def accounts_estudiante_toggle_estado(id_estudiante):
    return controller.toggle_estado_estudiante(id_estudiante)

@admin_bp.route("/cuentas/usuarios/export/acudientes")
@login_required
@admin_required
@mfa_required
def accounts_user_exportar_acudientes():
    return controller.accounts_user_exportar_acudientes()

@admin_bp.route("/cuentas/usuarios/export/estudiantes")
@login_required
@admin_required
@mfa_required
def accounts_user_exportar_estudiantes():
    return controller.accounts_user_exportar_estudiantes()

    # ACCOUNTS FUNC
@admin_bp.route("/cuentas/funcionarios")
@login_required
@admin_required
@mfa_required
def accounts_func():
    return controller.accounts_func()

@admin_bp.route("/cuentas/funcionarios/<int:id_usuario>/estado", methods=["POST"])
@login_required
@admin_required
@mfa_required
def accounts_func_toggle_estado(id_usuario):
    return controller.accounts_func_toggle_estado(id_usuario)

@admin_bp.route("/cuentas/funcionarios/export/tecnicos")
@login_required
@admin_required
@mfa_required
def accounts_func_exportar_tecnicos():
    return controller.accounts_func_exportar_tecnicos()

@admin_bp.route("/cuentas/funcionarios/export/admins")
@login_required
@admin_required
@mfa_required
def accounts_func_exportar_admins():
    return controller.accounts_func_exportar_admins()

# HISTORY
@admin_bp.route("/history")
@login_required
@admin_required
@mfa_required
def history():
    return controller.history()

@admin_bp.route("/history/export")
@login_required
@admin_required
@mfa_required
def history_export():
    return controller.history_export()

# COLEGIOS
@admin_bp.route("/colegios")
@login_required
@admin_required
@mfa_required
def school_status():
    return controller.school_status()


@admin_bp.route("/colegios/agregar", methods=["POST"])
@login_required
@admin_required
@mfa_required
def school_agregar():
    return controller.school_agregar()


@admin_bp.route("/colegios/<int:id_colegio>")
@login_required
@admin_required
@mfa_required
def school_config(id_colegio):
    return controller.school_config(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/datos", methods=["POST"])
@login_required
@admin_required
@mfa_required
def school_config_datos(id_colegio):
    return controller.school_config_datos(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/jornadas", methods=["POST"])
@login_required
@admin_required
@mfa_required
def school_config_jornadas(id_colegio):
    return controller.school_config_jornadas(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/cupos", methods=["POST"])
@login_required
@admin_required
@mfa_required
def school_config_cupos(id_colegio):
    return controller.school_config_cupos(id_colegio)


@admin_bp.route("/colegios/<int:id_colegio>/estado", methods=["POST"])
@login_required
@admin_required
@mfa_required
def school_config_estado(id_colegio):
    return controller.school_config_estado(id_colegio)

# SETTINGS
@admin_bp.route("/settings")
@login_required
@admin_required
@mfa_required
def settings():
    return controller.settings()

    # AFECTACIONES
@admin_bp.route("/settings/afectacion/crear", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_afectacion_crear():
    return controller.settings_afectacion_crear()

@admin_bp.route("/settings/afectacion/<int:id_afectacion>/editar", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_afectacion_editar(id_afectacion):
    return controller.settings_afectacion_editar(id_afectacion)

@admin_bp.route("/settings/afectacion/<int:id_afectacion>/estado", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_afectacion_estado(id_afectacion):
    return controller.settings_afectacion_estado(id_afectacion)

    # GRUPOS PREFERENCIALES
@admin_bp.route("/settings/grupo/crear", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_grupo_crear():
    return controller.settings_grupo_crear()

@admin_bp.route("/settings/grupo/<int:id_grupo>/editar", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_grupo_editar(id_grupo):
    return controller.settings_grupo_editar(id_grupo)

@admin_bp.route("/settings/grupo/<int:id_grupo>/estado", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_grupo_estado(id_grupo):
    return controller.settings_grupo_estado(id_grupo)

    # ESTRATOS
@admin_bp.route("/settings/estrato/crear", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_estrato_crear():
    return controller.settings_estrato_crear()

@admin_bp.route("/settings/estrato/<int:id_estrato>/editar", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_estrato_editar(id_estrato):
    return controller.settings_estrato_editar(id_estrato)

@admin_bp.route("/settings/estrato/<int:id_estrato>/estado", methods=["POST"])
@login_required
@admin_required
@mfa_required
def settings_estrato_estado(id_estrato):
    return controller.settings_estrato_estado(id_estrato)


# SECURITY
@admin_bp.route("/centro_seguridad", methods=["GET", "POST"])
@login_required
@admin_required
@mfa_required
def security():
    return controller.security()

    # CAMBIAR CONTRASEÑA
@admin_bp.route("/centro_seguridad/contraseña", methods=["POST"])
@login_required
@admin_required
@mfa_required
def security_change_password():
    return controller.security_change_password()

    # SESIÓN CONTROLADOR
@admin_bp.route("/centro_seguridad/sesiones/<string:jti_sesion>/cerrar", methods=["POST"])
@login_required
@admin_required
@mfa_required
def security_cerrar_sesion(jti_sesion):
    return controller.security_session_one(jti_sesion)

@admin_bp.route("/centro_seguridad/sesiones/cerrar-todas", methods=["POST"])
@login_required
@admin_required
@mfa_required
def security_cerrar_sesiones():
    return controller.security_session_all()