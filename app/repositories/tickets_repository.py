from app.utils.database_utils import db

# ====================================================================================================================================================
#                                           PAGINA TICKET_PANEL.HTML
# ====================================================================================================================================================

# DETALLE DEL TICKET

def sp_ticket_panel_consultar_detalle(id_ticket) -> dict | None:
    """Retorna todos los datos del ticket para el panel del técnico"""
    resultado = db.call_procedure("sp_ticket_panel_consultar_detalle", (id_ticket,))
    return resultado[0] if resultado else None


# COMENTARIOS

def sp_ticket_panel_comentarios_consultar(id_ticket) -> list[dict]:
    """ Retorna TODOS los comentarios del ticket (públicos e internos)"""
    return db.call_procedure("sp_ticket_panel_comentarios_consultar", (id_ticket,)) or []


def sp_ticket_panel_comentario_insertar(id_ticket, tipo_evento, id_usuario, comentario, es_interno) -> None:
    """Inserta un comentario en el ticket"""
    db.call_procedure(
        "sp_ticket_panel_comentario_insertar",
        (id_ticket, tipo_evento, id_usuario, comentario, int(es_interno)),
    )


# ASIGNACIÓN DE CUPO
def sp_ticket_validar_cupo(id_ticket: str, id_colegio: int, id_jornada: int) -> dict | None:
    """Verifica si existe cupo disponible para la combinación grado (del estudiante) + colegio + jornada"""
    resultado = db.call_procedure(
        "sp_ticket_validar_cupo", (id_ticket, id_colegio, id_jornada)
    )
    return resultado[0] if resultado else None


def sp_ticket_confirmar_asignacion(id_ticket: str, id_cupo: int, id_tecnico: int) -> None:
    """Asigna el cupo al ticket, cambia estado a 4 e inserta el comentario público automático"""
    db.call_procedure(
        "sp_ticket_confirmar_asignacion", (id_ticket, id_cupo, id_tecnico)
    )

    # GESTIÓN DE DTICKET ABANDONADOS
def sp_ticket_obtener_abandonados() -> list[dict]:
    """Retorna tickets en estado 4 sin respuesta del usuario en +3 días"""
    return db.call_procedure("sp_ticket_obtener_abandonados", ()) or []


def sp_ticket_rechazar_abandonado(id_ticket: str, id_responsable: int) -> None:
    """Cierra el ticket como Rechazado y registra el comentario automático"""
    db.call_procedure(
        "sp_ticket_rechazar_abandonado", (id_ticket, id_responsable)
    )


# CAMBIO DE ESTADO

def sp_ticket_panel_estado_actualizar(id_ticket, id_estado_nuevo, fecha_cierre, resolucion, id_tecnico,) -> None:
    """Actualiza el estado del ticket y registra automáticamente un comentario interno de auditoría con el cambio"""
    db.call_procedure(
        "sp_ticket_panel_estado_actualizar",
        (id_ticket, id_estado_nuevo, fecha_cierre, resolucion, id_tecnico),
    )


# DOCUMENTOS

def sp_ticket_panel_documentos_consultar(id_ticket) -> list[dict]:
    """Retorna la lista de documentos del ticket (sin restricción de usuario)"""
    return db.call_procedure("sp_ticket_panel_documentos_consultar", (id_ticket,)) or []


def sp_ticket_panel_documento_descargar(id_doc) -> dict | None:
    """Retorna el binario y metadata del documento para descarga"""
    resultado = db.call_procedure("sp_ticket_panel_documento_descargar", (id_doc,))
    return resultado[0] if resultado else None


def sp_ticket_panel_documento_insertar(id_ticket, id_tipo_doc, archivo, nombre_original) -> None:
    """Inserta un documento subido por el técnico al ticket"""
    db.call_procedure(
        "sp_documento_ticket_insertar",
        (id_ticket, id_tipo_doc, archivo, nombre_original),
    )


# DATOS DEL ACUDIENTE Y ESTUDIANTE (solo lectura)

def sp_ticket_panel_acudiente_consultar(id_ticket) -> dict | None:
    """Retorna los datos del acudiente creador del ticket"""
    resultado = db.call_procedure("sp_ticket_panel_acudiente_consultar", (id_ticket,))
    return resultado[0] if resultado else None


def sp_ticket_panel_estudiante_consultar(id_ticket) -> dict | None:
    """Retorna los datos del estudiante asociado al ticket"""
    resultado = db.call_procedure("sp_ticket_panel_estudiante_consultar", (id_ticket,))
    return resultado[0] if resultado else None


# CATÁLOGOS PARA SELECTFIELDS

def sp_catalogo_estados_ticket() -> list[dict]:
    """Retorna todos los estados del ticket para poblar el SelectField"""
    return db.call_procedure("sp_catalogo_estados_ticket", ()) or []


def sp_catalogo_jornadas() -> list[dict]:
    """Retorna todas las jornadas disponibles"""
    return db.call_procedure("sp_catalogo_jornadas", ()) or []


def sp_tipo_documento_consultar() -> list[dict]:
    """Retorna los tipos de documento activos (reutilizado del módulo acudiente)"""
    return db.call_procedure("sp_tbl_tipo_documento_consultar", ()) or []

    # ASIGNACIÓN DE CUPO

def sp_catalogo_barrios_con_colegios() -> list[dict]:
    """Barrios que tienen al menos un colegio activo (usa VW_BARRIOS_CON_COLEGIOS)"""
    return db.call_procedure("sp_catalogo_barrios_con_colegios", ()) or []

def sp_catalogo_colegios_por_barrio(id_barrio: int) -> list[dict]:
    """Colegios activos dentro del barrio indicado"""
    return db.call_procedure("sp_catalogo_colegios_por_barrio", (id_barrio,)) or []


    # 
    
def sp_ticket_cupo_asignado_detalle(id_ticket: str) -> dict | None:
    """Retorna toda la info del cupo actualmente asignado al ticket"""
    resultado = db.call_procedure("sp_ticket_cupo_asignado_detalle", (id_ticket,))
    return resultado[0] if resultado else None


def sp_ticket_usuario_confirmar_cupo(id_ticket: str, id_tecnico: int) -> None:
    """Confirma el cupo: descuenta disponible+reservado, cierra ticket como Solucionado"""
    db.call_procedure("sp_ticket_usuario_confirmar_cupo", (id_ticket, id_tecnico))


def sp_ticket_usuario_cancelar_cupo(id_ticket: str, id_tecnico: int) -> None:
    """Cancela el cupo: libera reserva, quita FK_ID_Cupo_Asignado, vuelve a estado 5"""
    db.call_procedure("sp_ticket_usuario_cancelar_cupo", (id_ticket, id_tecnico))
