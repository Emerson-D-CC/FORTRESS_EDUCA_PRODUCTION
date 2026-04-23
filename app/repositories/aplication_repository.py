from app.utils.database_utils import db

# ====================================================================================================================================================
#                                           PAGINA INDEX.HTML - PANEL PRINCIPAL
# ====================================================================================================================================================

def sp_dashboard_resumen_acudiente(id_usuario: int):
    """Retorna el resumen del panel principal para el acudiente."""
    resultado = db.call_procedure("sp_tbl_dashboard_resumen_acudiente", (id_usuario,))
    return resultado[0] if resultado else None



# ====================================================================================================================================================
#                                           PAGINA TICKET_REQUEST.HTML - SISTEMA DE TICKETS
# ====================================================================================================================================================

# DATOS PARA LISTAS DE OPCIONES

def sp_obtener_tipos_afectacion():
    return db.call_procedure("sp_tbl_tipo_afectacion_consultar", ()) or []

def sp_obtener_jornadas():
    return db.call_procedure("sp_tbl_jornada_consultar", ()) or []

def sp_obtener_tiempos_residencia():
    return db.call_procedure("sp_tbl_tiempo_residencia_consultar", ()) or []


# VERIFICACIONES

def sp_ticket_verificar_activo(id_estudiante, id_usuario):
    """Retorna True si el estudiante ya tiene un ticket abierto."""
    resultado = db.call_procedure(
        "sp_ticket_verificar_activo",
        (id_estudiante, id_usuario)
    )
    if not resultado:
        return False
    return resultado[0].get("total_activos", 0) > 0


# CREACIÓN

def sp_ticket_crear(data):
    """Llama al SP que inserta el ticket y retorna el ID generado"""
    return db.call_procedure(
        "sp_ticket_crear",
        data,
        commit=False
    )

def sp_ticket_obtener_ultimo_numero():
    """Retorna el número secuencial del último ticket creado"""
    resultado = db.call_procedure("sp_ticket_obtener_ultimo_numero", ())
    if not resultado:
        return 0
    return resultado[0].get("ultimo_numero", 0)



# ====================================================================================================================================================
#                                           PAGINA TICKET_STATUS.HTML - SEGUIMIENTO DE TICKETS
# ====================================================================================================================================================

# LISTAS DE TICKETS

def sp_ticket_consultar_por_usuario(id_usuario: int):
    """Retorna todos los tickets activos del acudiente."""
    return db.call_procedure("sp_tbl_ticket_consultar_por_usuario", (id_usuario,)) or []


def sp_ticket_cerrado_consultar_por_usuario(id_usuario: int):
    """Retorna todos los tickets cerrados del acudiente."""
    return db.call_procedure("sp_tbl_ticket_cerrado_consultar_por_usuario", (id_usuario,)) or []



# DATOS PARA LOS DETALLES DEL TICKET

def sp_ticket_consultar_detalle(id_ticket: str, id_usuario: int):
    """Retorna los datos completos de un ticket, verificando que pertenece al usuario."""
    resultado = db.call_procedure("sp_tbl_ticket_consultar_detalle", (id_ticket, id_usuario))
    return resultado[0] if resultado else None


def sp_ticket_comentarios_consultar(id_ticket: str, id_usuario: int):
    """Retorna los comentarios públicos de un ticket."""
    return db.call_procedure("sp_tbl_ticket_comentarios_consultar", (id_ticket, id_usuario)) or []


def sp_ticket_documentos_consultar(id_ticket: str, id_usuario: int):
    """Retorna la lista de documentos de un ticket."""
    return db.call_procedure("sp_tbl_ticket_documentos_consultar", (id_ticket, id_usuario)) or []


def sp_tipo_documento_consultar():
    """Retorna los tipos de documento activos."""
    return db.call_procedure("sp_tbl_tipo_documento_consultar", ()) or []


def sp_documento_ticket_insertar(id_ticket: str, id_tipo_doc: int, archivo: bytes, nombre_original: str):
    """Inserta un nuevo documento asociado a un ticket."""
    db.call_procedure("sp_documento_ticket_insertar", (
        id_ticket,
        id_tipo_doc,
        archivo,
        nombre_original,
    ))

def sp_documento_comentario_insertar(id_ticket, tipo_evento, id_usuario, comentario, es_interno) -> None:
    """Inserta un comentario manual en el ticket al subir un documento"""
    db.call_procedure(
        "sp_ticket_panel_comentario_insertar",
        (id_ticket, tipo_evento, id_usuario, comentario, int(es_interno)),
    )

def sp_documento_ticket_descargar(id_doc: int, id_usuario: int):
    """Retorna el binario y metadata de un documento, verificando pertenencia."""
    resultado = db.call_procedure("sp_tbl_documento_ticket_descargar", (id_doc, id_usuario))
    return resultado[0] if resultado else None



# ====================================================================================================================================================
#                                           PAGINA PROFILE.HTML - MI USUARIO
# ====================================================================================================================================================

# DATOS PARA LISTAS DE OPCIONES 

def sp_obtener_generos():
    return db.call_procedure("sp_tbl_genero_consultar", ()) or []

def sp_obtener_grupos_preferenciales():
    return db.call_procedure("sp_tbl_grupo_preferencial_consultar", ()) or []

def sp_obtener_grados():
    return db.call_procedure("sp_tbl_grado_consultar", ()) or []

def sp_obtener_colegios():
    return db.call_procedure("sp_tbl_colegio_consultar", ()) or []

def sp_obtener_tipos_identificacion():
    return db.call_procedure("sp_tbl_tipo_identificacion_consultar_est", ()) or []

def sp_obtener_estratos():
    return db.call_procedure("sp_tbl_estrato_consultar", ()) or []

def sp_obtener_localidades():
    return db.call_procedure("sp_tbl_localidad_consultar", ()) or []

def sp_obtener_barrios():
    return db.call_procedure("sp_tbl_barrio_consultar", ()) or []

def sp_obtener_parentesco_est():
    return db.call_procedure("sp_tbl_parentesco_consultar_est", ()) or []

def sp_obtener_parentesco_acu():
    return db.call_procedure("sp_tbl_parentesco_consultar_acu", ()) or []


#  PERFIL DEL USUARIO (ACUDIENTE)

def sp_obtener_perfil_acudiente(id_usuario):
    resultado = db.call_procedure("sp_perfil_acudiente_consultar", (id_usuario,))
    return resultado[0] if resultado else None

def sp_actualizar_datos_adicionales(data):
    return db.call_procedure("sp_tbl_datos_adicionales_actualizar", data, commit=False)


# PERFIL DE ESTUDIANTES

def sp_obtener_estudiantes_por_acudiente(id_usuario):
    """Retorna la lista de todos los estudiantes activos del acudiente."""
    return db.call_procedure(
        "sp_perfil_estudiantes_por_acudiente", (id_usuario,)
    ) or []

def sp_obtener_estudiante_por_id(id_estudiante, id_usuario):
    """Retorna los datos de un estudiante específico."""
    resultado = db.call_procedure(
        "sp_perfil_estudiante_por_id", (id_estudiante, id_usuario)
    )
    return resultado[0] if resultado else None

def sp_verificar_estudiante_acudiente(id_acudiente):
    """Retorna {'total_estudiantes': N} — si N > 0 el acudiente ya tiene al menos uno."""
    resultado = db.call_procedure(
        "sp_tbl_estudiante_verificar_por_acudiente", (id_acudiente,)
    )
    return resultado[0] if resultado else {"total_estudiantes": 0}

def sp_obtener_perfil_estudiante(id_usuario):
    resultado = db.call_procedure("sp_perfil_estudiante_consultar", (id_usuario,))
    return resultado[0] if resultado else None


# ACTUALIZAR DATOS 

def sp_actualizar_persona(data):
    return db.call_procedure("sp_tbl_persona_actualizar", data, commit=False)

def sp_actualizar_estudiante(data):
    return db.call_procedure("sp_tbl_estudiante_actualizar", data, commit=False)


# REGISTRAR ESTUDIANTE

def sp_registrar_estudiante(data):
    return db.call_procedure("sp_registrar_estudiante_completo", data, commit=False)

def sp_estudiante_existe(num_doc_estudiante, id_usuario):
    resultado = db.call_procedure(
        "sp_tbl_estudiante_verificar_existente",
        (num_doc_estudiante, id_usuario)
    )
    if not resultado:
        return False
    return resultado[0].get("existe", 0) > 0



# ====================================================================================================================================================
#                                           PAGINA SECURITY.HTML - SEGURIDAD    
# ====================================================================================================================================================
    
# CONTRASEÑA
 
def sp_cambiar_contraseña_perfil(id_usuario, nuevo_hash, ip, user_agent):
    """Valida la contraseña actual y actualiza a la nueva"""
    return db.call_procedure(
        "sp_tbl_usuario_cambiar_contraseña_perfil",
        (id_usuario, nuevo_hash, ip, user_agent),
        commit=False
    )

def sp_validar_data_user(username):
        return db.call_procedure(
        "sp_validar_data_user",
        (username,)
    )
        

def sp_validar_data_autenticacion(username):
    return db.call_procedure(
        "sp_obtener_datos_autenticacion",
        (username,)
    )
    
def sp_exito_login(username):
        return db.call_procedure(
        "sp_registrar_exito_login",
        (username,)
    )

        
# MFA

def sp_guardar_mfa_secret_temp(id_usuario, secret):
    """Guarda el secret temporal mientras el usuario no ha confirmado el código"""
    return db.call_procedure(
        "sp_tbl_usuario_guardar_mfa_secret_temp",
        (id_usuario, secret),
        commit=False
    )

def sp_activar_mfa(id_usuario):
    """Mueve el secret temporal al campo definitivo y activa 2FA"""
    return db.call_procedure(
        "sp_tbl_usuario_activar_mfa",
        (id_usuario,),
        commit=False
    )

def sp_desactivar_mfa(id_usuario):
    """Borra el secret y desactiva 2FA"""
    return db.call_procedure(
        "sp_tbl_usuario_desactivar_mfa",
        (id_usuario,),
        commit=False
    )

def sp_obtener_mfa_secret(id_usuario):
    """Devuelve el estado y secrets MFA del usuario"""
    return db.call_procedure(
        "sp_tbl_usuario_obtener_mfa_secret",
        (id_usuario,),
        commit=False
    )

# SISTEMA PARA VALIDAR SESIONES ACTIVAS

def sp_registrar_sesion(id_usuario, jti, dispositivo, ip):
    """Registra o actualiza una sesión activa"""
    return db.call_procedure(
        "sp_tbl_sesion_activa_registrar_sesion",
        (id_usuario, jti, dispositivo, ip),
        commit=False
    )

def sp_listar_sesiones(id_usuario):
    """Lista las sesiones activas de un usuario"""
    return db.call_procedure(
        "sp_tbl_sesion_activa_listar_sesiones",
        (id_usuario,),
        commit=False
    )

def sp_cerrar_sesion(jti):
    """Marca como inactiva una sesión por su JTI"""
    return db.call_procedure(
        "sp_tbl_sesion_activa_cerrar_sesion",
        (jti,),
        commit=False
    )

def sp_cerrar_todas_sesiones(id_usuario, jti_actual):
    """Cierra todas las sesiones excepto la actual"""
    return db.call_procedure(
        "sp_tbl_sesion_activa_cerrar_todas_sesiones",
        (id_usuario, jti_actual),
        commit=False
    )

def sp_verificar_jti(jti):
    """Verifica si un JTI está activo (para token blacklist)"""
    return db.call_procedure(
        "sp_tbl_sesion_activa_verificar_jti",
        (jti,),
        commit=False
    )
    
    

    
# ====================================================================================================================================================
#                                           PAGINA SETTINGS.HTML - AJUSTES
# ====================================================================================================================================================

# SISTEMA DE CONFIGURACIONES VARIAS

def sp_configuracion_obtener_notificaciones(id_usuario):
    """Obtiene el estado actual de las preferencias de notificación del usuario"""
    return db.call_procedure(
        "sp_configuracion_obtener_notificaciones",
        (id_usuario,),
        commit=False
    )
 
def sp_configuracion_actualizar_notif_email(id_usuario, activo):
    """Actualiza el campo Notificaciones_Email del usuario"""
    return db.call_procedure(
        "sp_configuracion_actualizar_notif_email",
        (id_usuario, activo),
        commit=True
    )
 
def sp_configuracion_actualizar_notif_navegador(id_usuario, activo):
    """Actualiza el campo Notificaciones_Navegador del usuario"""
    return db.call_procedure(
        "sp_configuracion_actualizar_notif_navegador",
        (id_usuario, activo),
        commit=True
    )

# SISTEMA PARA ELIMINAR AL USUARIO ACTUAL

def sp_validar_login(username, password):
    return db.call_procedure(
        "sp_tbl_usuario_validar_login",
        (username, password)
    )

def sp_eliminar_cuenta_completa(id_usuario, ip, user_agent):
    """Elimina lógicamente un usuario y el estudiante vinculado"""
    return db.call_procedure(
        "sp_eliminar_cuenta_completa",
        (id_usuario, ip, user_agent),
        commit=True
    )
