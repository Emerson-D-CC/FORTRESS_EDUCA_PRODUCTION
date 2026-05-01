from app.utils.database_utils import db

# ==============================================================================
#                       PÁGINA DASHBOARD.HTML
# ==============================================================================

def sp_technical_dashboard_metricas(id_usuario: int) -> dict | None:
    """Métricas del dashboard filtradas por el técnico"""
    resultado = db.call_procedure("sp_technical_dashboard_metricas", (id_usuario,))
    # call_procedure retorna lista de filas, se toma la primera (o None)
    if resultado and len(resultado) > 0:
        return resultado[0]
    return None


def sp_technical_cases_listar_asignados(id_usuario: int) -> list[dict]:
    """Últimas 5 solicitudes asignadas al técnico"""
    return db.call_procedure("sp_technical_cases_listar_asignados", (id_usuario,)) or []


def sp_technical_dashboard_chart_actividad(id_usuario: int) -> list[dict]:
    """Actividad de los últimos 7 días para el gráfico, filtrada por técnico"""
    return db.call_procedure("sp_technical_dashboard_chart_actividad", (id_usuario,)) or []



# ==============================================================================
#                       PÁGINA CASES.HTML
# ==============================================================================

def sp_technical_cases_listar(id_tecnico: int) -> list[dict]:
    """Retorna todos los tickets asignados al técnico"""
    return db.call_procedure("sp_technical_cases_listar", (id_tecnico,)) or []


def sp_technical_cases_metricas(id_tecnico: int) -> dict:
    """Métricas del técnico para las tarjetas superiores"""
    resultado = db.call_procedure("sp_technical_cases_metricas", (id_tecnico,))
    return resultado[0] if resultado else {}

def sp_catalogo_estados_ticket() -> list[dict]:
    """Estados del ticket para el SelectField de filtro"""
    return db.call_procedure("sp_catalogo_estados_ticket", ()) or []


def sp_catalogo_grados() -> list[dict]:
    """Grados disponibles para el SelectField de filtro"""
    return db.call_procedure("sp_catalogo_grados", ()) or []


def sp_catalogo_tipo_afectacion() -> list[dict]:
    """Tipos de afectación para el SelectField de filtro"""
    return db.call_procedure("sp_catalogo_tipo_afectacion", ()) or []



# ==============================================================================
#                       PÁGINA HISTORY.HTML
# ==============================================================================

def sp_technical_history_listar_todos(id_tecnico: int) -> list[dict]:
    """Retorna TODOS los registros de auditoría del técnico indicado. Sin filtros"""
    return db.call_procedure(
        "sp_technical_history_listar_todos", (id_tecnico,)
    ) or []

def sp_technical_history_exportar(id_tecnico:  int, tipo_evento: str | None, fecha_desde: str | None, fecha_hasta: str | None) -> list[dict]:
    """Retorna TODOS los registros del técnico sin paginar (para CSV/PDF)"""
    return db.call_procedure(
        "sp_technical_history_exportar",
        (id_tecnico, tipo_evento, fecha_desde, fecha_hasta),
    ) or []



    