from app.utils.database_utils import db


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
    
