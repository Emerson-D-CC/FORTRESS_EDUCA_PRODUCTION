from app.utils.database_utils import db

# ====================================================================================================================================================
#                                           PAGINA DASHBOARD.HTML
# ====================================================================================================================================================

def sp_dashboard_metricas() -> dict | None:
    """Retorna las métricas agregadas para el dashboard del admin"""
    resultado = db.call_procedure("sp_dashboard_metricas", ())
    return resultado[0] if resultado else None

def sp_dashboard_chart_actividad() -> list[dict]:
    """Retorna la actividad de solicitudes de los últimos 7 días para el gráfico del dashboard"""
    return db.call_procedure("sp_dashboard_chart_actividad", ()) or []
    

# ====================================================================================================================================================
#                                           PAGINA CASES.HTML
# ====================================================================================================================================================


def sp_cases_listar_todos(id_estado: int | None = None, id_grado: int | None = None, id_afectacion: int | None = None) -> list[dict]:
    """Retorna todos los tickets activos con soporte de filtros opcionales"""
    return db.call_procedure(
        "sp_cases_listar_todos",()
    ) or []
 
 
def sp_cases_metricas() -> dict | None:
    """Retorna las métricas agregadas para las tarjetas superiores"""
    resultado = db.call_procedure("sp_cases_metricas", ())
    return resultado[0] if resultado else None
 
 
# Catálogos para los filtros
 
def sp_catalogo_estados_ticket() -> list[dict]:
    """Estados del ticket activos (para el <select> de filtro de estado)"""
    return db.call_procedure("sp_catalogo_estados_ticket", ()) or []
 
 
def sp_catalogo_grados() -> list[dict]:
    """Grados disponibles (para el <select> de filtro de grado)"""
    return db.call_procedure("sp_catalogo_grados", ()) or []
 
 
def sp_catalogo_tipo_afectacion() -> list[dict]:
    """Tipos de afectación (para el <select> de filtro de afectación)"""
    return db.call_procedure("sp_catalogo_tipo_afectacion", ()) or []

# Reporte de datos

def sp_cases_exportar_todos() -> list[dict]:
    """Retorna TODOS los tickets activos (para CSV/PDF)"""
    return db.call_procedure("sp_cases_listar_todos", ()) or []

# ====================================================================================================================================================
#                                           PAGINA ACCOUNTS.HTML
# ====================================================================================================================================================

def sp_admin_metricas_accounts():
    resultado = db.call_procedure("sp_admin_metricas_accounts", ())
    return resultado[0] if resultado else {}

def sp_admin_roles_consultar():
    return db.call_procedure("sp_tbl_rol_consultar", ()) or []

def sp_admin_eventos_acceso_consultar():
    return db.call_procedure("sp_admin_eventos_acceso_consultar", ()) or []

def sp_admin_eventos_auditoria_consultar():
    return db.call_procedure("sp_admin_eventos_auditoria_consultar", ()) or []

def sp_admin_navegadores_consultar():
    return db.call_procedure("sp_admin_navegadores_consultar", ()) or []

def sp_admin_historial_acceso_listar(id_rol=None, evento=None, navegador=None):
    return db.call_procedure(
        "sp_admin_historial_acceso_listar",
        (id_rol, evento, navegador)
    ) or []

def sp_admin_historial_acciones_listar(id_rol=None, evento=None):
    return db.call_procedure(
        "sp_admin_historial_acciones_listar",
        (id_rol, evento)
    ) or []



# ====================================================================================================================================================
#                                           PAGINA ACCOUNTS_NEW
# ====================================================================================================================================================

def sp_obtener_tipos_documento_admin():
    """Todos los tipos de identificación (sin filtro de Tipo_Usuario)."""
    return db.call_procedure("sp_tbl_tipo_iden_consultar_admin", ()) or []

def sp_obtener_tipos_documento_est():
    return db.call_procedure("sp_tbl_tipo_identificacion_consultar_est", ()) or []

def sp_obtener_parentesco_admin():
    """Todos los tipos de parentesco activos."""
    return db.call_procedure("sp_tbl_parentesco_consultar_admin", ()) or []

def sp_obtener_parentesco_est():
    return db.call_procedure("sp_tbl_parentesco_consultar_est", ()) or []


def sp_obtener_barrios_admin():
    """Reutiliza el mismo SP de la pantalla de registro público."""
    return db.call_procedure("sp_tbl_barrio_consultar", ()) or []


def sp_obtener_grados():
    return db.call_procedure("sp_tbl_grado_consultar", ()) or []


def sp_obtener_colegios():
    return db.call_procedure("sp_tbl_colegio_consultar", ()) or []


def sp_obtener_generos():
    return db.call_procedure("sp_tbl_genero_consultar", ()) or []


def sp_obtener_grupos_preferenciales():
    return db.call_procedure("sp_tbl_grupo_pref_consultar", ()) or []


def sp_obtener_acudientes_activos():
    """Lista de acudientes activos para vincular con un estudiante."""
    return db.call_procedure("sp_tbl_acudientes_activos_consultar", ()) or []

#  VERIFICACIONES

def sp_verificar_usuario_admin(email: str, documento: str):
    """Verifica si ya existe un usuario con ese email o documento."""
    return db.call_procedure("sp_usuario_verificar_existente", (email, documento))


def sp_verificar_estudiante_admin(documento: str):
    """Verifica si ya existe un estudiante registrado con ese documento."""
    return db.call_procedure("sp_estudiante_verificar_existente", (documento,))

# CREACIÓN

def sp_registrar_usuario_admin(data: tuple):
    return db.call_procedure("sp_registrar_usuario_por_admin", data, commit=False)


def sp_registrar_estudiante_admin(data: tuple):
    return db.call_procedure("sp_registrar_estudiante_admin", data, commit=False)



# ====================================================================================================================================================
#                                           PAGINA ACCOUNTS_USER.HTML
# ====================================================================================================================================================

def sp_admin_metricas_usuarios():
    resultado = db.call_procedure("sp_admin_metricas_usuarios", ())
    return resultado[0] if resultado else {}

def sp_admin_acudientes_listar():
    return db.call_procedure("sp_admin_acudientes_listar", ()) or []

def sp_admin_estudiantes_listar():
    return db.call_procedure("sp_admin_estudiantes_listar", ()) or []

def sp_admin_toggle_estado_usuario(id_usuario, nuevo_estado, ejecutor_id, ip, user_agent):
    return db.call_procedure(
        "sp_admin_toggle_estado_usuario",
        (id_usuario, nuevo_estado, ejecutor_id, ip, user_agent),
        commit=True
    )

def sp_admin_toggle_estado_estudiante(id_estudiante, nuevo_estado, ejecutor_id, ip, user_agent):
    return db.call_procedure(
        "sp_admin_toggle_estado_estudiante",
        (id_estudiante, nuevo_estado, ejecutor_id, ip, user_agent),
        commit=True
    )



# ====================================================================================================================================================
#                                           PAGINA ACCOUNTS_FUNC.HTML
# ====================================================================================================================================================

def sp_admin_metricas_funcionarios():
    resultado = db.call_procedure("sp_admin_metricas_funcionarios", ())
    return resultado[0] if resultado else {}

def sp_admin_tecnicos_listar(estado=None):
    return db.call_procedure(
        "sp_admin_tecnicos_listar",
        (estado,)
    ) or []

def sp_admin_administradores_listar():
    return db.call_procedure("sp_admin_administradores_listar", ()) or []

def sp_admin_toggle_estado_tecnico(id_usuario, nuevo_estado, ejecutor_id, ip, user_agent):
    """Reutiliza el mismo SP que toggle_estado_usuario"""
    return db.call_procedure(
        "sp_admin_toggle_estado_usuario",
        (id_usuario, nuevo_estado, ejecutor_id, ip, user_agent),
        commit=True
    )
    
def sp_admin_tecnicos_exportar() -> list[dict]:
    """Retorna TODOS los técnicos sin filtrar (filtrado en Python)."""
    return db.call_procedure("sp_admin_tecnicos_listar", (None,)) or []

def sp_admin_administradores_exportar() -> list[dict]:
    """Retorna todos los administradores para exportación."""
    return db.call_procedure("sp_admin_administradores_listar", ()) or []



# ====================================================================================================================================================
#                                           PAGINA HISTORY.HTML
# ====================================================================================================================================================

def sp_history_listar_todos() -> list[dict]:
    """Retorna TODOS los registros de auditoría activos"""
    return db.call_procedure("sp_history_listar_todos", ()) or []

# EXPORTAR (CSV o PDF)

def sp_history_exportar_auditoria(tipo_evento, fecha_desde, fecha_hasta) -> list[dict]:
    """Retorna TODOS los registros sin paginar (para CSV)"""
    return (
        db.call_procedure(
            "sp_history_exportar_auditoria",
            (tipo_evento, fecha_desde, fecha_hasta),
        )
        or []
    )
    
    

# ====================================================================================================================================================
#                                           PAGINA SCHOOL_STATUS.HTML
# ====================================================================================================================================================


# CATÁLOGOS (datos de apoyo para formularios y filtros)

def sp_catalogo_barrios_activos() -> list[dict]:
    """Barrios activos para poblar SelectField de formularios"""
    return db.call_procedure("sp_catalogo_barrios_activos", ()) or []


def sp_catalogo_jornadas_activas() -> list[dict]:
    """Jornadas activas para filtros y gestión de jornadas"""
    return db.call_procedure("sp_catalogo_jornadas_activas", ()) or []


def sp_catalogo_grados_activos() -> list[dict]:
    """Grados activos para construir la tabla de cupos"""
    return db.call_procedure("sp_catalogo_grados_activos", ()) or []


# LISTADO Y ESTADÍSTICAS (school_status.html)

def sp_admin_colegios_estadisticas() -> dict:
    """Métricas globales para las tarjetas de resumen"""
    resultado = db.call_procedure("sp_admin_colegios_estadisticas", ()) or []
    return resultado[0] if resultado else {}


def sp_admin_colegios_listar() -> list[dict]:
    """Todos los colegios con datos"""
    return db.call_procedure("sp_admin_colegios_listar", ()) or []



# ====================================================================================================================================================
#                                           PAGINA SCHOOL_CONFIG.HTML
# ====================================================================================================================================================


def sp_admin_colegio_detalle(id_colegio: int) -> dict | None:
    """Datos completos de un colegio para la página de gestión"""
    resultado = db.call_procedure("sp_admin_colegio_detalle", (id_colegio,)) or []
    return resultado[0] if resultado else None


# CRUD DE COLEGIO

def sp_admin_colegio_insertar( nombre: str, dane: str, email: str, telefono: str, direccion: str, id_barrio: int) -> int | None:
    """Inserta un nuevo colegio. Retorna el ID generado o None si falla"""
    resultado = db.call_procedure(
        "sp_admin_colegio_insertar",
        (nombre, dane, email, telefono, direccion, id_barrio),
        out_params=1,   # p_nuevo_id es parámetro OUT
        commit=True,
    ) or []
    return resultado[0].get("p_nuevo_id") if resultado else None


def sp_admin_colegio_actualizar(id_colegio: int, nombre: str, dane: str, email: str, telefono: str, direccion: str, id_barrio: int) -> None:
    """Actualiza los datos institucionales de un colegio"""
    db.call_procedure(
        "sp_admin_colegio_actualizar",
        (id_colegio, nombre, dane, email, telefono, direccion, id_barrio),
        commit=True,
    )


def sp_admin_colegio_estado_cambiar(id_colegio: int) -> int | None:
    """Alterna Estado_Colegio entre 1 y 0. Retorna el nuevo estado (1 = activo, 0 = inactivo)"""
    resultado = db.call_procedure(
        "sp_admin_colegio_estado_cambiar", (id_colegio,), commit=True
    ) or []
    return resultado[0].get("Nuevo_Estado") if resultado else None


# GESTIÓN DE JORNADAS

def sp_admin_colegio_jornadas_activas(id_colegio: int) -> list[dict]:
    """Jornadas activas del colegio con conteo de grados configurados"""
    return db.call_procedure(
        "sp_admin_colegio_jornadas_activas", (id_colegio,)
    ) or []


def sp_admin_colegio_jornada_agregar(id_colegio: int, id_jornada: int) -> None:
    """Activa una jornada para el colegio creando/reactivando cupos"""
    db.call_procedure(
        "sp_admin_colegio_jornada_agregar", (id_colegio, id_jornada), commit=True
    )


def sp_admin_colegio_jornada_quitar(id_colegio: int, id_jornada: int) -> None:
    """Desactiva todos los cupos de la jornada para el colegio"""
    db.call_procedure(
        "sp_admin_colegio_jornada_quitar", (id_colegio, id_jornada), commit=True
    )


# GESTIÓN DE CUPOS

def sp_admin_colegio_cupos_obtener(id_colegio: int) -> list[dict]:
    """Matriz de cupos (grado jornada activa) para la tabla de configuración"""
    return db.call_procedure(
        "sp_admin_colegio_cupos_obtener", (id_colegio,)
    ) or []


def sp_admin_colegio_cupo_guardar(id_colegio: int,id_grado: int,id_jornada: int, cupos_disponibles: int,) -> None:
    """Upsert de una celda individual de la tabla de cupos"""
    db.call_procedure(
        "sp_admin_colegio_cupo_guardar",
        (id_colegio, id_grado, id_jornada, cupos_disponibles), commit=True
    )



# ====================================================================================================================================================
#                                           PAGINA SETTINGS.HTML
# ====================================================================================================================================================

# TIPO AFECTACIÓN

def sp_admin_prioridad_afectaciones_listar() -> list[dict]:
    """Lista todos los tipos de afectación ordenados por nivel de prioridad"""
    return db.call_procedure("sp_admin_prioridad_afectaciones_listar", ()) or []


def sp_admin_prioridad_afectacion_insertar(nombre: str, descripcion: str, nivel: int) -> int | None:
    """Inserta un nuevo tipo de afectación. Retorna el ID generado o None si falla"""
    resultado = db.call_procedure(
        "sp_admin_prioridad_afectacion_insertar",
        (nombre, descripcion, nivel),
        out_params=1,
        commit=True,
    ) or []
    return resultado[0].get("p_nuevo_id") if resultado else None


def sp_admin_prioridad_afectacion_actualizar(id_afectacion: int, nombre: str, descripcion: str, nivel: int) -> None:
    """Actualiza los datos de un tipo de afectación existente"""
    db.call_procedure(
        "sp_admin_prioridad_afectacion_actualizar",
        (id_afectacion, nombre, descripcion, nivel),
        commit=True,
    )


def sp_admin_prioridad_afectacion_estado_cambiar(id_afectacion: int) -> int | None:
    """Alterna Estado_Afectacion entre 1 y 0. Retorna el nuevo estado"""
    resultado = db.call_procedure(
        "sp_admin_prioridad_afectacion_estado_cambiar",
        (id_afectacion,),
        commit=True,
    ) or []
    return resultado[0].get("Nuevo_Estado") if resultado else None


# GRUPO PREFERENCIAL

def sp_admin_prioridad_grupos_listar() -> list[dict]:
    """Lista todos los grupos preferenciales ordenados por nivel de prioridad"""
    return db.call_procedure("sp_admin_prioridad_grupos_listar", ()) or []


def sp_admin_prioridad_grupo_insertar(nombre: str, descripcion: str, nivel: int) -> int | None:
    """Inserta un nuevo grupo preferencial. Retorna el ID generado o None si falla"""
    resultado = db.call_procedure(
        "sp_admin_prioridad_grupo_insertar",
        (nombre, descripcion, nivel),
        out_params=1,
        commit=True,
    ) or []
    return resultado[0].get("p_nuevo_id") if resultado else None


def sp_admin_prioridad_grupo_actualizar(id_grupo: int, nombre: str, descripcion: str, nivel: int) -> None:
    """Actualiza los datos de un grupo preferencial existente"""
    db.call_procedure(
        "sp_admin_prioridad_grupo_actualizar",
        (id_grupo, nombre, descripcion, nivel),
        commit=True,
    )


def sp_admin_prioridad_grupo_estado_cambiar(id_grupo: int) -> int | None:
    """Alterna Estado_Grupo_Preferencial entre 1 y 0. Retorna el nuevo estado"""
    resultado = db.call_procedure(
        "sp_admin_prioridad_grupo_estado_cambiar",
        (id_grupo,),
        commit=True,
    ) or []
    return resultado[0].get("Nuevo_Estado") if resultado else None


# ESTRATO

def sp_admin_prioridad_estratos_listar() -> list[dict]:
    """Lista todos los estratos ordenados por nivel de prioridad"""
    return db.call_procedure("sp_admin_prioridad_estratos_listar", ()) or []


def sp_admin_prioridad_estrato_insertar(nombre: str, descripcion: str, nivel: int) -> int | None:
    """Inserta un nuevo estrato. Retorna el ID generado o None si falla"""
    resultado = db.call_procedure(
        "sp_admin_prioridad_estrato_insertar",
        (nombre, descripcion, nivel),
        out_params=1,
        commit=True,
    ) or []
    return resultado[0].get("p_nuevo_id") if resultado else None


def sp_admin_prioridad_estrato_actualizar(id_estrato: int, nombre: str, descripcion: str, nivel: int) -> None:
    """Actualiza los datos de un estrato existente"""
    db.call_procedure(
        "sp_admin_prioridad_estrato_actualizar",
        (id_estrato, nombre, descripcion, nivel),
        commit=True,
    )


def sp_admin_prioridad_estrato_estado_cambiar(id_estrato: int) -> int | None:
    """Alterna Estado_Estrato entre 1 y 0. Retorna el nuevo estado"""
    resultado = db.call_procedure(
        "sp_admin_prioridad_estrato_estado_cambiar",
        (id_estrato,),
        commit=True,
    ) or []
    return resultado[0].get("Nuevo_Estado") if resultado else None